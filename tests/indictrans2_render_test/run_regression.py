#!/usr/bin/env python3
"""
Local regression test for source-aware normalize_technical_reference(),
classify_reference_consistency(), and check_entity_preservation().
Run: python tests/indictrans2_render_test/run_regression.py
"""
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


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


REGRESSION_CASES = [
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

REQUIRED_ENTITIES = ["IS 14220:2018", "5 HP", "25 mm", "openwell", "irrigation"]

all_passed = True
print("=" * 72)
print("SOURCE-AWARE NORMALIZATION REGRESSION & ADVERSARIAL TESTS")
print("=" * 72)
for tc in REGRESSION_CASES:
    actual = normalize_technical_reference(tc["raw"], tc.get("source", ""))
    actual_status = classify_reference_consistency(tc.get("source", ""), actual)
    passed_norm = (actual == tc["expected"])
    passed_status = (actual_status == tc["expected_status"])
    passed = passed_norm and passed_status
    if not passed:
        all_passed = False
    icon = "PASS" if passed else "FAIL"
    print(f"[{icon}] [{tc['id']}] {tc['desc']}")
    print(f"       STATUS: {actual_status} (expected: {tc['expected_status']})")
    if not passed:
        print(f"       RAW : {tc['raw']}")
        print(f"       SRC : {tc.get('source', '')}")
        print(f"       EXP : {tc['expected']}")
        print(f"       ACT : {actual}")

print()
print("=" * 72)
print("ENTITY PRESERVATION CHECK")
print("=" * 72)
sample_src = "IS 14220:2018 ಪ್ರಕಾರ ನೀರಾವರಿಗಾಗಿ 5 HP ಓಪನ್‌ವೆಲ್ ಪಂಪ್‌ಸೆಟ್‌ಗಳು ಮತ್ತು 25 mm ಪೈಪ್‌ಗಳನ್ನು ನೀಡಿ."
sample_raw = "IS 14220:Give 5 HP openwell pumpsets and 25 mm pipes for irrigation as per 2018 ."
normalized_render = normalize_technical_reference(sample_raw, sample_src)
print(f"SOURCE_TEXT        : {sample_src}")
print(f"RAW_MODEL_OUTPUT   : {sample_raw}")
print(f"NORMALIZED_OUTPUT  : {normalized_render}")

ent_results = check_entity_preservation(normalized_render, REQUIRED_ENTITIES)
all_ents_ok = all(ent_results.values())
print(f"\nENTITY_PRESERVATION_RESULT : {'PASS (All preserved)' if all_ents_ok else 'FAIL'}")
for ent, ok in ent_results.items():
    print(f"  - [{'OK' if ok else 'MISS'}] {ent}")

print()
print("=" * 72)
passed_count = sum(
    1 for tc in REGRESSION_CASES
    if normalize_technical_reference(tc["raw"], tc.get("source", "")) == tc["expected"]
    and classify_reference_consistency(tc.get("source", ""), normalize_technical_reference(tc["raw"], tc.get("source", ""))) == tc["expected_status"]
)
total_count = len(REGRESSION_CASES)
regression_str = f"PASS ({passed_count}/{total_count})" if all_passed else f"FAIL ({passed_count}/{total_count})"
print(f"REGRESSION_RESULT          : {regression_str}")
print("=" * 72)

sys.exit(0 if (all_passed and all_ents_ok) else 1)
