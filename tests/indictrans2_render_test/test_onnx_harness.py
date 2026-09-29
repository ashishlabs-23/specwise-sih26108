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
import http.server
import json
import os
import re
import socketserver
import sys
import threading
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
# REPRESENTATIVE & BENCHMARK SUITE TEST CASES
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

FULL_SUITE_CASES = [
    {
        "label": "BL-01-Hindi-plain",
        "src_text": "सिंचाई के लिए 5 HP ओपनवेल सबमर्सिबल पंपसेट की आपूर्ति करें।",
        "src_lang": "hin_Deva",
        "tgt_lang": "eng_Latn",
        "expected": "Supply 5 HP openwell submersible pumpsets for irrigation.",
        "required_entities": ["5 HP", "openwell", "submersible", "irrigation"],
    },
    {
        "label": "BL-02-Kannada-plain",
        "src_text": "ನೀರಾವರಿಗಾಗಿ 5 HP ಓಪನ್‌ವೆಲ್ ಸಬ್‌ಮರ್ಸಿಬಲ್ ಪಂಪ್‌ಸೆಟ್ ಪೂರೈಸಬೇಕು.",
        "src_lang": "kan_Knda",
        "tgt_lang": "eng_Latn",
        "expected": "A 5 HP openwell submersible pumpset should be supplied for irrigation.",
        "required_entities": ["5 HP", "openwell", "submersible", "irrigation"],
    },
    {
        "label": "BL-03-Hindi-technical",
        "src_text": "IS 14220:2018 के अनुसार सिंचाई के लिए 5 HP ओपनवेल पंपसेट और 25 mm पाइप दें।",
        "src_lang": "hin_Deva",
        "tgt_lang": "eng_Latn",
        "expected": "Give 5 HP openwell pumpsets and 25 mm pipes for irrigation as per IS 14220:2018.",
        "required_entities": ["IS 14220:2018", "5 HP", "25 mm", "openwell", "irrigation"],
    },
    {
        "label": "BL-04-Kannada-technical",
        "src_text": "IS 14220:2018 ಪ್ರಕಾರ ನೀರಾವರಿಗಾಗಿ 5 HP ಓಪನ್‌ವೆಲ್ ಪಂಪ್‌ಸೆಟ್‌ಗಳು ಮತ್ತು 25 mm ಪೈಪ್‌ಗಳನ್ನು ನೀಡಿ.",
        "src_lang": "kan_Knda",
        "tgt_lang": "eng_Latn",
        "expected": "Provide a 5 HP openwell pumpset and 25 mm pipe for irrigation according to IS 14220:2018.",
        "required_entities": ["IS 14220:2018", "5 HP", "25 mm", "openwell", "irrigation"],
    },
    {
        "label": "BL-05-Hindi-borewell-submersible",
        "src_text": "IS 8034:2018 के तहत 100 mm बोरवेल के लिए 3 HP सबमर्सिबल पंप की आवश्यकता है।",
        "src_lang": "hin_Deva",
        "tgt_lang": "eng_Latn",
        "expected": "A 3 HP submersible pump for 100 mm borewell is required under IS 8034:2018.",
        "required_entities": ["IS 8034:2018", "100 mm", "3 HP", "submersible", "borewell"],
    },
    {
        "label": "BL-06-Kannada-borewell-submersible",
        "src_text": "IS 8034:2018 ಅಡಿಯಲ್ಲಿ 100 mm ಬೋರ್‌ವೆಲ್‌ಗಾಗಿ 3 HP ಸಬ್‌ಮರ್ಸಿಬಲ್ ಪಂಪ್ ಅಗತ್ಯವಿದೆ.",
        "src_lang": "kan_Knda",
        "tgt_lang": "eng_Latn",
        "expected": "A 3 HP submersible pump is required for 100 mm borewell under IS 8034:2018.",
        "required_entities": ["IS 8034:2018", "100 mm", "3 HP", "submersible", "borewell"],
    },
    {
        "label": "BL-07-Hindi-centrifugal-monoset",
        "src_text": "IS 9079:2018 के अनुसार कृषि उपयोग हेतु मोनोसेट पंप उपलब्ध कराएं।",
        "src_lang": "hin_Deva",
        "tgt_lang": "eng_Latn",
        "expected": "Provide monoset pumps for agricultural use according to IS 9079:2018.",
        "required_entities": ["IS 9079:2018", "monoset", "pump"],
    },
    {
        "label": "BL-08-Kannada-centrifugal-monoset",
        "src_text": "IS 9079:2018 ಪ್ರಕಾರ ಕೃಷಿ ಬಳಕೆಗಾಗಿ ಮೊನೊಸೆಟ್ ಪಂಪ್ ಒದಗಿಸಿ.",
        "src_lang": "kan_Knda",
        "tgt_lang": "eng_Latn",
        "expected": "Provide monoset pump for agricultural use according to IS 9079:2018.",
        "required_entities": ["IS 9079:2018", "monoset", "pump"],
    },
    {
        "label": "BL-09-Hindi-solar-pv-water-pump",
        "src_text": "IS 14536:2018 मानक के अनुसार 5 HP सौर फोटोवोल्टिक वाटर पंपिंग सिस्टम चाहिए।",
        "src_lang": "hin_Deva",
        "tgt_lang": "eng_Latn",
        "expected": "A 5 HP solar photovoltaic water pumping system is needed as per IS 14536:2018 standard.",
        "required_entities": ["IS 14536:2018", "5 HP", "solar", "pumping"],
    },
    {
        "label": "BL-10-Kannada-solar-pv-water-pump",
        "src_text": "IS 14536:2018 ಮಾನದಂಡದ ಪ್ರಕಾರ 5 HP ಸೌರ ಫೋಟೊವೋಲ್ಟಾಯಿಕ್ ವಾಟರ್ ಪಂಪಿಂಗ್ ಸಿಸ್ಟಮ್ ಬೇಕು.",
        "src_lang": "kan_Knda",
        "tgt_lang": "eng_Latn",
        "expected": "A 5 HP solar photovoltaic water pumping system is needed according to IS 14536:2018 standard.",
        "required_entities": ["IS 14536:2018", "5 HP", "solar", "pumping"],
    },
    {
        "label": "BL-11-Hindi-submersible-motors",
        "src_text": "IS 9283:2024 के अनुरूप सबमर्सिबल मोटर की खरीद करें।",
        "src_lang": "hin_Deva",
        "tgt_lang": "eng_Latn",
        "expected": "Procure submersible motors conforming to IS 9283:2024.",
        "required_entities": ["IS 9283:2024", "submersible", "motor"],
    },
    {
        "label": "BL-12-Kannada-submersible-motors",
        "src_text": "IS 9283:2024 ಗೆ ಅನುಗುಣವಾಗಿ ಸಬ್‌ಮರ್ಸಿಬಲ್ ಮೋಟಾರ್ ಖರೀದಿಸಿ.",
        "src_lang": "kan_Knda",
        "tgt_lang": "eng_Latn",
        "expected": "Purchase submersible motor in accordance with IS 9283:2024.",
        "required_entities": ["IS 9283:2024", "submersible", "motor"],
    },
    {
        "label": "BL-13-Hindi-steel-tubes",
        "src_text": "IS 1239:1990 के अनुसार 50 mm जस्तीकृत स्टील पाइप की आपूर्ति।",
        "src_lang": "hin_Deva",
        "tgt_lang": "eng_Latn",
        "expected": "Supply of 50 mm galvanized steel pipes according to IS 1239:1990.",
        "required_entities": ["IS 1239:1990", "50 mm", "steel", "pipe"],
    },
    {
        "label": "BL-14-Kannada-steel-tubes",
        "src_text": "IS 1239:1990 ಪ್ರಕಾರ 50 mm ಕಲಾಯಿ ಉಕ್ಕಿನ ಪೈಪ್‌ಗಳ ಪೂರೈಕೆ.",
        "src_lang": "kan_Knda",
        "tgt_lang": "eng_Latn",
        "expected": "Supply of 50 mm galvanized steel pipes according to IS 1239:1990.",
        "required_entities": ["IS 1239:1990", "50 mm", "steel", "pipe"],
    },
    {
        "label": "BL-15-Hindi-pvc-cables",
        "src_text": "IS 694:2010 के अनुसार 3 कोर 4 sq mm कॉपर केबल।",
        "src_lang": "hin_Deva",
        "tgt_lang": "eng_Latn",
        "expected": "3 core 4 sq mm copper cable as per IS 694:2010.",
        "required_entities": ["IS 694:2010", "3 core", "4 sq mm", "cable"],
    },
    {
        "label": "BL-16-Kannada-pvc-cables",
        "src_text": "IS 694:2010 ಪ್ರಕಾರ 3 ಕೋರ್ 4 sq mm ತಾಮ್ರದ ಕೇಬಲ್.",
        "src_lang": "kan_Knda",
        "tgt_lang": "eng_Latn",
        "expected": "3 core 4 sq mm copper cable according to IS 694:2010.",
        "required_entities": ["IS 694:2010", "3 core", "4 sq mm", "cable"],
    },
    {
        "label": "BL-17-Hindi-armoured-cables",
        "src_text": "IS 1554:1988 के अनुसार 1.1 kV ग्रेड आर्मर्ड केबल।",
        "src_lang": "hin_Deva",
        "tgt_lang": "eng_Latn",
        "expected": "1.1 kV grade armoured cable as per IS 1554:1988.",
        "required_entities": ["IS 1554:1988", "1.1 kV", "armoured", "cable"],
    },
    {
        "label": "BL-18-Kannada-armoured-cables",
        "src_text": "IS 1554:1988 ಪ್ರಕಾರ 1.1 kV ಗ್ರೇಡ್ ಆರ್ಮರ್ಡ್ ಕೇಬಲ್.",
        "src_lang": "kan_Knda",
        "tgt_lang": "eng_Latn",
        "expected": "1.1 kV grade armoured cable according to IS 1554:1988.",
        "required_entities": ["IS 1554:1988", "1.1 kV", "armoured", "cable"],
    },
    {
        "label": "BL-19-Hindi-handpumps",
        "src_text": "IS 15500:2004 के अनुसार इंडिया मार्क II हैंडपंप सेट।",
        "src_lang": "hin_Deva",
        "tgt_lang": "eng_Latn",
        "expected": "India Mark II handpump set as per IS 15500:2004.",
        "required_entities": ["IS 15500:2004", "mark ii", "handpump"],
    },
    {
        "label": "BL-20-Kannada-handpumps",
        "src_text": "IS 15500:2004 ಪ್ರಕಾರ ಇಂಡಿಯಾ ಮಾರ್ಕ್ II ಹ್ಯಾಂಡ್‌ಪಂಪ್ ಸೆಟ್.",
        "src_lang": "kan_Knda",
        "tgt_lang": "eng_Latn",
        "expected": "India Mark II handpump set according to IS 15500:2004.",
        "required_entities": ["IS 15500:2004", "mark ii", "handpump"],
    },
    {
        "label": "BL-21-Hindi-pump-testing",
        "src_text": "IS 11346:2002 के अनुसार सबमर्सिबल पंपसेट की स्वीकृति और परीक्षण कोड।",
        "src_lang": "hin_Deva",
        "tgt_lang": "eng_Latn",
        "expected": "Code for acceptance tests for submersible pumpsets as per IS 11346:2002.",
        "required_entities": ["IS 11346:2002", "submersible", "pumpset"],
    },
    {
        "label": "BL-22-Kannada-pump-testing",
        "src_text": "IS 11346:2002 ಪ್ರಕಾರ ಸಬ್‌ಮರ್ಸಿಬಲ್ ಪಂಪ್‌ಸೆಟ್‌ನ ಸ್ವೀಕಾರ ಮತ್ತು ಪರೀಕ್ಷಾ ಕೋಡ್.",
        "src_lang": "kan_Knda",
        "tgt_lang": "eng_Latn",
        "expected": "Acceptance and test code for submersible pumpset according to IS 11346:2002.",
        "required_entities": ["IS 11346:2002", "submersible", "pumpset"],
    },
    {
        "label": "BL-23-Hindi-flow-measurement",
        "src_text": "IS 10572:1983 के अनुसार पंप प्रवाह दर का परीक्षण करें।",
        "src_lang": "hin_Deva",
        "tgt_lang": "eng_Latn",
        "expected": "Test the pump flow rate as per IS 10572:1983.",
        "required_entities": ["IS 10572:1983", "flow", "rate"],
    },
    {
        "label": "BL-24-Kannada-flow-measurement",
        "src_text": "IS 10572:1983 ಪ್ರಕಾರ ಪಂಪ್ ಹರಿವಿನ ಪ್ರಮಾಣವನ್ನು ಪರೀಕ್ಷಿಸಿ.",
        "src_lang": "kan_Knda",
        "tgt_lang": "eng_Latn",
        "expected": "Test the pump flow rate according to IS 10572:1983.",
        "required_entities": ["IS 10572:1983", "flow", "rate"],
    },
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


def classify_reference_consistency(source_text: str, output_text: str) -> str:
    """
    Deterministically classify reference consistency between source and normalized output:
      - MATCH: Every output IS reference corresponds to a source IS reference with exact same number and year,
               and all source IS references are preserved.
      - MISSING: Source contains IS reference(s) but output contains none.
      - CONFLICT: Output contains IS reference not in source, OR same IS number with different year,
                  OR output contains an unmatched split IS reference.
      - NONE: Neither source nor output contains any IS reference.
    """
    src_refs = set(extract_source_is_references(source_text))
    out_refs = set(extract_source_is_references(output_text))

    src_nums = extract_source_is_numbers(source_text)
    out_nums = extract_source_is_numbers(output_text)

    # Check for split IS standard pattern left un-reconstructed (e.g. "IS 14220...2018")
    split_is_pattern = re.compile(
        r'^\s*IS\s*(\d{3,6})\s*[:\s]\s*(.*?)\s+(as per|according to|conforming to|in accordance with|per)\s+(\d{4})\b',
        re.IGNORECASE | re.DOTALL
    )
    has_unrepaired_split = bool(split_is_pattern.search(output_text))

    if not src_refs and not out_refs and not src_nums and not out_nums and not has_unrepaired_split:
        return "NONE"

    if src_refs and not out_refs:
        if out_nums or has_unrepaired_split:
            return "CONFLICT"
        return "MISSING"

    if not src_refs and (out_refs or out_nums or has_unrepaired_split):
        return "CONFLICT"

    # Both have references
    if out_refs != src_refs or src_nums != out_nums or has_unrepaired_split:
        return "CONFLICT"

    return "MATCH"


def normalize_technical_reference(raw_text: str, source_text: str = "") -> str:
    """
    Deterministic source-aware postprocessing and technical reference normalization:
      1. Strips tokenization artifacts (escaped colons, backslashes).
      2. Normalizes decimal numbers (e.g. '7 . 5' -> '7.5').
      3. Canonicalizes intact standard formatting 'IS 14220 : 2018' -> 'IS 14220:2018'
         ONLY when supported by source_text.
      4. Restores split standard prefix (e.g. 'IS 14220:Give ... as per 2018' -> 'Give ... as per IS 14220:2018')
         ONLY when the exact IS number AND exact IS year match a source reference in source_text.
         NEVER reconstructs when source_text is empty or contains a different year / different standard.
      5. Cleans whitespace before punctuation (e.g. '2018 .' -> '2018.').
    """
    out = raw_text.strip()
    # 1. Remove escaped colons/slashes
    out = re.sub(r'\\([:/-])', r'\1', out)
    # 2. Fix decimals
    out = re.sub(r'(\d+)\s*\.\s*(\d+)', r'\1.\2', out)

    source_refs = extract_source_is_references(source_text) if source_text else []

    # 3. Canonicalize intact standard formatting when supported by source
    if source_refs:
        def _replace_intact(m):
            num, yr = m.group(1), m.group(2)
            can = f"IS {num}:{yr}"
            return can if can in source_refs else m.group(0)
        out = re.sub(r'\bIS\s*(\d{3,6})\s*:\s*(\d{4})\b', _replace_intact, out, flags=re.IGNORECASE)

    # 4. Restore split IS standard prefix ONLY when exact IS number + year exist in source_text
    split_is_pattern = re.compile(
        r'^\s*IS\s*(\d{3,6})\s*[:\s]\s*(.*?)\s+(as per|according to|conforming to|in accordance with|per)\s+(\d{4})\b(.*)$',
        re.IGNORECASE | re.DOTALL
    )
    m = split_is_pattern.match(out)
    if m:
        is_num, main_clause, prep, yr, rest = m.groups()
        canonical_ref = f"IS {is_num}:{yr}"

        # Strict safety check: exact number AND exact year must exist in source_refs
        if source_text and canonical_ref in source_refs:
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
    Validate normalization rules against key regression and adversarial cases (A through J):
      A. Exact matching number + year (must repair + MATCH)
      B. Same number, wrong year (must NOT repair + CONFLICT)
      C. Completely different standard (must NOT repair + CONFLICT)
      D. Source has no IS reference, raw contains IS (must NOT reconstruct + CONFLICT)
      E. Source has IS reference, raw omits it (no fabrication + MISSING)
      F. Exact intact reference with spacing (canonicalize only when supported by source + MATCH)
      G. Ordinary numbers (must remain untouched + NONE)
      H. Multiple source IS references (verify individually + MATCH)
      I. No IS references anywhere (mark NONE)
      J. Omitted source_text fallback (must NOT reconstruct without source evidence)
    """
    test_cases = [
        {
            "id": "A",
            "desc": "Exact matching number + year (must repair)",
            "source": "IS 14220:2018 ಪ್ರಕಾರ ನೀರಾವರಿಗಾಗಿ 5 HP ಓಪನ್‌ವೆಲ್ ಪಂಪ್‌ಸೆಟ್‌ಗಳು ಮತ್ತು 25 mm ಪೈಪ್‌ಗಳನ್ನು ನೀಡಿ.",
            "raw": "IS 14220:Give 5 HP openwell pumpsets and 25 mm pipes for irrigation as per 2018 .",
            "expected": "Give 5 HP openwell pumpsets and 25 mm pipes for irrigation as per IS 14220:2018.",
            "expected_status": "MATCH",
        },
        {
            "id": "B",
            "desc": "Same number, wrong year (must NOT repair, mark CONFLICT)",
            "source": "IS 14220:2024 ಪ್ರಕಾರ 5 HP ಪಂಪ್ ನೀಡಿ.",
            "raw": "IS 14220:Give 5 HP pumps as per 2018 .",
            "expected": "IS 14220:Give 5 HP pumps as per 2018.",
            "expected_status": "CONFLICT",
        },
        {
            "id": "C",
            "desc": "Completely different standard (must NOT repair, mark CONFLICT)",
            "source": "IS 1239:1990 ಪ್ರಕಾರ 50 mm ಪೈಪ್ ನೀಡಿ.",
            "raw": "IS 14220:Give 5 HP pumps as per 2018 .",
            "expected": "IS 14220:Give 5 HP pumps as per 2018.",
            "expected_status": "CONFLICT",
        },
        {
            "id": "D",
            "desc": "Source has no IS reference, raw contains IS (must NOT reconstruct, mark CONFLICT)",
            "source": "ನೀರಾವರಿಗಾಗಿ ಪಂಪ್‌ಗಳನ್ನು ಆರ್ಡರ್ ಮಾಡಿ.",
            "raw": "IS 99999:Order pumps for irrigation as per 2018 .",
            "expected": "IS 99999:Order pumps for irrigation as per 2018.",
            "expected_status": "CONFLICT",
        },
        {
            "id": "E",
            "desc": "Source has IS reference, raw omits it (no fabrication, mark MISSING)",
            "source": "IS 14220:2018 ಪ್ರಕಾರ 5 HP ಪಂಪ್ ನೀಡಿ.",
            "raw": "Give 5 HP openwell pump for irrigation .",
            "expected": "Give 5 HP openwell pump for irrigation.",
            "expected_status": "MISSING",
        },
        {
            "id": "F",
            "desc": "Exact intact reference with spacing (canonicalize only when supported by source, mark MATCH)",
            "source": "IS 14220:2018 ಪ್ರಕಾರ 5 HP ಪಂಪ್ ನೀಡಿ.",
            "raw": "Give 5 HP pumps as per IS 14220 : 2018 .",
            "expected": "Give 5 HP pumps as per IS 14220:2018.",
            "expected_status": "MATCH",
        },
        {
            "id": "G",
            "desc": "Ordinary numbers (must remain untouched, mark NONE)",
            "source": "2024 ರ ಇನ್‌ವಾಯ್ಸ್ 14220 ರಂತೆ 500 RPM ನಲ್ಲಿ 25 mm ನ 100 ಪೈಪ್‌ಗಳನ್ನು ಆರ್ಡರ್ ಮಾಡಿ.",
            "raw": "Order 100 pipes of 25 mm at 500 RPM for 2024 as per invoice 14220 .",
            "expected": "Order 100 pipes of 25 mm at 500 RPM for 2024 as per invoice 14220.",
            "expected_status": "NONE",
        },
        {
            "id": "H",
            "desc": "Multiple source IS references (verify individually, mark MATCH)",
            "source": "IS 1239:1990 ಮತ್ತು IS 694:2010 ಪ್ರಕಾರ ಪೈಪ್ ಮತ್ತು ಕೇಬಲ್ ಪೂರೈಸಿ.",
            "raw": "Supply pipes as per IS 1239 : 1990 and cables as per IS 694 : 2010 .",
            "expected": "Supply pipes as per IS 1239:1990 and cables as per IS 694:2010.",
            "expected_status": "MATCH",
        },
        {
            "id": "I",
            "desc": "No IS references anywhere (mark NONE)",
            "source": "ಕೃಷಿಗಾಗಿ ಉತ್ತಮ ಗುಣಮಟ್ಟದ ಪಂಪ್‌ಸೆಟ್ ನೀಡಿ.",
            "raw": "Provide high quality pumpset for agriculture .",
            "expected": "Provide high quality pumpset for agriculture.",
            "expected_status": "NONE",
        },
        {
            "id": "J",
            "desc": "Omitted source_text fallback (must NOT reconstruct without source evidence)",
            "source": "",
            "raw": "IS 14220:Give 5 HP openwell pumpsets as per 2018 .",
            "expected": "IS 14220:Give 5 HP openwell pumpsets as per 2018.",
            "expected_status": "CONFLICT",
        },
    ]

    all_passed = True
    results = []
    for tc in test_cases:
        actual = normalize_technical_reference(tc["raw"], tc.get("source", ""))
        actual_status = classify_reference_consistency(tc.get("source", ""), actual)
        passed_norm = (actual == tc["expected"])
        passed_status = (actual_status == tc["expected_status"])
        passed = passed_norm and passed_status
        if not passed:
            all_passed = False
        results.append({
            "id": tc["id"],
            "desc": tc["desc"],
            "raw": tc["raw"],
            "source": tc.get("source", ""),
            "expected": tc["expected"],
            "actual": actual,
            "expected_status": tc["expected_status"],
            "actual_status": actual_status,
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
# THREAD-SAFE BENCHMARK STATE & MINIMAL HTTP HEALTH SERVER
# ---------------------------------------------------------------------------
class BenchmarkState:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._status = "running"  # "running", "completed", "failed"
        self._completed = False

    def set_completed(self, success: bool = True) -> None:
        with self._lock:
            self._completed = True
            self._status = "completed" if success else "failed"

    def get_response(self) -> dict[str, str]:
        with self._lock:
            if self._status == "failed":
                return {"status": "error", "benchmark": "failed"}
            elif self._status == "completed":
                return {"status": "ok", "benchmark": "completed"}
            else:
                return {"status": "ok", "benchmark": "running"}

    @property
    def status_str(self) -> str:
        with self._lock:
            return self._status

    @property
    def is_completed(self) -> bool:
        with self._lock:
            return self._completed


BENCHMARK_STATE = BenchmarkState()


class HealthHandler(http.server.BaseHTTPRequestHandler):
    """Minimal HTTP RequestHandler serving /health and / endpoints."""

    def do_GET(self) -> None:
        if self.path in ("/health", "/health/"):
            data = BENCHMARK_STATE.get_response()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            payload = json.dumps(data).encode("utf-8")
            self.wfile.write(payload)
        elif self.path in ("/", ""):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"SpecWise IndicTrans2 ONNX INT8 Benchmark Service Running\n")
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Not Found\n")

    def log_message(self, format: str, *args: object) -> None:
        # Keep logs clean; suppress noisy standard HTTP access logs
        pass


def start_health_server_background(port: int) -> tuple[socketserver.TCPServer, threading.Thread]:
    """Start minimal single-threaded HTTP health server in background daemon thread."""
    socketserver.TCPServer.allow_reuse_address = True
    server_address = ("0.0.0.0", port)
    httpd = socketserver.TCPServer(server_address, HealthHandler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    print(f"[HTTP SERVER] Started background listener on http://0.0.0.0:{port} (health endpoint: /health)", flush=True)
    return httpd, server_thread


# ---------------------------------------------------------------------------
# MAIN EXECUTION ENTRY POINT
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="IndicTrans2 ONNX INT8 Render Free Feasibility Harness")
    parser.add_argument("--full-suite", action="store_true", help="Run full 24-case benchmark instead of single sanity case")
    args = parser.parse_args()

    is_full_suite = args.full_suite or os.environ.get("FULL_SUITE", "").strip().lower() in ("true", "1", "yes")
    port = int(os.environ.get("PORT", "10000"))

    if is_full_suite:
        print("FULL_SUITE_ENABLED=true")

    # Start the HTTP health server in background daemon thread BEFORE beginning benchmark
    httpd, server_thread = start_health_server_background(port)

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
        BENCHMARK_STATE.set_completed(success=False)
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
    print(f"FULL_SUITE_MODE                    : {is_full_suite}")
    print()

    # 3. Model Download
    try:
        snap_dir, disk_mib = download_model_files()
    except Exception as exc:
        BENCHMARK_STATE.set_completed(success=False)
        sys.exit(1)

    cases = FULL_SUITE_CASES if is_full_suite else [REPRESENTATIVE_CASE]

    suite_t0 = time.perf_counter()
    last_phase_metrics = {}
    all_successful = True
    last_raw_output = ""
    last_norm_output = ""
    case_records = []

    if is_full_suite:
        print(f"\n--- FULL {len(cases)}-CASE BENCHMARK EXECUTION ---")
        for idx, case in enumerate(cases, 1):
            t_case0 = time.perf_counter()
            try:
                raw_out, norm_out, succ, p_metrics = translate_single_case(
                    snap_dir=snap_dir,
                    src_text=case["src_text"],
                    src_lang=case["src_lang"],
                    tgt_lang=case.get("tgt_lang", "eng_Latn"),
                )
                case_lat = time.perf_counter() - t_case0
                last_phase_metrics = p_metrics
                last_raw_output = raw_out
                last_norm_output = norm_out

                exact = (norm_out.strip().casefold() == case["expected"].strip().casefold())
                ref_consistency = classify_reference_consistency(case["src_text"], norm_out)
                ent_preservation = check_entity_preservation(norm_out, case.get("required_entities", []))
                all_ents = all(ent_preservation.values()) if case.get("required_entities") else True
                peak_after = _peak_rss_mib()

                if not succ:
                    all_successful = False

                case_records.append({
                    "case_id": case["label"],
                    "inference_success": succ,
                    "exact_match": exact,
                    "reference_consistency": ref_consistency,
                    "technical_entity_preservation": all_ents,
                    "output_text": norm_out,
                    "latency": case_lat,
                    "peak_rss_after_case": peak_after,
                })

                print(f"[{idx:02d}/{len(cases):02d}] {case['label']:<32} | {case_lat:.2f}s | exact={'YES' if exact else 'DIFF'} | ref={ref_consistency:<8} | ent={'PASS' if all_ents else 'FAIL'} | peak={peak_after:.1f}MiB | out: {norm_out}")
            except Exception as exc:
                all_successful = False
                case_records.append({
                    "case_id": case["label"],
                    "inference_success": False,
                    "exact_match": False,
                    "reference_consistency": "CONFLICT",
                    "technical_entity_preservation": False,
                    "output_text": "",
                    "latency": 0.0,
                    "peak_rss_after_case": _peak_rss_mib(),
                })
                print(f"[{idx:02d}/{len(cases):02d}] {case['label']:<32} | ERROR: {exc}", file=sys.stderr)
    else:
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
            last_phase_metrics = phase_metrics
            last_raw_output = raw_output
            last_norm_output = norm_output
            if not success:
                all_successful = False
        except Exception as exc:
            print(f"\nFATAL: Translation failed during execution: {exc}", file=sys.stderr)
            peak_err = _peak_rss_mib()
            print(f"PEAK_RSS_MiB                       : {_fmt_mib(peak_err)}")
            BENCHMARK_STATE.set_completed(success=False)
            sys.exit(1)

    total_infer_latency = time.perf_counter() - suite_t0
    final_rss = _rss_mib()
    peak_rss = _peak_rss_mib()

    # 5. Output Phase-Level RSS Metrics
    print("\n--- PHASE-LEVEL RSS LOGGING ---")
    print(f"START_RSS_MiB                      : {_fmt_mib(start_rss)}")
    print(f"AFTER_IMPORTS_RSS_MiB              : {_fmt_mib(after_imports_rss)}")
    print(f"BEFORE_ENCODER_SESSION_RSS_MiB     : {_fmt_mib(last_phase_metrics.get('BEFORE_ENCODER_SESSION_RSS_MiB'))}")
    print(f"AFTER_ENCODER_SESSION_RSS_MiB      : {_fmt_mib(last_phase_metrics.get('AFTER_ENCODER_SESSION_RSS_MiB'))}")
    print(f"AFTER_ENCODER_RUN_RSS_MiB          : {_fmt_mib(last_phase_metrics.get('AFTER_ENCODER_RUN_RSS_MiB'))}")
    print(f"AFTER_ENCODER_RELEASE_RSS_MiB      : {_fmt_mib(last_phase_metrics.get('AFTER_ENCODER_RELEASE_RSS_MiB'))}")
    print(f"BEFORE_DECODER_SESSION_RSS_MiB     : {_fmt_mib(last_phase_metrics.get('BEFORE_DECODER_SESSION_RSS_MiB'))}")
    print(f"AFTER_DECODER_SESSION_RSS_MiB      : {_fmt_mib(last_phase_metrics.get('AFTER_DECODER_SESSION_RSS_MiB'))}")
    print(f"AFTER_DECODER_RUN_RSS_MiB          : {_fmt_mib(last_phase_metrics.get('AFTER_DECODER_RUN_RSS_MiB'))}")
    print(f"FINAL_RSS_MiB                      : {_fmt_mib(final_rss)}")
    print(f"PEAK_RSS_MiB                       : {_fmt_mib(peak_rss)}")
    print()

    # 6. Translation Result & Normalization Verification
    if not is_full_suite:
        exact_match = (last_norm_output.strip().casefold() == REPRESENTATIVE_CASE["expected"].strip().casefold())
        ent_preservation = check_entity_preservation(last_norm_output, REQUIRED_ENTITIES)
        all_ents_preserved = all(ent_preservation.values())
        ref_consistency = classify_reference_consistency(REPRESENTATIVE_CASE["src_text"], last_norm_output)

        print("--- TRANSLATION OUTCOME ---")
        print(f"RAW_MODEL_OUTPUT                   : {last_raw_output}")
        print(f"NORMALIZED_OUTPUT                  : {last_norm_output}")
        print(f"translation success                : {all_successful}")
        print(f"exact match                        : {'YES' if exact_match else 'NO (minor variation)'}")
        print(f"reference consistency              : {ref_consistency}")
        print(f"inference latency                  : {total_infer_latency:.3f} s")
        print()

        # 7. Entity Preservation & Normalization Regression Results
        print("--- ENTITY PRESERVATION & REGRESSION TESTS ---")
        print(f"ENTITY_PRESERVATION_RESULT         : {'PASS (All preserved)' if all_ents_preserved else 'FAIL'}")
        for ent, present in ent_preservation.items():
            status_icon = "✓" if present else "✗"
            print(f"  - [{status_icon}] {ent}")
        print(f"REFERENCE_CONSISTENCY_RESULT       : {ref_consistency}")
    else:
        total_cases = len(cases)
        inf_succ_count = sum(1 for r in case_records if r["inference_success"])
        exact_match_count = sum(1 for r in case_records if r["exact_match"])
        ref_match_count = sum(1 for r in case_records if r["reference_consistency"] == "MATCH")
        ref_missing_count = sum(1 for r in case_records if r["reference_consistency"] == "MISSING")
        ref_conflict_count = sum(1 for r in case_records if r["reference_consistency"] == "CONFLICT")
        ent_pass_count = sum(1 for r in case_records if r["technical_entity_preservation"])
        ent_fail_count = total_cases - ent_pass_count

        print("=== FULL-SUITE QUALITY EVALUATION ===")
        print(f"TOTAL_CASES                        : {total_cases}")
        print(f"INFERENCE_SUCCESS                  : {inf_succ_count}/{total_cases}")
        print(f"EXACT_MATCH_COUNT                  : {exact_match_count}/{total_cases}")
        print(f"REFERENCE_MATCH_COUNT              : {ref_match_count}/{total_cases}")
        print(f"REFERENCE_MISSING_COUNT            : {ref_missing_count}/{total_cases}")
        print(f"REFERENCE_CONFLICT_COUNT           : {ref_conflict_count}/{total_cases}")
        print(f"ENTITY_PRESERVATION_PASS           : {ent_pass_count}/{total_cases}")
        print(f"ENTITY_PRESERVATION_FAIL           : {ent_fail_count}/{total_cases}")
        print(f"TOTAL_LATENCY                      : {total_infer_latency:.3f} s")
        avg_lat = total_infer_latency / total_cases if total_cases > 0 else 0.0
        print(f"AVERAGE_LATENCY                    : {avg_lat:.3f} s/case")
        print(f"PEAK_RSS_MiB                       : {_fmt_mib(peak_rss)}")
        print("======================================")

    print()
    reg_passed, reg_details = run_normalization_regression_tests()
    passed_count = sum(1 for r in reg_details if r["passed"])
    total_count = len(reg_details)
    print(f"REGRESSION_RESULT                  : {'PASS (' + str(passed_count) + '/' + str(total_count) + ' cases)' if reg_passed else 'FAIL (' + str(passed_count) + '/' + str(total_count) + ')'}")
    for r in reg_details:
        status_icon = "✓" if r["passed"] else "✗"
        print(f"  - [{status_icon}] [{r['id']}] {r['desc']} (ref: {r['actual_status']})")
        if not r["passed"]:
            print(f"      RAW : {r['raw']}")
            print(f"      SRC : {r['source']}")
            print(f"      EXP : {r['expected']} (status: {r['expected_status']})")
            print(f"      ACT : {r['actual']} (status: {r['actual_status']})")
    print()

    # 8. Render Free Feasibility Verdict
    runtime_feasible = (peak_rss is not None and peak_rss < RENDER_MEMORY_TARGET_MIB and all_successful)
    headroom = RENDER_FREE_LIMIT_MIB - (peak_rss if peak_rss else 0.0)

    print("=" * 72)
    print("RENDER FREE FEASIBILITY VERDICT")
    print("=" * 72)
    print(f"Target Ceiling (Threshold)         : < {RENDER_MEMORY_TARGET_MIB} MiB")
    print(f"Hard Container Ceiling             : {RENDER_FREE_LIMIT_MIB} MiB")
    print(f"Observed Peak RSS                  : {_fmt_mib(peak_rss)}")
    print(f"Headroom vs 512 MiB                : {headroom:.1f} MiB")
    print()
    runtime_status = "✅ PASS (Peak RSS < 460 MiB)" if runtime_feasible else "❌ FAIL"
    print(f"RUNTIME_FEASIBILITY                : {runtime_status}")
    print("TRANSLATION_QUALITY_EVIDENCE       : Evaluated separately (see quality report above)")
    print()
    print("DISCLAIMER: Third-party ONNX INT8 conversion under evaluation;")
    print("            not yet accepted as production translation backend.")
    print()

    if runtime_feasible:
        BENCHMARK_STATE.set_completed(success=True)
        print("BENCHMARK_COMPLETED=true")
        print()
        print("=== RENDER SERVICE STATE ===")
        print("BENCHMARK_COMPLETED: True")
        print(f"BENCHMARK_STATUS: {BENCHMARK_STATE.status_str}")
        print(f"SERVER_PORT: {port}")
        print("HEALTH_ENDPOINT: /health")
        print(f"FULL_SUITE: {is_full_suite}")
        print("============================")
        print("[SERVICE] Benchmark complete. Keep-alive active (serving /health on background thread)...", flush=True)
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            print("\n[SERVICE] Exiting on SIGINT/SIGTERM...", flush=True)
            sys.exit(0)
    else:
        BENCHMARK_STATE.set_completed(success=False)
        print("BENCHMARK_COMPLETED=false")
        print()
        print("=== RENDER SERVICE STATE ===")
        print("BENCHMARK_COMPLETED: False")
        print(f"BENCHMARK_STATUS: {BENCHMARK_STATE.status_str}")
        print(f"SERVER_PORT: {port}")
        print("HEALTH_ENDPOINT: /health")
        print(f"FULL_SUITE: {is_full_suite}")
        print("============================")
        sys.exit(2)


if __name__ == "__main__":
    main()
