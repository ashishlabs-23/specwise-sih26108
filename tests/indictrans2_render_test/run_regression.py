#!/usr/bin/env python3
"""
Local regression test for source-aware normalize_technical_reference() and check_entity_preservation().
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


def check_entity_preservation(text: str, entities: list) -> dict:
    text_norm = re.sub(r"\s+", " ", text).casefold()
    return {ent: re.sub(r"\s+", " ", ent).casefold() in text_norm for ent in entities}


REGRESSION_CASES = [
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
        "desc": "Intact IS standard with spacing around colon",
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

REQUIRED_ENTITIES = ["IS 14220:2018", "5 HP", "25 mm", "openwell", "irrigation"]

all_passed = True
print("=" * 72)
print("SOURCE-AWARE NORMALIZATION REGRESSION & ADVERSARIAL TESTS")
print("=" * 72)
for i, tc in enumerate(REGRESSION_CASES, 1):
    actual = normalize_technical_reference(tc["raw"], tc.get("source", ""))
    passed = actual == tc["expected"]
    if not passed:
        all_passed = False
    icon = "PASS" if passed else "FAIL"
    print(f"[{icon}] Case {i}: {tc['desc']}")
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
passed_count = sum(1 for tc in REGRESSION_CASES if normalize_technical_reference(tc["raw"], tc.get("source", "")) == tc["expected"])
total_count = len(REGRESSION_CASES)
regression_str = f"PASS ({passed_count}/{total_count})" if all_passed else f"FAIL ({passed_count}/{total_count})"
print(f"REGRESSION_RESULT          : {regression_str}")
print("=" * 72)

sys.exit(0 if (all_passed and all_ents_ok) else 1)
