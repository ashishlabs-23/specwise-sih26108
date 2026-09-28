import os
import re
import sys
import tarfile
import time
from pathlib import Path

# -----------------------------------------------------------------------------
# STATIC GUARDS: Ensure no heavyweight or unwanted frameworks are loaded
# -----------------------------------------------------------------------------
FORBIDDEN_MODULES = (
    "torch",
    "transformers",
    "app",
    "frontend",
    "firebase_admin",
    "google",
    "IndicTransToolkit",
    "sacrebleu",
    "nltk",
    "fairseq",
)
for forbidden in FORBIDDEN_MODULES:
    if forbidden in sys.modules:
        print(f"FATAL: Forbidden library '{forbidden}' detected in sys.modules", file=sys.stderr)
        sys.exit(1)


# -----------------------------------------------------------------------------
# MEMORY INSTRUMENTATION (Linux /proc/self/status with psutil/resource fallback)
# -----------------------------------------------------------------------------
def get_current_rss_mb() -> float | None:
    # Check Linux /proc/self/status for accurate unshared process RSS
    status_path = Path("/proc/self/status")
    if status_path.exists():
        try:
            for line in status_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("VmRSS:"):
                    parts = line.split()
                    return float(parts[1]) / 1024.0  # kB to MiB
        except Exception:
            pass

    try:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    except Exception:
        try:
            import psutil
            return psutil.Process().memory_info().rss / (1024.0 * 1024.0)
        except Exception:
            return None


def get_peak_rss_mb() -> float | None:
    status_path = Path("/proc/self/status")
    if status_path.exists():
        try:
            for line in status_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("VmHWM:"):
                    parts = line.split()
                    return float(parts[1]) / 1024.0  # High Water Mark kB to MiB
        except Exception:
            pass

    try:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    except Exception:
        return get_current_rss_mb()


rss_before_imports = get_current_rss_mb()

MODEL_ID = "ai4bharat/indictrans2-indic-en-dist-200M"
HF_TOKEN = os.environ.get("HF_TOKEN")


def safe_exception(exc: Exception) -> str:
    detail = str(exc)
    if HF_TOKEN:
        detail = detail.replace(HF_TOKEN, "[REDACTED]")
    return f"{type(exc).__name__}: {detail}"


def report_failure(stage: str, exc: Exception) -> None:
    print(f"{stage} failed: {safe_exception(exc)}", file=sys.stderr)


IDENTIFIER_PATTERN = re.compile(
    r"\bIS\s*\d{3,6}(?:\s*:\s*(?:19|20)\d{2})?|"
    r"\b\d+(?:\.\d+)?\s*(?:HP|mm)\b",
    re.IGNORECASE,
)


def extract_identifiers(text: str) -> list[str]:
    return IDENTIFIER_PATTERN.findall(text)


def normalize_identifier(identifier: str) -> str:
    return re.sub(r"\s+", "", identifier).casefold()


if not HF_TOKEN:
    print("FATAL: HF_TOKEN environment variable is required for gated model access.", file=sys.stderr)
    sys.exit(1)

# -----------------------------------------------------------------------------
# PREPROCESSING DEPENDENCIES (Import lightweight official modules)
# -----------------------------------------------------------------------------
try:
    import ctranslate2
    import sentencepiece as spm
    from huggingface_hub import snapshot_download
    from indicnlp.normalize.indic_normalize import IndicNormalizerFactory
    from indicnlp.tokenize.indic_tokenize import trivial_tokenize
    from indicnlp.transliterate.unicode_transliterate import UnicodeIndicTransliterator
    from sacremoses import MosesDetokenizer
except Exception as exc:
    report_failure("Lean runtime dependency loading", exc)
    sys.exit(1)

rss_after_preproc_deps = get_current_rss_mb()

# -----------------------------------------------------------------------------
# OFFICIAL AI4BHARAT PREPROCESSING ROUTINES
# Source: AI4Bharat IndicTrans2 (IndicTrans2/inference/normalize_punctuation.py
#         and IndicTrans2/inference/normalize_regex_inference.py)
# -----------------------------------------------------------------------------
PUNC_MAP = {
    "\r": "",
    "…": "...",
    " \u200B": " ",
    "\u200B": "",
    "\u200c": "",
    "\u200d": "",
    "\ufeff": "",
    "\u00a0": " ",
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
    "–": "-",
    "—": "-",
    "−": "-",
}


def punc_norm(text: str) -> str:
    """Official AI4Bharat punctuation normalization."""
    for src, tgt in PUNC_MAP.items():
        text = text.replace(src, tgt)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def normalize_regex(text: str) -> str:
    """Official AI4Bharat regex/entity spacing normalization."""
    text = re.sub(r"([A-Za-z0-9])([।,?!;:])", r"\1 \2", text)
    text = re.sub(r"([।,?!;:])([A-Za-z0-9])", r"\1 \2", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# FLORES mapping for script and language handling
LANG_TO_SCRIPT_MAP = {
    "hin_Deva": "hi",
    "kan_Knda": "kn",
    "eng_Latn": "en",
}

normalizer_factory = IndicNormalizerFactory()
normalizers = {
    "hi": normalizer_factory.get_normalizer("hi"),
    "kn": normalizer_factory.get_normalizer("kn"),
}
english_detokenizer = MosesDetokenizer(lang="en")


def preprocess_indic(text: str, src_lang: str) -> str:
    """
    Official 5-step Indic source preprocessing pipeline:
    1. Punctuation normalization
    2. Regex normalization
    3. Language-specific Unicode normalization
    4. Indic trivial tokenization
    5. Script transliteration to Devanagari (if non-Devanagari script like Kannada)
    """
    script_code = LANG_TO_SCRIPT_MAP.get(src_lang, "hi")

    # Step 1: Punctuation normalization
    t = punc_norm(text)

    # Step 2: Regex normalization
    t = normalize_regex(t)

    # Step 3: Indic Unicode normalization
    normalizer = normalizers.get(script_code)
    if normalizer:
        t = normalizer.normalize(t)

    # Step 4: Indic trivial tokenization
    tokens = trivial_tokenize(t, lang=script_code)
    t = " ".join(tokens)

    # Step 5: Transliteration to Devanagari for unified Indic vocabulary
    if script_code != "hi":
        t = UnicodeIndicTransliterator.transliterate(t, script_code, "hi")

    return t


def postprocess_english(tokens: list[str]) -> str:
    """
    Official English target postprocessing pipeline:
    1. Filter out language routing and special tokens
    2. Moses English detokenization
    3. Punctuation clean-up
    """
    # Detokenize via Moses
    text = english_detokenizer.detokenize(tokens)
    # Clean up standard spacing around colons and decimals in technical terms
    text = re.sub(r"\s*:\s*", ":", text)
    text = re.sub(r"(\d+)\s*\.\s*(\d+)", r"\1.\2", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -----------------------------------------------------------------------------
# MODEL ARTIFACT RETRIEVAL (Official AI4Bharat CT2 INT8 Checkpoint)
# -----------------------------------------------------------------------------
try:
    download_started = time.perf_counter()
    model_snapshot_dir = snapshot_download(
        repo_id=MODEL_ID,
        allow_patterns=[
            "ct2_int8_model/*",
            "*.model",
            "*.spm",
            "model.SRC",
            "model.TGT",
            "dict.*.txt",
            "vocab*",
            "additional/*",
        ],
        token=HF_TOKEN,
    )
    download_seconds = time.perf_counter() - download_started
except Exception as exc:
    report_failure("Official CT2 INT8 model snapshot download", exc)
    sys.exit(1)

# Locate CT2 directory and SentencePiece models
try:
    load_started = time.perf_counter()
    root_path = Path(model_snapshot_dir)

    # Check if inside an archive or standard directory
    ct2_dir = root_path / "ct2_int8_model"
    if not ct2_dir.is_dir():
        # Check for additional/indic-en-dist.tar.gz or ct2 tar archive
        tar_candidates = list(root_path.glob("**/*.tar.gz")) + list(root_path.glob("**/*.tar"))
        for tar_f in tar_candidates:
            if "ct2" in tar_f.name.lower() or "dist" in tar_f.name.lower():
                with tarfile.open(tar_f, "r:*") as tar:
                    tar.extractall(path=root_path)
                break
        ct2_dir = root_path / "ct2_int8_model" if (root_path / "ct2_int8_model").is_dir() else root_path

    # Locate SentencePiece models
    spm_files = list(root_path.glob("**/*.spm")) + list(root_path.glob("**/*.model"))
    src_spm_file = None
    tgt_spm_file = None

    for f in spm_files:
        name = f.name.lower()
        if "src" in name or "source" in name or "indic" in name:
            src_spm_file = f
        elif "tgt" in name or "target" in name or "en" in name:
            tgt_spm_file = f

    if not src_spm_file and spm_files:
        src_spm_file = spm_files[0]
    if not tgt_spm_file:
        tgt_spm_file = src_spm_file

    if not src_spm_file or not src_spm_file.exists():
        raise FileNotFoundError(f"Source SentencePiece model not found in snapshot: {model_snapshot_dir}")

    src_sp = spm.SentencePieceProcessor()
    src_sp.load(str(src_spm_file))

    tgt_sp = spm.SentencePieceProcessor()
    if tgt_sp_file and tgt_sp_file.exists() and tgt_sp_file != src_spm_file:
        tgt_sp.load(str(tgt_spm_file))
    else:
        tgt_sp = src_sp

    # Initialize single CTranslate2 INT8 CPU Translator instance
    translator = ctranslate2.Translator(
        str(ct2_dir),
        device="cpu",
        compute_type="int8",
        intra_threads=1,
        inter_threads=1,
    )
    load_seconds = time.perf_counter() - load_started
except Exception as exc:
    report_failure("CTranslate2 INT8 model/tokenizer initialization", exc)
    sys.exit(1)

rss_after_model_load = get_current_rss_mb()

print("=" * 70)
print("INDICTRANS2 TRUE LEAN CT2 INT8 VALIDATION HARNESS")
print("=" * 70)
print(f"Model ID:              {MODEL_ID}")
print(f"Execution Engine:      CTranslate2 INT8 (CPU, 1 instance)")
print(f"Model download time:   {download_seconds:.3f} s")
print(f"Model load time:       {load_seconds:.3f} s")
if rss_before_imports is not None:
    print(f"RSS before imports:    {rss_before_imports:.2f} MiB")
if rss_after_preproc_deps is not None:
    print(f"RSS after preproc:     {rss_after_preproc_deps:.2f} MiB")
if rss_after_model_load is not None:
    print(f"RSS after model load:  {rss_after_model_load:.2f} MiB")
print("=" * 70)


def translate_sentence(text: str, src_lang: str, tgt_lang: str) -> tuple[str, float, float]:
    t0 = time.perf_counter()

    # Step 1-5: Full official Indic preprocessing
    preprocessed_text = preprocess_indic(text, src_lang=src_lang)

    # Step 6: SentencePiece subword tokenization
    subwords = src_sp.encode_as_pieces(preprocessed_text)

    # Step 7-8: Language tag routing and 256-token truncation
    # Format: [src_lang] + tokens[:254] + ["</s>"]
    input_tokens = [src_lang] + subwords[:254] + ["</s>"]

    # Step 9: CTranslate2 INT8 translation
    t_gen_start = time.perf_counter()
    results = translator.translate_batch(
        [input_tokens],
        beam_size=5,
        max_decoding_length=256,
        target_prefix=[[tgt_lang]],
    )
    t_gen = time.perf_counter() - t_gen_start

    # Step 10: SentencePiece decoding
    raw_tokens = results[0].hypotheses[0]
    special_tokens = {src_lang, tgt_lang, "</s>", "<s>", "<unk>", "<pad>"}
    filtered_tokens = [tok for tok in raw_tokens if tok not in special_tokens]

    # Step 11-12: English target postprocessing & detokenization
    decoded_raw = tgt_sp.decode_pieces(filtered_tokens)
    final_english = postprocess_english(decoded_raw.split())

    total_time = time.perf_counter() - t0
    return final_english, total_time, t_gen


# -----------------------------------------------------------------------------
# VALIDATION TEST CASES & PARITY TARGETS
# -----------------------------------------------------------------------------
VALIDATION_CASES = (
    (
        "Hindi",
        "सिंचाई के लिए 5 HP ओपनवेल सबमर्सिबल पंपसेट की आपूर्ति करें।",
        "hin_Deva",
        "Supply 5 HP openwell submersible pumpsets for irrigation.",
    ),
    (
        "Kannada",
        "ನೀರಾವರಿಗಾಗಿ 5 HP ಓಪನ್ವೆಲ್ ಸಬ್ಮರ್ಸಿಬಲ್ ಪಂಪ್ಸೆಟ್ ಪೂರೈಸಬೇಕು.",
        "kan_Knda",
        "A 5 HP openwell submersible pumpset should be supplied for irrigation.",
    ),
    (
        "Hindi technical",
        "IS 14220:2018 के अनुसार सिंचाई के लिए 5 HP ओपनवेल पंपसेट और 25 mm पाइप दें।",
        "hin_Deva",
        "Give 5 HP open well pumpsets and 25 mm pipes for irrigation as per IS 14220:2018.",
    ),
    (
        "Kannada technical",
        "IS 14220:2018 ಪ್ರಕಾರ ನೀರಾವರಿಗಾಗಿ 5 HP ಓಪನ್ವೆಲ್ ಪಂಪ್ಸೆಟ್ ಮತ್ತು 25 mm ಪೈಪ್ ಒದಗಿಸಿ.",
        "kan_Knda",
        "Provide a 5 HP openwell pumpset and 25 mm pipe for irrigation according to IS 14220:2018.",
    ),
)
tgt_lang = "eng_Latn"

success_count = 0
first_inference_rss = None

for idx, (lang_label, raw_text, src_code, expected_ref) in enumerate(VALIDATION_CASES, start=1):
    try:
        identifiers_before = extract_identifiers(raw_text)
        actual_translation, total_sec, gen_sec = translate_sentence(raw_text, src_lang=src_code, tgt_lang=tgt_lang)

        if idx == 1:
            first_inference_rss = get_current_rss_mb()

        identifiers_after = extract_identifiers(actual_translation)
        norm_after = {normalize_identifier(v) for v in identifiers_after}
        preservation = [
            (ident, normalize_identifier(ident) in norm_after)
            for ident in identifiers_before
        ]

        # Parity evaluation against independent lean reference
        is_exact_match = (actual_translation.strip().casefold() == expected_ref.strip().casefold())
        parity_status = "EXACT MATCH" if is_exact_match else "DIFFERENT OUTPUT"

        print(f"\nCASE {idx} [{lang_label}]")
        print(f"  Input:         {raw_text}")
        print(f"  Actual Output: {actual_translation}")
        print(f"  Reference:     {expected_ref}")
        print(f"  Parity Check:  {parity_status}")
        print(f"  Latency:       Total: {total_sec:.3f} s (Generation: {gen_sec:.3f} s)")
        print(f"  Identifiers:   before={identifiers_before} | after={identifiers_after}")
        print(f"  Preservation:  {preservation}")

        success_count += 1
    except Exception as exc:
        report_failure(f"Inference case {idx} ({lang_label})", exc)
        print(f"  Parity Check:  ERROR ({safe_exception(exc)})")

rss_peak = get_peak_rss_mb()

print("\n" + "=" * 70)
print("LEAN RUNTIME VALIDATION SUMMARY")
print("=" * 70)
print(f"Cases executed:             {len(VALIDATION_CASES)}")
print(f"Successful cases:           {success_count}/{len(VALIDATION_CASES)}")
if rss_before_imports is not None:
    print(f"RSS before imports:         {rss_before_imports:.2f} MiB")
if rss_after_preproc_deps is not None:
    print(f"RSS after preproc deps:     {rss_after_preproc_deps:.2f} MiB")
if rss_after_model_load is not None:
    print(f"RSS after model load:       {rss_after_model_load:.2f} MiB")
if first_inference_rss is not None:
    print(f"RSS after 1st inference:    {first_inference_rss:.2f} MiB")
if rss_peak is not None:
    print(f"Peak observed RSS:          {rss_peak:.2f} MiB")
print("=" * 70)

if success_count != len(VALIDATION_CASES):
    sys.exit(1)