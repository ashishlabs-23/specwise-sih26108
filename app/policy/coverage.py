import re
from typing import Optional
from app.models import CoverageEntry

# Regex to extract the bare IS number from a requirement value field.
# Matches "IS 8034", "IS 8034:2018", "IS 694", etc.
_IS_NUM_RE = re.compile(r"IS\s*(\d{3,6})", re.I)
_YEAR_RE = re.compile(r"\b(19\d\d|20\d\d)\b")


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
    text.  Uses the global result tier as the base; within the same tier,
    prefers candidates whose matched terms actually appear in this requirement.

    Returns:
        3  strong result AND at least one matched term overlaps req_text
        2  strong result but no matched term overlaps this requirement's text
        1  possible result (regardless of term overlap)
        0  weak or unknown
    """
    result = assessment.result
    if result == "strong":
        relevant = any(
            term.lower() in req_text_lower
            for reason in assessment.reasons
            for term in _extract_matched_terms(reason)
        )
        return 3 if relevant else 2
    if result == "possible":
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

        # Score every candidate against this specific requirement
        scored = sorted(
            ((a, _score_for_req(a, req_text_lower)) for a in applicability),
            key=lambda x: x[1],
            reverse=True,
        )
        best, score = scored[0]
        _append_entry(out, req, best, score)

    return out
