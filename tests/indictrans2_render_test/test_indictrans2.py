import os
import re
import sys
import time

MODEL_ID = "ai4bharat/indictrans2-indic-en-dist-200M"
HF_TOKEN = os.environ.get("HF_TOKEN")


def safe_exception(exc):
    detail = str(exc)
    if HF_TOKEN:
        detail = detail.replace(HF_TOKEN, "[REDACTED]")
    return f"{type(exc).__name__}: {detail}"


def report_failure(stage, exc):
    print(f"{stage} failed: {safe_exception(exc)}", file=sys.stderr)


IDENTIFIER_PATTERN = re.compile(
    r"\bIS\s*\d{3,6}(?:\s*:\s*(?:19|20)\d{2})?|"
    r"\b\d+(?:\.\d+)?\s*(?:HP|mm)\b",
    re.IGNORECASE,
)


def extract_identifiers(text):
    return IDENTIFIER_PATTERN.findall(text)


def normalize_identifier(identifier):
    return re.sub(r"\s+", "", identifier).casefold()


if not HF_TOKEN:
    raise SystemExit("HF_TOKEN environment variable is required for gated model access.")

try:
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    from IndicTransToolkit.processor import IndicProcessor
except Exception as exc:
    report_failure("IndicTrans2 dependency loading", exc)
    raise SystemExit(1) from None


def peak_rss_mb():
    try:
        import resource

        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    except Exception:
        return None


inputs = (
    (
        "Hindi",
        "सिंचाई के लिए 5 HP ओपनवेल सबमर्सिबल पंपसेट की आपूर्ति करें।",
        "hin_Deva",
    ),
    (
        "Kannada",
        "ನೀರಾವರಿಗಾಗಿ 5 HP ಓಪನ್‌ವೆಲ್ ಸಬ್‌ಮರ್ಸಿಬಲ್ ಪಂಪ್‌ಸೆಟ್ ಪೂರೈಸಬೇಕು.",
        "kan_Knda",
    ),
    (
        "Hindi technical",
        "IS 14220:2018 के अनुसार सिंचाई के लिए 5 HP ओपनवेल पंपसेट और 25 mm पाइप दें।",
        "hin_Deva",
    ),
    (
        "Kannada technical",
        "IS 14220:2018 ಪ್ರಕಾರ ನೀರಾವರಿಗಾಗಿ 5 HP ಓಪನ್‌ವೆಲ್ ಪಂಪ್‌ಸೆಟ್ ಮತ್ತು 25 mm ಪೈಪ್ ಒದಗಿಸಿ.",
        "kan_Knda",
    ),
)
tgt_lang = "eng_Latn"

try:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    load_started = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID,
        trust_remote_code=True,
        token=HF_TOKEN,
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_ID,
        trust_remote_code=True,
        token=HF_TOKEN,
    ).to(device)
    model.eval()
    processor = IndicProcessor(inference=True)
    load_seconds = time.perf_counter() - load_started
except Exception as exc:
    report_failure("IndicTrans2 model/toolkit loading", exc)
    raise SystemExit(1) from None

print(f"MODEL LOAD TIME: {load_seconds:.3f} seconds")

for language, text, src_lang in inputs:
    try:
        identifiers_before = extract_identifiers(text)
        inference_started = time.perf_counter()
        batch = processor.preprocess_batch(
            [text], src_lang=src_lang, tgt_lang=tgt_lang
        )
        encoded = tokenizer(
            batch,
            return_tensors="pt",
            padding="longest",
            truncation=True,
            max_length=256,
            return_attention_mask=True,
        ).to(device)

        generation_started = time.perf_counter()
        with torch.inference_mode():
            generated = model.generate(
                **encoded,
                use_cache=True,
                min_length=0,
                max_length=256,
                num_beams=5,
                num_return_sequences=1,
            )
        generation_seconds = time.perf_counter() - generation_started
        decoded = tokenizer.batch_decode(
            generated,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )
        translation = processor.postprocess_batch(decoded, lang=tgt_lang)[0]
        inference_seconds = time.perf_counter() - inference_started
        identifiers_after = extract_identifiers(translation)
        normalized_after = {normalize_identifier(value) for value in identifiers_after}
        identifier_status = [
            (identifier, normalize_identifier(identifier) in normalized_after)
            for identifier in identifiers_before
        ]
    except Exception as exc:
        report_failure(f"{language} inference", exc)
        raise SystemExit(1) from None

    print(f"{language} actual translation: {translation}")
    print(f"{language} end-to-end inference time: {inference_seconds:.3f} seconds")
    print(f"{language} generation-only time: {generation_seconds:.3f} seconds")
    print(f"{language} identifiers before: {identifiers_before or 'none'}")
    print(f"{language} identifiers after: {identifiers_after or 'none'}")
    print(f"{language} identifier preservation diagnostic: {identifier_status}")

try:
    peak_memory = peak_rss_mb()
    if peak_memory is None:
        print("PEAK PROCESS RSS: unavailable")
    else:
        print(f"PEAK PROCESS RSS: {peak_memory:.1f} MiB")
except Exception as exc:
    report_failure("Peak process RSS measurement", exc)