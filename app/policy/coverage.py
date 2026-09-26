import re
from typing import Optional
from app.models import CoverageEntry

# Regex to extract the bare IS number from a requirement value field.
# Matches "IS 8034", "IS 8034:2018", "IS 694", etc.
_IS_NUM_RE = re.compile(r"IS\s*(\d{3,6})", re.I)
_YEAR_RE = re.compile(r"\b(19\d\d|20\d\d)\b")
_ITEM_PREFIX_RE = re.compile(r"^\s*(?:[-*•]\s*)?item\s+\d+\s*[:.)-]", re.I)
_NUMBERED_METRIC_ITEM_RE = re.compile(r"^\s*\d+[.)]\s+\d+(?:\.\d+)?\s*(?:w|kw|kwp|mw|hp|kva|v|kv|mm|cm|m)\b", re.I)
_LABELED_COMPONENT_RE = re.compile(r"^\s*[-*•]\s*([A-Za-z][A-Za-z0-9 /()-]{1,32})\s*:")
_CONTEXT_LABELS = {"scope", "scope of work", "application", "standard", "standard compliance", "power", "power rating", "head range", "discharge", "rated power"}


def _is_number_in(standard_id: str, is_value: str) -> bool:
    """Return True when the bare IS number from is_value appears in standard_id."""
    m = _IS_NUM_RE.search(is_value)
    if not m:
        return False
    return m.group(1) in standard_id


def _extract_year(s: str) -> Optional[str]:
    """Extract 4-digit year from standard identifier or citation string."""
    m = _YEAR_RE.search(s)
    return m.group(1) if m else None


def _extract_matched_terms(reason: str) -> list[str]:
    """Pull quoted terms out of an applicability reason string."""
    return re.findall(r"'([^']+)'", reason)


def _score_for_req(assessment, req_text_lower: str) -> int:
    """
    Score a pre-computed ApplicabilityAssessment against a single requirement's
    text. Uses term overlap to establish requirement-specific relevance.

    Returns:
        3  strong result AND at least one matched term overlaps req_text -> covered
        1  possible result AND at least one matched term overlaps req_text -> partial
        0  no term overlap, weak, or unknown -> not_covered
    """
    relevant = any(
        term.lower() in req_text_lower
        for reason in assessment.reasons
        for term in _extract_matched_terms(reason)
    )
    if not relevant:
        return 0

    if assessment.result == "strong":
        return 3
    if assessment.result == "possible":
        return 1
    return 0


def _append_entry(out: list, req, assessment, score: int) -> None:
    """Translate numeric score to coverage state and append a CoverageEntry."""
    if score >= 3:
        state = "covered"
        reason = assessment.reasons[0] if assessment.reasons else "Strong applicability match."
    elif score >= 1:
        state = "partial"
        reason = (
            assessment.reasons[0] if assessment.reasons
            else "Possible applicability match — full coverage not established."
        )
    else:
        state = "not_covered"
        reason = "No candidate with sufficient applicability support for this requirement."

    out.append(CoverageEntry(
        requirement_id=req.requirement_id,
        standard_id=assessment.standard_id,
        state=state,
        reason=reason,
        evidence_ids=assessment.evidence_ids,
    ))


def build(requirements, applicability):
    """
    Requirement-specific coverage with unverified reference and currentness / edition mismatch handling.

    Every requirement is evaluated independently.  A single strong primary
    candidate DOES NOT automatically cover all requirements.

    Requirement categories
    ----------------------
    ``reference`` (IS-number citations extracted from the tender):
        • If NO corpus candidate matches the cited IS number:
          -> ``unverified_reference`` (standard_id=None, preserves cited string).
        • If a corpus candidate matches the IS number:
          -> Compare cited edition/year with corpus standard edition.
             If mismatch (e.g. cited IS 694:1990 vs corpus IS 694:2010):
             -> ``edition_mismatch`` (preserves cited edition, identifies corpus edition).
             If editions match or no edition cited:
             -> evaluate applicability score and append covered/partial.

    All other categories:
        Score every ApplicabilityAssessment against this requirement's text
        individually and pick the best-scoring one.

        score 3  (strong + term overlap) → ``covered``
        score 2  (strong, no overlap)    → ``partial``
        score 1  (possible)              → ``partial``
        score 0  (weak / unknown)        → ``not_covered``
    """
    out: list = []
    strong = [a for a in applicability if a.result == "strong"]

    def product_term_matches(assessment, req_text_lower):
        return any(
            term.lower() in req_text_lower
            for reason in assessment.reasons
            if reason.startswith("Product term matched:")
            for term in _extract_matched_terms(reason)
        )

    def explicit_item_clause(req_text):
        if _ITEM_PREFIX_RE.search(req_text) or _NUMBERED_METRIC_ITEM_RE.search(req_text):
            return True
        label = _LABELED_COMPONENT_RE.match(req_text)
        return bool(label and label.group(1).strip().lower() not in _CONTEXT_LABELS)

    for req in requirements:
        req_text_lower = req.text.lower()

        # ── IS-reference requirements ────────────────────────────────────────
        if req.category == "reference" and req.attribute == "is_number" and req.value:
            cited = req.value  # e.g. "IS 13947", "IS 694:1990", "IS 8034:2018"

            # Candidates that match the cited IS number
            matching = [
                a for a in applicability
                if _is_number_in(a.standard_id, cited)
            ]

            if not matching:
                # Cited IS number is absent from the corpus
                out.append(CoverageEntry(
                    requirement_id=req.requirement_id,
                    standard_id=None,
                    state="unverified_reference",
                    reason=(
                        f"Tender cites {cited!r} which is not present in "
                        "the prototype corpus. Coverage cannot be verified."
                    ),
                    evidence_ids=[],
                ))
                continue

            # Cited IS IS in the corpus — pick the highest-scoring match
            best = max(matching, key=lambda a: _score_for_req(a, req_text_lower))
            
            # Check for edition / currentness mismatch
            cited_year = _extract_year(cited)
            corpus_year = _extract_year(best.standard_id)
            if cited_year and corpus_year and cited_year != corpus_year:
                out.append(CoverageEntry(
                    requirement_id=req.requirement_id,
                    standard_id=best.standard_id,
                    state="edition_mismatch",
                    reason=(
                        f"Tender cites historical/cited edition {cited!r}, but corpus contains "
                        f"current edition '{best.standard_id}'. Edition revision and technical parameter differences must be reviewed."
                    ),
                    evidence_ids=best.evidence_ids,
                ))
                continue

            if best.result == "strong":
                _append_entry(out, req, best, 3)
            else:
                _append_entry(out, req, best, _score_for_req(best, req_text_lower))
            continue

        # ── All other requirement categories ─────────────────────────────────
        if not applicability:
            out.append(CoverageEntry(
                requirement_id=req.requirement_id,
                standard_id=None,
                state="not_covered",
                reason="No candidate standards available.",
                evidence_ids=[],
            ))
            continue

        # Scope/admin prose extracted from a tender is not itself a technical
        # procurement requirement. Keep separately labeled item/component
        # clauses visible as gaps; unlabelled prose becomes relevant only when
        # it carries the candidate's actual product discriminator.
        direct = [a for a in applicability if product_term_matches(a, req_text_lower)]
        if direct:
            best = max(direct, key=lambda a: (a.result == "strong", a.result == "possible"))
            _append_entry(out, req, best, 3 if best.result == "strong" else _score_for_req(best, req_text_lower))
            continue

        if req.category == "performance" and strong and not explicit_item_clause(req.text):
            _append_entry(out, req, strong[0], 3)
            continue

        if req.category == "product" and not explicit_item_clause(req.text):
            continue

        # Score every candidate against this specific requirement
        scored = sorted(
            ((a, _score_for_req(a, req_text_lower)) for a in applicability),
            key=lambda x: x[1],
            reverse=True,
        )
        best, score = scored[0]
        _append_entry(out, req, best, score)

    return out
