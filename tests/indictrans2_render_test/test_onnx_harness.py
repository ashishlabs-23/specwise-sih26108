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
  7. Graph Optimization: ORT_ENABLE_BASIC
  8. Batch size: 1
  9. Bounded sequence length: max 64/100 tokens, greedy decoding
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
    "expected": "Give 5 HP openwell pumpsets and 25 mm pipes for irrigation as per IS 14220:2018.",
}

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


def build_prefixed(text: str, src_lang: str) -> str:
    """Format input text with language prefix tag expected by BPE tokenizer."""
    for s, t in _PUNC_NORM.items():
        text = text.replace(s, t)
    text = re.sub(r"[ \t]+", " ", text).strip()
    if src_lang == "kan_Knda":
        text = "".join(_KN_TO_HI.get(ch, ch) for ch in text)
        lang_tag = "hin_Deva"
    else:
        lang_tag = src_lang
    return f"{lang_tag} {text}"


def postprocess_target_text(raw_text: str) -> str:
    """Clean tokenization artifacts from generated translation."""
    out = re.sub(r'\s*:\s*', ':', raw_text)
    out = re.sub(r'(\d+)\s*\.\s*(\d+)', r'\1.\2', out)
    return re.sub(r'\s+', ' ', out).strip()

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
    so.graph_optimization_level = ort_module.GraphOptimizationLevel.ORT_ENABLE_BASIC
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
    max_tokens: int = MAX_GEN_TOKENS,
) -> tuple[str, bool, dict[str, float]]:
    """
    Executes single-sentence translation with sequential session lifetime:
      Phase 1: Load Encoder -> Encode -> Release Encoder -> gc.collect()
      Phase 2: Load Decoder (Initial) -> Step 0 -> Release Initial Decoder -> gc.collect()
      Phase 3: Load Decoder (with Past) -> Steps 1..N -> Release Decoder -> gc.collect()
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

    prefixed_input = build_prefixed(src_text, src_lang)
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
    decoded_raw = tgt_tok.decode(safe_ids, skip_special_tokens=True)
    final_output = postprocess_target_text(decoded_raw)

    return final_output, True, metrics

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
    print(f"graph optimization setting         : ORT_ENABLE_BASIC")
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
    print(f"Expected Reference                 : {case['expected']}")
    print(flush=True)

    t_infer0 = time.perf_counter()
    try:
        output_text, success, phase_metrics = translate_single_case(
            snap_dir=snap_dir,
            src_text=case["src_text"],
            src_lang=case["src_lang"],
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

    # 6. Translation Result
    exact_match = (output_text.strip().casefold() == case["expected"].strip().casefold())
    print("--- TRANSLATION OUTCOME ---")
    print(f"translation success                : {success}")
    print(f"translation output                 : {output_text}")
    print(f"exact match                        : {'YES' if exact_match else 'NO (minor variation)'}")
    print(f"inference latency                  : {infer_latency:.3f} s")
    print()

    # 7. Render Free Feasibility Verdict
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
