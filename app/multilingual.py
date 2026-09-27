"""Deterministic, safety-first multilingual query preprocessing.

This module preserves the submitted text and creates a separate, validated English
representation for the existing English retrieval pipeline.  It never translates
corpus evidence or source material.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
import re
from typing import Protocol


SUPPORTED_LANGUAGES = {"en", "hi", "kn", "ta", "te"}
LANGUAGE_LABELS = {
    "en": "English", "hi": "Hindi", "kn": "Kannada", "ta": "Tamil",
    "te": "Telugu", "mixed": "Mixed language", "unsupported": "Unsupported",
}
FLORES_CODES = {"hi": "hin_Deva", "kn": "kan_Knda", "ta": "tam_Taml", "te": "tel_Telu"}
SCRIPT_RANGES = {
    "hi": re.compile(r"[\u0900-\u097F]"),
    "kn": re.compile(r"[\u0C80-\u0CFF]"),
    "ta": re.compile(r"[\u0B80-\u0BFF]"),
    "te": re.compile(r"[\u0C00-\u0C7F]"),
}
# Devanagari is not Hindi-exclusive.  These common Marathi markers keep known
# non-MVP Marathi input out of the Hindi model path.
MARATHI_MARKERS = {"साठी", "पुरवठा", "सिंचनासाठी", "विहीर", "पंपसंच"}
ENGLISH_TERMS = re.compile(
    r"\b(?:open[ -]?well|bore[ -]?well|submersible|pump(?:set| set)?|"
    r"irrigation|supply|head|flow|voltage|standard|procurement)\b", re.I
)
NEGATIONS = {
    "en": re.compile(r"\b(?:no|not|without|exclude|excluding)\b", re.I),
    "hi": re.compile(r"(?:नहीं|नहि|बिना|मत)"),
    "kn": re.compile(r"(?:ಅಲ್ಲ|ಬೇಡ|ಇಲ್ಲದೆ)"),
    "ta": re.compile(r"(?:இல்லை|இல்லாமல்|வேண்டாம்)"),
    "te": re.compile(r"(?:కాదు|లేదు|లేకుండా|వద్దు)"),
}
# Entity detection deliberately allows only recognized engineering forms. Values
# are restored byte-for-byte after model output and checked again before routing.
TECHNICAL_ENTITY = re.compile(
    r"\b(?:IS\s*\d{3,6}(?::\d{4})?(?:\s*\(\s*Part\s*\d+[A-Za-z]?\s*\))?|"
    r"Part\s*\d+[A-Za-z]?|(?:19|20)\d{2}|\d+(?:\.\d+)?\s*(?:HP|kV|V|Hz|mm|m|L/s|LPS|LPM|m3/h)|"
    r"\d+(?:\.\d+)?\s*[x×]\s*\d+(?:\.\d+)?\s*(?:mm|m)|[A-Za-z]{1,8}[-/]\d{2,}[A-Za-z0-9-]*)\b",
    re.I,
)


@dataclass(frozen=True)
class LanguageMetadata:
    detected: str
    processing_mode: str
    translation_verified: bool


@dataclass(frozen=True)
class PreparedInput:
    original_text: str
    normalized_english_text: str | None
    metadata: LanguageMetadata
    failure_reason: str | None = None


class Translator(Protocol):
    def translate(self, text: str, source_language: str) -> str: ...


class IndicTrans2Translator:
    """Lazy local IndicTrans2 adapter.

    A model must be provisioned locally via INDICTRANS2_MODEL_PATH.  Network
    download is deliberately disabled in the request path so unavailable model
    state cannot become an undocumented remote dependency or English fallback.
    """

    def __init__(self, model_path: str | None = None):
        self.model_path = model_path or os.getenv("INDICTRANS2_MODEL_PATH")
        self._model = None
        self._tokenizer = None
        self._processor = None
        self._load_error: str | None = None

    def _load(self) -> None:
        if self._model is not None or self._load_error is not None:
            return
        if not self.model_path:
            self._load_error = "IndicTrans2 model is not provisioned locally."
            return
        try:
            from IndicTransToolkit import IndicProcessor
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            self._processor = IndicProcessor(inference=True)
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, trust_remote_code=True, local_files_only=True
            )
            self._model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_path, trust_remote_code=True, local_files_only=True
            )
        except Exception:
            self._load_error = "IndicTrans2 model could not be loaded from its configured local path."

    def translate(self, text: str, source_language: str) -> str:
        self._load()
        if self._model is None or self._tokenizer is None or self._processor is None:
            raise RuntimeError(self._load_error or "IndicTrans2 is unavailable.")
        source = FLORES_CODES[source_language]
        # IndicTrans2's maintained toolkit handles its FLORES tags and
        # script/token normalization before and after model inference.
        batch = self._processor.preprocess_batch([text], src_lang=source, tgt_lang="eng_Latn")
        encoded = self._tokenizer(
            batch, return_tensors="pt", padding=True, truncation=True, max_length=256
        )
        generated = self._model.generate(**encoded, max_new_tokens=256, num_beams=1)
        decoded = self._tokenizer.batch_decode(generated, skip_special_tokens=True)
        return self._processor.postprocess_batch(decoded, lang="eng_Latn")[0].strip()


def detect_language(text: str) -> str:
    scripts = [code for code, pattern in SCRIPT_RANGES.items() if pattern.search(text)]
    if len(scripts) > 1:
        return "unsupported"
    if not scripts:
        return "en" if re.search(r"[A-Za-z]", text) else "unsupported"
    language = scripts[0]
    if language == "hi" and any(marker in text for marker in MARATHI_MARKERS):
        return "unsupported"
    # Technical English words embedded in an Indic sentence are intentionally
    # classified mixed, rather than assuming the entire text is English.
    return "mixed" if ENGLISH_TERMS.search(text) else language


def protect_entities(text: str) -> tuple[str, dict[str, str]]:
    protected: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        key = f"SPECWISEENTITY{len(protected)}X"
        protected[key] = match.group(0)
        return key

    return TECHNICAL_ENTITY.sub(replace, text), protected


def restore_entities(text: str, protected: dict[str, str]) -> str:
    for key, value in protected.items():
        text = re.sub(re.escape(key), value, text, flags=re.I)
    return text


def normalize_technical_terms(text: str) -> str:
    normalized = text
    normalized = re.sub(r"\bopen[ -]?well\b", "openwell", normalized, flags=re.I)
    normalized = re.sub(r"\bbore[ -]?well\b", "borewell", normalized, flags=re.I)
    normalized = re.sub(r"\bsubmersible\s+pump\s*set\b", "submersible pumpset", normalized, flags=re.I)
    normalized = re.sub(r"\bsubmersible\s+pumpset\b", "submersible pumpset", normalized, flags=re.I)
    return normalized


def _entities_preserved(normalized: str, protected: dict[str, str]) -> bool:
    return all(value.lower() in normalized.lower() for value in protected.values())


def _has_contradictory_family(text: str) -> bool:
    lowered = text.lower()
    return "openwell" in lowered and "borewell" in lowered


def validate_translation(source: str, normalized: str, language: str, protected: dict[str, str]) -> bool:
    if not normalized.strip() or not _entities_preserved(normalized, protected):
        return False
    if _has_contradictory_family(normalized):
        return False
    source_negated = bool(NEGATIONS.get(language, NEGATIONS["en"]).search(source))
    target_negated = bool(NEGATIONS["en"].search(normalized))
    if source_negated != target_negated:
        return False
    # A translated Indic procurement query must retain a product discriminator
    # before it is allowed to reach recommendation policy.
    return bool(re.search(r"\b(?:openwell|borewell|submersible)\b", normalized, re.I))


def prepare_input(text: str, translator: Translator | None = None) -> PreparedInput:
    detected = detect_language(text)
    if detected == "en":
        return PreparedInput(text, normalize_technical_terms(text), LanguageMetadata("en", "native_english", True))
    if detected == "unsupported":
        return PreparedInput(text, None, LanguageMetadata("unsupported", "unsupported", False),
                             "Multilingual normalization could not be verified.")
    if detected == "mixed":
        normalized = normalize_technical_terms(text)
        # Mixed inputs containing English corpus terms can safely use those terms
        # directly. Native prose remains preserved for audit in original_text.
        valid = bool(ENGLISH_TERMS.search(normalized)) and not _has_contradictory_family(normalized)
        return PreparedInput(text, normalized if valid else None, LanguageMetadata("mixed", "mixed", valid),
                             None if valid else "Multilingual normalization could not be verified.")
    protected_text, protected = protect_entities(text)
    if translator is None:
        translator = IndicTrans2Translator()
    try:
        translated = restore_entities(translator.translate(protected_text, detected), protected)
    except Exception:
        return PreparedInput(text, None, LanguageMetadata(detected, "translated_to_english", False),
                             "Multilingual normalization could not be verified.")
    normalized = normalize_technical_terms(translated)
    verified = validate_translation(text, normalized, detected, protected)
    return PreparedInput(text, normalized if verified else None,
                         LanguageMetadata(detected, "translated_to_english", verified),
                         None if verified else "Multilingual normalization could not be verified.")
