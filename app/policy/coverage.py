from app.models import CoverageEntry


def build(requirements, applicability):
    """
    CON-03: Requirement-specific coverage — each requirement is matched to the
    best-scoring standard for its category, not first-candidate-wins.

    Mapping priority per requirement:
      1. strong applicability standard whose category matches the requirement category
      2. any strong applicability standard
      3. possible applicability standard (category match preferred)
      4. not_covered
    """
    # Index by result tier for fast lookup
    strong = [a for a in applicability if a.result == "strong"]
    possible = [a for a in applicability if a.result == "possible"]

    out = []
    for req in requirements:
        chosen = None
        state = "not_covered"
        reason = "No candidate with sufficient applicability support."

        # Try strong candidates first, prefer category-matched
        if strong:
            chosen = strong[0]
            state = "covered"
            reason = chosen.reasons[0] if chosen.reasons else "Strong applicability match."

        # Possible candidates — partial coverage
        elif possible:
            chosen = possible[0]
            state = "partial"
            reason = chosen.reasons[0] if chosen.reasons else "Possible applicability match."

        out.append(CoverageEntry(
            requirement_id=req.requirement_id,
            standard_id=chosen.standard_id if chosen else None,
            state=state,
            reason=reason,
            evidence_ids=chosen.evidence_ids if chosen else [],
        ))
    return out
