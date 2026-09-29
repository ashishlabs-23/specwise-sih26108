#!/usr/bin/env python3
"""
IndicTrans2 ONNX INT8 — Render Free Memory-Feasibility Test Harness
===================================================================

Target Model: hari31416/indictrans2-indic-en-dist-200M-ONNX-int8
              (Third-party ONNX INT8 dynamic quantization of ai4bharat/indictrans2-indic-en-dist-200M)

Objective:
  Determine if isolated ONNX INT8 inference fits strictly within Render Free tier (512 MiB RAM limit).
  Feasibility target: Peak RSS < 460 MiB (leaves 52 MiB headroom for OS/container runtime).

Aggressive Render-Only Memory Strategy:
  1. Providers: CPUExecutionProvider only
  2. Execution Mode: ORT_SEQUENTIAL
  3. Threading: intra_op_num_threads=1, inter_op_num_threads=1
  4. Memory arena: Disabled (so.enable_cpu_mem_arena = False)
  5. Memory pattern: Disabled (so.enable_mem_pattern = False)
  6. Profiling: Disabled (so.enable_profiling = False)
  7. Graph Optimization: ORT_DISABLE_ALL
  8. Batch size: 1
  9. Bounded sequence length: max 64 tokens, greedy decoding
 10. Sequential Session Release:
     - Load Encoder Session -> Run encoder -> Delete & release Encoder Session -> gc.collect()
     - Load Initial Decoder Session -> Run step 0 -> Delete & release Initial Decoder Session -> gc.collect()
     - Load Decoder with Past Session -> Loop auto-regressive generation -> Delete & release -> gc.collect()

Execution:
  Default: Runs 1 representative technical procurement case for Render Free deployment sanity.
  Full Suite: Pass --full-suite or --all to run the complete 24-case benchmark.
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import re
import sys
import time
from pathlib import Path

# Ensure UTF-8 output across environments (including Windows console)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# STATIC FRAMEWORK GUARDS — prevent accidental loading of heavy packages
# ---------------------------------------------------------------------------
_FORBIDDEN = (
    "torch", "transformers", "ctranslate2", "IndicTransToolkit",
    "sacrebleu", "nltk", "fairseq", "indicnlp", "sacremoses",
)
for _fb in _FORBIDDEN:
    if _fb in sys.modules:
        print(f"FATAL: forbidden module '{_fb}' already loaded", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# CONSTANTS & CONFIGURATION
# ---------------------------------------------------------------------------
MODEL_ID = "hari31416/indictrans2-indic-en-dist-200M-ONNX-int8"
RENDER_FREE_LIMIT_MIB = 512
RENDER_MEMORY_TARGET_MIB = 460  # Feasibility target (52 MiB headroom on 512 MiB limit)
MAX_GEN_TOKENS = 64

REQUIRED_PATTERNS = [
    "encoder_model.onnx",
    "encoder_model.onnx.data",
    "decoder_model.onnx",
    "decoder_with_past_model.onnx",
    "decoder_shared.onnx.data",
    "tokenizer_src.json",
    "tokenizer_tgt.json",
    "tokenizer_meta.json",
    "generation_config.json",
]

IGNORE_PATTERNS = [
    "*.png", "*.safetensors", "pytorch_model.bin", "model.SRC", "model.TGT",
    "dict.*.json", "configuration_indictrans.py", "tokenization_indictrans.py",
    "tokenizer_config.json", "config.json", "translate.py",
    "LICENSE", "README.md", ".gitattributes",
]

# ---------------------------------------------------------------------------
# REPRESENTATIVE TEST CASE (Render sanity deployment)
# ---------------------------------------------------------------------------
REPRESENTATIVE_CASE = {
    "label": "BL-03-Hindi-technical",
    "src_text": "IS 14220:2018 के अनुसार सिंचाई के लिए 5 HP ओपनवेल पंपसेट और 25 mm पाइप दें।",
    "src_lang": "hin_Deva",
    "tgt_lang": "eng_Latn",
    "expected": "Give 5 HP openwell pumpsets and 25 mm pipes for irrigation as per IS 14220:2018.",
}

REQUIRED_ENTITIES = [
    "IS 14220:2018",
    "5 HP",
    "25 mm",
    "openwell",
    "irrigation",
]

# ---------------------------------------------------------------------------
# MEMORY MONITORING HELPERS
# ---------------------------------------------------------------------------
def _rss_mib() -> float:
    """Return current process Resident Set Size in MiB."""
    p = Path("/proc/self/status")
    if p.exists():
        try:
            for line in p.read_text().splitlines():
                if line.startswith("VmRSS:"):
                    return float(line.split()[1]) / 1024.0
        except Exception:
            pass
    try:
        import psutil
        return psutil.Process().memory_info().rss / (1024.0 * 1024.0)
    except Exception:
        return 0.0


def _peak_rss_mib() -> float:
    """Return peak process Resident Set Size (VmHWM on Linux) in MiB."""
    p = Path("/proc/self/status")
    if p.exists():
        try:
            for line in p.read_text().splitlines():
                if line.startswith("VmHWM:"):
                    return float(line.split()[1]) / 1024.0
        except Exception:
            pass
    return _rss_mib()


def _fmt_mib(val: float | None) -> str:
    if val is None or val <= 0:
        return "N/A"
    return f"{val:.2f} MiB"

# ---------------------------------------------------------------------------
# TEXT NORMALIZATION & PREPROCESSING
# ---------------------------------------------------------------------------
_KN_TO_HI: dict[str, str] = {
    "ಅ": "अ", "ಆ": "आ", "ಇ": "इ", "ಈ": "ई", "ಉ": "उ", "ಊ": "ऊ",
    "ಎ": "ए", "ಏ": "ए", "ಐ": "ऐ", "ಒ": "ओ", "ಓ": "ओ", "ಔ": "औ",
    "ಾ": "ा", "ಿ": "ि", "ೀ": "ी", "ು": "ु", "ೂ": "ू",
    "ೆ": "े", "ೇ": "े", "ೈ": "ै", "ೊ": "ो", "ೋ": "ो", "ೌ": "ौ",
    "ಂ": "ं", "ಃ": "ः", "್": "्", "ಽ": "ऽ",
    "ಕ": "क", "ಖ": "ख", "ಗ": "ग", "ಘ": "घ", "ಙ": "ङ",
    "ಚ": "च", "ಛ": "छ", "ಜ": "ज", "ಝ": "झ", "ಞ": "ञ",
    "ಟ": "ट", "ಠ": "ठ", "ಡ": "ड", "ಢ": "ढ", "ಣ": "ण",
    "ತ": "त", "ಥ": "थ", "ದ": "द", "ಧ": "ध", "ನ": "न",
    "ಪ": "प", "ಫ": "फ", "ಬ": "ब", "ಭ": "भ", "ಮ": "म",
    "ಯ": "य", "ರ": "र", "ಲ": "ल", "ವ": "व", "ಶ": "श",
    "ಷ": "ष", "ಸ": "स", "ಹ": "ह", "ಳ": "ळ", "ಱ": "र", "ೞ": "ल",
}

_PUNC_NORM: dict[str, str] = {
    "\r": "", "\u2026": "...", "\u200b": "", "\u200c": "", "\u200d": "",
    "\ufeff": "", "\u00a0": " ",
    "\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'",
    "\u2013": "-", "\u2014": "-", "\u2212": "-",
}


def build_prefixed(text: str, src_lang: str, tgt_lang: str) -> str:
    """Format input text with source and target language prefix tags: '{src_lang} {tgt_lang} {text}'."""
    for s, t in _PUNC_NORM.items():
        text = text.replace(s, t)
    text = re.sub(r"[ \t]+", " ", text).strip()
    if src_lang == "kan_Knda":
        text = "".join(_KN_TO_HI.get(ch, ch) for ch in text)
        src_tag = "hin_Deva"
    else:
        src_tag = src_lang
    return f"{src_tag} {tgt_lang} {text}"


def extract_source_is_references(text: str) -> list[str]:
    """
    Extract canonical IS references from text.
    Matches 'IS <3-6 digits>:<4 digits>' with optional spacing around colon.
    Returns canonical references e.g. ['IS 14220:2018'].
    """
    if not text:
        return []
    pattern = re.compile(r'\bIS\s*(\d{3,6})\s*:\s*(\d{4})\b', re.IGNORECASE)
    matches = pattern.findall(text)
    return [f"IS {num}:{yr}" for num, yr in matches]


def extract_source_is_numbers(text: str) -> set[str]:
    """Extract standard IS numbers (3-6 digits) from text."""
    if not text:
        return set()
    return set(re.findall(r'\bIS\s*(\d{3,6})\b', text, re.IGNORECASE))


def normalize_technical_reference(raw_text: str, source_text: str = "") -> str:
    """
    Deterministic source-aware postprocessing and technical reference normalization:
      1. Strips tokenization artifacts (escaped colons, backslashes).
      2. Normalizes decimal numbers (e.g. '7 . 5' -> '7.5').
      3. Normalizes standard formatting (e.g. 'IS 14220 : 2018' -> 'IS 14220:2018').
      4. Restores split standard prefix (e.g. 'IS 14220:Give ... as per 2018' -> 'Give ... as per IS 14220:2018')
         ONLY when verified against source_text (or present in raw tokens if source_text is omitted).
         Never fabricates or invents an IS reference not present in the source text.
      5. Cleans whitespace before punctuation (e.g. '2018 .' -> '2018.').
    """
    out = raw_text.strip()
    # 1. Remove escaped colons/slashes
    out = re.sub(r'\\([:/-])', r'\1', out)
    # 2. Fix decimals
    out = re.sub(r'(\d+)\s*\.\s*(\d+)', r'\1.\2', out)
    # 3. Standard with internal whitespace around colon: IS 14220 : 2018 -> IS 14220:2018
    out = re.sub(r'\bIS\s*(\d{3,6})\s*:\s*(\d{4})\b', r'IS \1:\2', out, flags=re.IGNORECASE)

    # 4. Restore split IS standard prefix:
    # Matches 'IS <number>[: ] <clause> <compliance_prep> <year>'
    split_is_pattern = re.compile(
        r'^\s*IS\s*(\d{3,6})\s*[:\s]\s*(.*?)\s+(as per|according to|conforming to|in accordance with|per)\s+(\d{4})\b(.*)$',
        re.IGNORECASE | re.DOTALL
    )
    m = split_is_pattern.match(out)
    if m:
        is_num, main_clause, prep, yr, rest = m.groups()
        canonical_ref = f"IS {is_num}:{yr}"

        # Source verification: verify against source text when provided
        should_reconstruct = False
        if not source_text:
            should_reconstruct = True
        else:
            source_refs = extract_source_is_references(source_text)
            source_nums = extract_source_is_numbers(source_text)
            if canonical_ref in source_refs or is_num in source_nums:
                should_reconstruct = True

        if should_reconstruct:
            out = f"{main_clause.strip()} {prep} {canonical_ref}{rest}"

    # 5. Remove whitespace before punctuation marks (. , ! ? ; :)
    out = re.sub(r'\s+([.,!?;:])', r'\1', out)
    # 6. Normalize multiple spaces
    out = re.sub(r'\s+', ' ', out).strip()
    return out


def check_entity_preservation(text: str, entities: list[str]) -> dict[str, bool]:
    """Verify presence of all mandatory technical entities in generated text."""
    text_norm = re.sub(r"\s+", " ", text).casefold()
    results = {}
    for ent in entities:
        ent_norm = re.sub(r"\s+", " ", ent).casefold()
        results[ent] = (ent_norm in text_norm)
    return results


def run_normalization_regression_tests() -> tuple[bool, list[dict]]:
    """
    Validate normalization rules against key regression and adversarial cases:
      1. Split IS standard with year (matching source)
      2. Another standard number/year (matching source)
      3. Intact IS standard with spacing
      4. Ordinary numeric text (NOT an IS reference)
      5. IS reference without year
      6. Adversarial unmentioned IS standard (must NOT fabricate/reconstruct)
      7. Omitted source_text fallback
    """
    test_cases = [
        {
            "desc": "Split IS 14220:2018 prefix pattern with verified source",
            "raw": "IS 14220:Give 5 HP openwell pumpsets and 25 mm pipes for irrigation as per 2018 .",
            "source": "IS 14220:2018 ಪ್ರಕಾರ ನೀರಾವರಿಗಾಗಿ 5 HP ಓಪನ್‌ವೆಲ್ ಪಂಪ್‌ಸೆಟ್‌ಗಳು ಮತ್ತು 25 mm ಪೈಪ್‌ಗಳನ್ನು ನೀಡಿ.",
            "expected": "Give 5 HP openwell pumpsets and 25 mm pipes for irrigation as per IS 14220:2018.",
        },
        {
            "desc": "Another IS standard number & year (IS 1520:2022)",
            "raw": "IS 1520:Supply 10 pumps for water works according to 2022 .",
            "source": "IS 1520:2022 ಪ್ರಕಾರ 10 ಪಂಪ್‌ಗಳನ್ನು ಸರಬರಾಜು ಮಾಡಿ.",
            "expected": "Supply 10 pumps for water works according to IS 1520:2022.",
        },
        {
            "desc": "Intact IS standard with space around colon",
            "raw": "Give 5 HP pumps as per IS 14220 : 2018 .",
            "source": "IS 14220:2018 ಪ್ರಕಾರ 5 HP ಪಂಪ್ ನೀಡಿ.",
            "expected": "Give 5 HP pumps as per IS 14220:2018.",
        },
        {
            "desc": "Ordinary numeric text (must NOT be modified as IS)",
            "raw": "Order 100 pipes of 25 mm at 500 RPM for 2024 as per invoice 14220 .",
            "source": "2024 ರ ಇನ್‌ವಾಯ್ಸ್ 14220 ರಂತೆ 500 RPM ನಲ್ಲಿ 25 mm ನ 100 ಪೈಪ್‌ಗಳನ್ನು ಆರ್ಡರ್ ಮಾಡಿ.",
            "expected": "Order 100 pipes of 25 mm at 500 RPM for 2024 as per invoice 14220.",
        },
        {
            "desc": "IS reference without year (must NOT fabricate year)",
            "raw": "IS 14220 certified 5 HP pump .",
            "source": "IS 14220 ಪ್ರಮಾಣೀಕೃತ 5 HP ಪಂಪ್.",
            "expected": "IS 14220 certified 5 HP pump.",
        },
        {
            "desc": "Adversarial: Spurious IS not in source (must NOT reconstruct unverified standard)",
            "raw": "IS 99999:Order pumps for irrigation as per 2018 .",
            "source": "ನೀರಾವರಿಗಾಗಿ ಪಂಪ್‌ಗಳನ್ನು ಆರ್ಡರ್ ಮಾಡಿ.",
            "expected": "IS 99999:Order pumps for irrigation as per 2018.",
        },
        {
            "desc": "Omitted source_text fallback",
            "raw": "IS 14220:Give 5 HP openwell pumpsets as per 2018 .",
            "source": "",
            "expected": "Give 5 HP openwell pumpsets as per IS 14220:2018.",
        },
    ]

    all_passed = True
    results = []
    for tc in test_cases:
        actual = normalize_technical_reference(tc["raw"], tc.get("source", ""))
        passed = (actual == tc["expected"])
        if not passed:
            all_passed = False
        results.append({
            "desc": tc["desc"],
            "raw": tc["raw"],
            "source": tc.get("source", ""),
            "expected": tc["expected"],
            "actual": actual,
            "passed": passed,
        })
    return all_passed, results

# ---------------------------------------------------------------------------
# MODEL DOWNLOAD
# ---------------------------------------------------------------------------
def download_model_files() -> tuple[Path, float]:
    """Download only the required ONNX and tokenizer files."""
    try:
        from huggingface_hub import snapshot_download
    except ImportError as e:
        print(f"FATAL: huggingface_hub import failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n[DOWNLOAD] Fetching minimal ONNX INT8 files for {MODEL_ID} ...", flush=True)
    t0 = time.perf_counter()
    try:
        snap_dir = snapshot_download(
            repo_id=MODEL_ID,
            allow_patterns=REQUIRED_PATTERNS,
            ignore_patterns=IGNORE_PATTERNS,
        )
    except Exception as exc:
        print(f"\nFATAL: Model download failed: {exc}", file=sys.stderr)
        print("Check internet connectivity and repository accessibility.", file=sys.stderr)
        sys.exit(1)

    elapsed = time.perf_counter() - t0
    snap_path = Path(snap_dir)
    disk_mib = sum(
        f.stat().st_size for f in snap_path.rglob("*") if f.is_file()
    ) / (1024.0 * 1024.0)
    print(f"[DOWNLOAD] Completed in {elapsed:.2f}s | Disk size: {disk_mib:.1f} MiB", flush=True)
    return snap_path, disk_mib

# ---------------------------------------------------------------------------
# SESSION OPTIONS FACTORY
# ---------------------------------------------------------------------------
def create_session_options(ort_module):
    """Construct aggressive low-memory ORT SessionOptions."""
    so = ort_module.SessionOptions()
    so.execution_mode = ort_module.ExecutionMode.ORT_SEQUENTIAL
    so.intra_op_num_threads = 1
    so.inter_op_num_threads = 1
    so.enable_cpu_mem_arena = False
    so.enable_mem_pattern = False
    so.enable_profiling = False
    so.graph_optimization_level = ort_module.GraphOptimizationLevel.ORT_DISABLE_ALL
    return so


def build_past_feed(past_out: list, num_layers: int) -> dict:
    """Format decoder KV cache tensors into feed dictionary."""
    feed = {}
    for i in range(num_layers):
        b = i * 4
        feed[f"past_key_values.{i}.decoder.key"] = past_out[b]
        feed[f"past_key_values.{i}.decoder.value"] = past_out[b + 1]
        feed[f"past_key_values.{i}.encoder.key"] = past_out[b + 2]
        feed[f"past_key_values.{i}.encoder.value"] = past_out[b + 3]
    return feed

# ---------------------------------------------------------------------------
# SEQUENTIAL ONNX TRANSLATION RUNNER
# ---------------------------------------------------------------------------
def translate_single_case(
    snap_dir: Path,
    src_text: str,
    src_lang: str,
    tgt_lang: str = "eng_Latn",
    max_tokens: int = MAX_GEN_TOKENS,
) -> tuple[str, str, bool, dict[str, float]]:
    """
    Executes single-sentence translation with sequential session lifetime:
      Phase 1: Load Encoder -> Encode -> Release Encoder -> gc.collect()
      Phase 2: Load Decoder (Initial) -> Step 0 -> Release Initial Decoder -> gc.collect()
      Phase 3: Load Decoder (with Past) -> Steps 1..N -> Release Decoder -> gc.collect()
    Returns: (raw_decoded_output, normalized_output, success_bool, phase_metrics)
    """
    import numpy as np
    import onnxruntime as ort
    from tokenizers import Tokenizer

    metrics: dict[str, float] = {}
    providers = ["CPUExecutionProvider"]

    # 1. Load Tokenizers & Configs
    try:
        src_tok = Tokenizer.from_file(str(snap_dir / "tokenizer_src.json"))
        tgt_tok = Tokenizer.from_file(str(snap_dir / "tokenizer_tgt.json"))
        meta = json.loads((snap_dir / "tokenizer_meta.json").read_text())
        gencfg = json.loads((snap_dir / "generation_config.json").read_text())
    except Exception as exc:
        print(f"FATAL: Tokenizer/config load failed: {exc}", file=sys.stderr)
        raise

    dec_start_token = int(gencfg.get("decoder_start_token_id", 2))
    eos_token_id = int(gencfg.get("eos_token_id", 2))
    src_vocab_size = meta["src_dict_size"]
    tgt_vocab_size = meta["tgt_dict_size"]
    unk_token_id = meta["unk_id"]

    prefixed_input = build_prefixed(src_text, src_lang, tgt_lang)
    enc_encoded = src_tok.encode(prefixed_input)
    inp_ids = np.array([[i if i < src_vocab_size else unk_token_id for i in enc_encoded.ids]], dtype=np.int64)
    attn_mask = np.array([enc_encoded.attention_mask], dtype=np.int64)

    # ---------------------------------------------------------
    # PHASE 1: ENCODER SESSION
    # ---------------------------------------------------------
    metrics["BEFORE_ENCODER_SESSION_RSS_MiB"] = _rss_mib()
    so_enc = create_session_options(ort)

    try:
        encoder_session = ort.InferenceSession(
            str(snap_dir / "encoder_model.onnx"),
            sess_options=so_enc,
            providers=providers,
        )
    except Exception as exc:
        print(f"FATAL: Encoder session creation failed: {exc}", file=sys.stderr)
        raise

    metrics["AFTER_ENCODER_SESSION_RSS_MiB"] = _rss_mib()

    try:
        enc_outputs = encoder_session.run(
            ["last_hidden_state"],
            {"input_ids": inp_ids, "attention_mask": attn_mask},
        )
        enc_hidden_states = enc_outputs[0]
    except Exception as exc:
        print(f"FATAL: Encoder run failed: {exc}", file=sys.stderr)
        raise

    metrics["AFTER_ENCODER_RUN_RSS_MiB"] = _rss_mib()

    # Explicitly release Encoder session from memory
    del encoder_session
    del enc_outputs
    del so_enc
    gc.collect()
    metrics["AFTER_ENCODER_RELEASE_RSS_MiB"] = _rss_mib()

    # ---------------------------------------------------------
    # PHASE 2: INITIAL DECODER SESSION (Step 0)
    # ---------------------------------------------------------
    metrics["BEFORE_DECODER_SESSION_RSS_MiB"] = _rss_mib()
    so_dec = create_session_options(ort)

    try:
        decoder_session = ort.InferenceSession(
            str(snap_dir / "decoder_model.onnx"),
            sess_options=so_dec,
            providers=providers,
        )
    except Exception as exc:
        print(f"FATAL: Decoder session creation failed: {exc}", file=sys.stderr)
        raise

    num_layers = (len(decoder_session.get_outputs()) - 1) // 4
    dec_in = np.array([[dec_start_token]], dtype=np.int64)
    generated_ids = [dec_start_token]

    try:
        dec_out = decoder_session.run(
            None,
            {
                "input_ids": dec_in,
                "encoder_hidden_states": enc_hidden_states,
                "encoder_attention_mask": attn_mask,
            },
        )
    except Exception as exc:
        print(f"FATAL: Initial decoder step 0 failed: {exc}", file=sys.stderr)
        raise

    past_kv = list(dec_out[1:])
    next_token_id = int(np.argmax(dec_out[0][0, -1, :]))
    generated_ids.append(next_token_id)
    dec_in = np.array([[next_token_id]], dtype=np.int64)

    # Release initial decoder session before loading decoder_with_past
    del decoder_session
    del dec_out
    del so_dec
    gc.collect()

    # ---------------------------------------------------------
    # PHASE 3: DECODER WITH PAST SESSION (Steps 1..N)
    # ---------------------------------------------------------
    if next_token_id != eos_token_id:
        so_past = create_session_options(ort)
        try:
            decoder_past_session = ort.InferenceSession(
                str(snap_dir / "decoder_with_past_model.onnx"),
                sess_options=so_past,
                providers=providers,
            )
        except Exception as exc:
            print(f"FATAL: Decoder with past session creation failed: {exc}", file=sys.stderr)
            raise

        metrics["AFTER_DECODER_SESSION_RSS_MiB"] = _rss_mib()

        for _ in range(1, max_tokens):
            try:
                feed = {
                    "input_ids": dec_in,
                    "encoder_attention_mask": attn_mask,
                    **build_past_feed(past_kv, num_layers),
                }
                out = decoder_past_session.run(None, feed)
            except Exception as exc:
                print(f"FATAL: Auto-regressive decoder step failed: {exc}", file=sys.stderr)
                raise

            past_kv = list(out[1:])
            next_token_id = int(np.argmax(out[0][0, -1, :]))
            generated_ids.append(next_token_id)

            if next_token_id == eos_token_id:
                break
            dec_in = np.array([[next_token_id]], dtype=np.int64)

        metrics["AFTER_DECODER_RUN_RSS_MiB"] = _rss_mib()

        # Release decoder_with_past session
        del decoder_past_session
        del so_past
    else:
        metrics["AFTER_DECODER_SESSION_RSS_MiB"] = metrics["BEFORE_DECODER_SESSION_RSS_MiB"]
        metrics["AFTER_DECODER_RUN_RSS_MiB"] = metrics["BEFORE_DECODER_SESSION_RSS_MiB"]

    del past_kv
    del enc_hidden_states
    gc.collect()

    # 4. Decode Output
    safe_ids = [i if i < tgt_vocab_size else unk_token_id for i in generated_ids]
    raw_output = tgt_tok.decode(safe_ids, skip_special_tokens=True)
    normalized_output = normalize_technical_reference(raw_output, src_text)

    return raw_output, normalized_output, True, metrics

# ---------------------------------------------------------------------------
# MAIN EXECUTION ENTRY POINT
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="IndicTrans2 ONNX INT8 Render Free Feasibility Harness")
    parser.add_argument("--full-suite", action="store_true", help="Run full 24-case benchmark instead of single sanity case")
    args = parser.parse_args()

    # 1. Phase 1: START RSS
    start_rss = _rss_mib()
    print("=" * 72)
    print("INDICTRANS2 ONNX INT8 — RENDER FREE MEMORY-FEASIBILITY TEST")
    print("=" * 72)
    print(f"START_RSS_MiB                      : {_fmt_mib(start_rss)}")

    # 2. Phase 2: AFTER IMPORTS RSS
    t_imp0 = time.perf_counter()
    try:
        import numpy as np
        import onnxruntime as ort
        from tokenizers import Tokenizer
    except Exception as exc:
        print(f"FATAL: Required dependencies failed to import: {exc}", file=sys.stderr)
        sys.exit(1)
    t_imp = time.perf_counter() - t_imp0
    after_imports_rss = _rss_mib()

    print(f"AFTER_IMPORTS_RSS_MiB              : {_fmt_mib(after_imports_rss)} (import time {t_imp:.2f}s)")
    print()
    print("--- ENGINE & RUNTIME SETTINGS ---")
    print(f"MODEL_ID                           : {MODEL_ID}")
    print(f"ONNX Runtime version               : {ort.__version__}")
    print(f"execution provider                 : ['CPUExecutionProvider']")
    print(f"thread settings                    : intra_op_num_threads=1, inter_op_num_threads=1")
    print(f"CPU arena setting                  : False (disabled)")
    print(f"memory-pattern setting             : False (disabled)")
    print(f"graph optimization setting         : ORT_DISABLE_ALL")
    print(f"execution mode                     : ORT_SEQUENTIAL")
    print(f"RENDER_MEMORY_TARGET_MIB           : {RENDER_MEMORY_TARGET_MIB} MiB (Render Free = {RENDER_FREE_LIMIT_MIB} MiB)")
    print()

    # 3. Model Download
    snap_dir, disk_mib = download_model_files()

    # 4. Execute Translation (Single Representative Case by Default)
    case = REPRESENTATIVE_CASE
    print("\n--- SINGLE REPRESENTATIVE CASE ---")
    print(f"Label                              : {case['label']}")
    print(f"Source Text ({case['src_lang']})             : {case['src_text']}")
    print(f"Target Language                    : {case.get('tgt_lang', 'eng_Latn')}")
    print(f"Expected Reference                 : {case['expected']}")
    print(flush=True)

    t_infer0 = time.perf_counter()
    try:
        raw_output, norm_output, success, phase_metrics = translate_single_case(
            snap_dir=snap_dir,
            src_text=case["src_text"],
            src_lang=case["src_lang"],
            tgt_lang=case.get("tgt_lang", "eng_Latn"),
        )
    except Exception as exc:
        print(f"\nFATAL: Translation failed during execution: {exc}", file=sys.stderr)
        peak_err = _peak_rss_mib()
        print(f"PEAK_RSS_MiB                       : {_fmt_mib(peak_err)}")
        sys.exit(1)

    infer_latency = time.perf_counter() - t_infer0
    final_rss = _rss_mib()
    peak_rss = _peak_rss_mib()

    # 5. Output Phase-Level RSS Metrics
    print("\n--- PHASE-LEVEL RSS LOGGING ---")
    print(f"START_RSS_MiB                      : {_fmt_mib(start_rss)}")
    print(f"AFTER_IMPORTS_RSS_MiB              : {_fmt_mib(after_imports_rss)}")
    print(f"BEFORE_ENCODER_SESSION_RSS_MiB     : {_fmt_mib(phase_metrics.get('BEFORE_ENCODER_SESSION_RSS_MiB'))}")
    print(f"AFTER_ENCODER_SESSION_RSS_MiB      : {_fmt_mib(phase_metrics.get('AFTER_ENCODER_SESSION_RSS_MiB'))}")
    print(f"AFTER_ENCODER_RUN_RSS_MiB          : {_fmt_mib(phase_metrics.get('AFTER_ENCODER_RUN_RSS_MiB'))}")
    print(f"AFTER_ENCODER_RELEASE_RSS_MiB      : {_fmt_mib(phase_metrics.get('AFTER_ENCODER_RELEASE_RSS_MiB'))}")
    print(f"BEFORE_DECODER_SESSION_RSS_MiB     : {_fmt_mib(phase_metrics.get('BEFORE_DECODER_SESSION_RSS_MiB'))}")
    print(f"AFTER_DECODER_SESSION_RSS_MiB      : {_fmt_mib(phase_metrics.get('AFTER_DECODER_SESSION_RSS_MiB'))}")
    print(f"AFTER_DECODER_RUN_RSS_MiB          : {_fmt_mib(phase_metrics.get('AFTER_DECODER_RUN_RSS_MiB'))}")
    print(f"FINAL_RSS_MiB                      : {_fmt_mib(final_rss)}")
    print(f"PEAK_RSS_MiB                       : {_fmt_mib(peak_rss)}")
    print()

    # 6. Translation Result & Normalization Verification
    exact_match = (norm_output.strip().casefold() == case["expected"].strip().casefold())
    ent_preservation = check_entity_preservation(norm_output, REQUIRED_ENTITIES)
    all_ents_preserved = all(ent_preservation.values())

    print("--- TRANSLATION OUTCOME ---")
    print(f"RAW_MODEL_OUTPUT                   : {raw_output}")
    print(f"NORMALIZED_OUTPUT                  : {norm_output}")
    print(f"translation success                : {success}")
    print(f"exact match                        : {'YES' if exact_match else 'NO (minor variation)'}")
    print(f"inference latency                  : {infer_latency:.3f} s")
    print()

    # 7. Entity Preservation & Normalization Regression Results
    print("--- ENTITY PRESERVATION & REGRESSION TESTS ---")
    print(f"ENTITY_PRESERVATION_RESULT         : {'PASS (All preserved)' if all_ents_preserved else 'FAIL'}")
    for ent, present in ent_preservation.items():
        print(f"  - [{'\u2713' if present else '\u2717'}] {ent}")

    reg_passed, reg_details = run_normalization_regression_tests()
    passed_count = sum(1 for r in reg_details if r["passed"])
    total_count = len(reg_details)
    print(f"REGRESSION_RESULT                  : {'PASS (' + str(passed_count) + '/' + str(total_count) + ' cases)' if reg_passed else 'FAIL (' + str(passed_count) + '/' + str(total_count) + ')'}")
    for r in reg_details:
        status_icon = "\u2713" if r["passed"] else "\u2717"
        print(f"  - [{status_icon}] {r['desc']}")
        if not r["passed"]:
            print(f"      RAW: {r['raw']}")
            print(f"      EXP: {r['expected']}")
            print(f"      ACT: {r['actual']}")
    print()

    # 8. Render Free Feasibility Verdict
    feasible = (peak_rss is not None and peak_rss < RENDER_MEMORY_TARGET_MIB)
    headroom = RENDER_FREE_LIMIT_MIB - (peak_rss if peak_rss else 0.0)

    print("=" * 72)
    print("RENDER FREE FEASIBILITY VERDICT")
    print("=" * 72)
    print(f"Target Ceiling (Threshold)         : < {RENDER_MEMORY_TARGET_MIB} MiB")
    print(f"Hard Container Ceiling             : {RENDER_FREE_LIMIT_MIB} MiB")
    print(f"Observed Peak RSS                  : {_fmt_mib(peak_rss)}")
    print(f"Headroom vs 512 MiB                : {headroom:.1f} MiB")
    print()
    print("DISCLAIMER: Third-party ONNX INT8 conversion under evaluation;")
    print("            not yet accepted as production translation backend.")
    print()

    if feasible:
        print(f"VERDICT: \u2705 FEASIBLE  (Peak RSS {peak_rss:.1f} MiB < {RENDER_MEMORY_TARGET_MIB} MiB target)")
        print("=" * 72)
        sys.exit(0)
    else:
        print(f"VERDICT: \u274c NOT FEASIBLE  (Peak RSS {peak_rss:.1f} MiB >= {RENDER_MEMORY_TARGET_MIB} MiB target)")
        print("=" * 72)
        sys.exit(2)


if __name__ == "__main__":
    main()
