from app.models import ApplicabilityAssessment

# Role-based score ceiling: CODE_OF_PRACTICE / TEST_METHOD / RELATED_STANDARD
# can never be "strong" as a primary product recommendation.
_ROLE_CEILING = {
    "PRIMARY_PRODUCT_STANDARD": "strong",
    "CODE_OF_PRACTICE": "possible",
    "TEST_METHOD": "possible",
    "RELATED_STANDARD": "weak",
}

_RESULT_ORDER = ["unknown", "weak", "possible", "strong"]


def _cap(result: str, ceiling: str) -> str:
    ri, ci = _RESULT_ORDER.index(result), _RESULT_ORDER.index(ceiling)
    return _RESULT_ORDER[min(ri, ci)]


def _phrases_in(phrases: list[str], text: str) -> list[str]:
    """Return phrases that appear verbatim in text (case-insensitive)."""
    return [p for p in phrases if p.lower() in text]


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
    req_text = " ".join(r.text for r in requirements).lower()
    score = 0
    reasons: list[str] = []
    excluded = False

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

    # ── 6. Apply role ceiling ─────────────────────────────────────────────────
    role = getattr(standard, "standard_role", "PRIMARY_PRODUCT_STANDARD")
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
