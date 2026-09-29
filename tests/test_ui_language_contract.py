"""
tests/test_ui_language_contract.py
==================================
Unit and contract tests for the frontend UI multilingual support:
  - Supported language list (en, hi, kn, ta, te)
  - Dictionary completeness across all 5 languages
  - Fallback to English for invalid language codes
  - Storage key definition (specwise_lang)
  - Backend API purity (ensures backend is unchanged and independent of UI language)
"""

import json
import re
from pathlib import Path
import pytest

FRONTEND_SRC = Path(__file__).parent.parent / "frontend" / "src"
LANG_CONTEXT_FILE = FRONTEND_SRC / "context" / "LanguageContext.tsx"
NAVBAR_FILE = FRONTEND_SRC / "components" / "Navbar.tsx"


def test_language_context_file_exists():
    assert LANG_CONTEXT_FILE.exists(), f"LanguageContext.tsx not found at {LANG_CONTEXT_FILE}"


def test_supported_languages_list():
    content = LANG_CONTEXT_FILE.read_text(encoding="utf-8")
    match = re.search(r'export const languages\s*=\s*\[(.*?)\]\s*as const;', content)
    assert match, "Could not find `languages` definition in LanguageContext.tsx"

    raw_langs = match.group(1)
    langs = [lang.strip().strip('"\'') for lang in raw_langs.split(",") if lang.strip()]
    expected_langs = ["en", "hi", "kn", "ta", "te"]
    assert set(langs) == set(expected_langs), f"Expected {expected_langs}, got {langs}"


def test_storage_key_definition():
    content = LANG_CONTEXT_FILE.read_text(encoding="utf-8")
    assert 'specwise_lang' in content, "Storage key 'specwise_lang' must be defined for persistence"


def test_dictionary_completeness_across_all_languages():
    content = LANG_CONTEXT_FILE.read_text(encoding="utf-8")

    # Extract english dictionary keys
    eng_match = re.search(r'export const english:\s*Translations\s*=\s*\{(.*?)\n\};\s*export const dictionary', content, re.DOTALL)
    assert eng_match, "Could not extract english translations dictionary"
    eng_keys = set(re.findall(r'^\s*([A-Za-z0-9_]+)\s*:\s*["\'`]', eng_match.group(1), re.MULTILINE))
    assert len(eng_keys) >= 50, f"Expected comprehensive english dictionary, found only {len(eng_keys)} keys"

    # Verify each language dictionary contains entries and has english fallback
    for lang in ["hi", "kn", "ta", "te"]:
        dict_match = re.search(rf'\b{lang}:\s*\{{([^}}]+)\}}', content)
        assert dict_match, f"Missing dictionary entry for language '{lang}'"
        has_fallback_spread = "...english" in dict_match.group(1)
        lang_keys = set(re.findall(r'^\s*([A-Za-z0-9_]+)\s*:\s*["\'`]', dict_match.group(1), re.MULTILINE))

        if not has_fallback_spread:
            missing_keys = eng_keys - lang_keys
            assert not missing_keys, f"Language '{lang}' is missing keys: {missing_keys}"


def test_navbar_renders_all_supported_languages():
    navbar_content = NAVBAR_FILE.read_text(encoding="utf-8")
    for lang in ["en", "hi", "kn", "ta", "te"]:
        assert f'code: "{lang}"' in navbar_content or f'"{lang}":' in navbar_content, (
            f"Navbar must include language code '{lang}' in selection list"
        )


def test_proxy_symbol_and_fallback_guard_present():
    content = LANG_CONTEXT_FILE.read_text(encoding="utf-8")
    # Must guard against non-string symbol accesses
    assert 'typeof prop !== "string"' in content, (
        "Proxy handler must safely delegate non-string/Symbol properties to target"
    )
    # Must fallback to english
    assert 'english[prop]' in content or 'english[key]' in content, (
        "Translation proxy must fall back to english for missing keys"
    )


def test_backend_api_is_independent_of_ui_language():
    """Verify backend endpoints and schemas do not have tight coupling to UI language."""
    from app.models import AnalysisRequest, StandardRecord
    # Verify AnalysisRequest does not mandate UI language
    req = AnalysisRequest(text="openwell submersible pumpset 5 HP")
    assert req.text == "openwell submersible pumpset 5 HP"
    assert hasattr(req, "query_language") is False or req.query_language is None
