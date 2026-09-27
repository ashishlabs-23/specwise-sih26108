from app.models import ApplicabilityAssessment
import re

# Role-based score ceiling: CODE_OF_PRACTICE / TEST_METHOD / RELATED_STANDARD
# can never be "strong" as a primary product recommendation.
_ROLE_CEILING = {
    "PRIMARY_PRODUCT_STANDARD": "strong",
    "CODE_OF_PRACTICE": "possible",
    "TEST_METHOD": "possible",
    "RELATED_STANDARD": "weak",
}

_RESULT_ORDER = ["unknown", "weak", "possible", "strong"]
_GENERIC_SUBMERSIBLE_PRODUCT_TERMS = {"submersible pump", "submersible pumpset"}


def _normalize_product_wording(value: str) -> str:
    """Normalize spelling variants while keeping openwell and borewell distinct."""
    value = re.sub(r"\b(open|bore)[\s-]*well\b", r"\1well", value, flags=re.I)
    value = re.sub(r"\bpump\s+sets?\b", "pumpset", value, flags=re.I)
    value = re.sub(r"\bpumpsets\b", "pumpset", value, flags=re.I)
    return re.sub(r"\s+", " ", value).strip().lower()


def _cap(result: str, ceiling: str) -> str:
    ri, ci = _RESULT_ORDER.index(result), _RESULT_ORDER.index(ceiling)
    return _RESULT_ORDER[min(ri, ci)]


def _phrases_in(phrases: list[str], text: str) -> list[str]:
    """Return phrases that appear verbatim in text (case-insensitive)."""
    text = _normalize_product_wording(text)
    hits = []
    for phrase in phrases:
        normalized_phrase = _normalize_product_wording(phrase)
        if normalized_phrase in text:
            hits.append(phrase)
            continue
        if normalized_phrase in {"borewell", "borehole", "tubewell"} and re.search(r"\bdeep\s+well\b", text, re.I):
            hits.append(phrase)
            continue
        # Pump product names tolerate intervening well descriptors and spacing
        # variants ("deep well ... pump set") while preserving the product noun.
        if re.search(r"submersible\s+(?:[a-z-]+\s+){0,3}pumps?\s*sets?", phrase, re.I):
            if re.search(r"\bsubmersible\b(?:\s+[a-z-]+){0,3}\s+\bpumps?\s*sets?\b", text, re.I):
                hits.append(phrase)
                continue
            if re.search(r"\bdeep\s+well\s+submersible\s+pumps?\s+sets?\b", text, re.I):
                hits.append(phrase)
                continue
            if re.search(r"\bborewell\s+submersible\s+pumps?\s*sets?\b", text, re.I):
                hits.append(phrase)
    return hits


def _has_current_exact_reference(standard, requirements) -> bool:
    """Return whether the tender explicitly cites this record's current ID."""
    target = standard.standard_id.upper().replace(" ", "")
    for req in requirements:
        if req.category != "reference" or not req.value:
            continue
        citation = req.value.upper().replace(" ", "")
        if citation == target:
            return True
    return False


def assess(standard, requirements) -> ApplicabilityAssessment:
    """
    Role-aware, data-driven applicability scoring.

    Scoring layers (highest-signal first):

    1. EXCLUSION check — if any exclusion_term matches the query, cap at 'weak'
       and record the reason.

    2. PRODUCT_TERMS match — +5 per product_term found in query text (these are
       strong discriminating terms like 'openwell', 'monoset pumpset').

    3. APPLICATION_TERMS match — +2 per application_term found (agriculture,
       borewell, irrigation, etc.).

    4. KEYWORD match — +1 per general keyword found (broader vocabulary).

    5. ROLE CEILING — CODE_OF_PRACTICE / TEST_METHOD can at most be 'possible'.

    6. EVIDENCE guard — standards with no loaded evidence are capped at 'possible'.
    """
    req_text = _normalize_product_wording(" ".join(r.text for r in requirements))
    score = 0
    reasons: list[str] = []
    excluded = False
    app_hits: list[str] = []

    # ── 1. Exclusion terms ────────────────────────────────────────────────────
    exclusion_hits = _phrases_in(getattr(standard, "exclusion_terms", []), req_text)
    if exclusion_hits:
        excluded = True
        reasons.append(
            f"Exclusion signal: query contains '{', '.join(exclusion_hits)}' "
            f"which is outside the scope of {standard.standard_id}."
        )

    if not excluded:
        # ── 2. Product terms (strongest signal) ──────────────────────────────
        product_hits = _phrases_in(getattr(standard, "product_terms", []), req_text)
        for pt in product_hits:
            score += 5
            reasons.append(f"Product term matched: '{pt}'")

        # ── 3. Application terms ──────────────────────────────────────────────
        app_hits = _phrases_in(getattr(standard, "application_terms", []), req_text)
        for at in app_hits:
            score += 2
            reasons.append(f"Application term matched: '{at}'")

        # ── 4. General keywords ───────────────────────────────────────────────
        for kw in standard.keywords:
            if kw.lower() in req_text:
                score += 1
                reasons.append(f"Keyword matched: '{kw}'")

    # ── 5. Raw result before role ceiling ────────────────────────────────────
    raw_result = (
        "strong"   if score >= 8 else
        "possible" if score >= 3 else
        "weak"     if score >= 1 else
        "unknown"
    )
    if excluded:
        raw_result = "weak"

    # A record with declared product terms must match at least one of those
    # terms before broad application/keyword overlap can make it a strong
    # primary candidate (for example, clear water terms cannot make a monoset
    # standard strong for an openwell pump).
    product_terms = getattr(standard, "product_terms", [])
    product_hits = _phrases_in(product_terms, req_text)
    if product_terms and not excluded and not product_hits:
        raw_result = _cap(raw_result, "possible")
        reasons.append(
            "Product discriminator not matched: broad application or keyword overlap "
            "cannot establish a strong match for this product standard."
        )

    # Generic submersible wording is useful retrieval context but does not
    # distinguish the competing openwell and borewell primary families. A
    # current exact tender citation may anchor a generic product only when no
    # exclusion contradicts it. Historical citations remain review signals.
    generic_hits = {
        _normalize_product_wording(term)
        for term in product_hits
        if _normalize_product_wording(term) in _GENERIC_SUBMERSIBLE_PRODUCT_TERMS
    }
    family_hits = [
        term for term in product_hits
        if _normalize_product_wording(term) not in _GENERIC_SUBMERSIBLE_PRODUCT_TERMS
    ]
    family_hits.extend(
        term for term in app_hits
        if "well" in _normalize_product_wording(term)
    )
    current_reference = _has_current_exact_reference(standard, requirements)
    role = getattr(standard, "standard_role", "PRIMARY_PRODUCT_STANDARD")
    if (
        role == "PRIMARY_PRODUCT_STANDARD"
        and generic_hits
        and not family_hits
        and not current_reference
        and not excluded
    ):
        raw_result = _cap(raw_result, "possible")
        reasons.append(
            "Generic submersible product wording is not sufficient to select a "
            "primary family; a family-specific well discriminator or compatible "
            "current tender citation is required."
        )

    # ── 6. Apply role ceiling ─────────────────────────────────────────────────
    ceiling = _ROLE_CEILING.get(role, "strong")
    final_result = _cap(raw_result, ceiling)
    if final_result != raw_result:
        reasons.append(
            f"Role ceiling applied: standard_role='{role}' limits applicability "
            f"to at most '{ceiling}' (was '{raw_result}')."
        )

    # ── 7. Evidence guard ────────────────────────────────────────────────────
    if not standard.evidence_ids:
        final_result = _cap(final_result, "possible")
        reasons.append(
            "SOURCE ACCESS RESTRICTED — DETAILS NOT VERIFIED: "
            "no evidence loaded; applicability capped at 'possible'."
        )

    return ApplicabilityAssessment(
        standard_id=standard.standard_id,
        result=final_result,
        reasons=reasons or ["No applicability signal matched."],
        evidence_ids=standard.evidence_ids,
    )
