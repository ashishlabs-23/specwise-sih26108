from app.models import ConflictRecord


def detect(candidates_ids: list[str], applicability, lifecycle, by_id: dict):
    """
    CON-06: Detects two classes of conflicts:
      1. lifecycle_warning  — standard has a lifecycle warning event (existing behaviour)
      2. standard_conflict  — two candidates that both appear in each other's
                              conflicts_with list (data-driven, no BIS facts invented)

    The StandardRecord 'conflicts_with' field is optional; if absent or empty,
    no standard-vs-standard conflict is raised.
    """
    rows = []

    # --- 1. Lifecycle warnings (existing) ---
    for item in lifecycle:
        if item.state == "warning":
            rows.append(ConflictRecord(
                conflict_type="lifecycle_warning",
                description=(
                    f"{item.standard_id}: {' '.join(item.reasons)}"
                ),
                evidence_ids=item.evidence_ids,
            ))

    # --- 2. Standard-vs-standard conflicts (data-driven) ---
    seen_pairs: set[frozenset] = set()
    for sid in candidates_ids:
        standard = by_id.get(sid)
        if standard is None:
            continue
        conflicts_with = getattr(standard, "conflicts_with", []) or []
        for other_id in conflicts_with:
            pair = frozenset({sid, other_id})
            if pair in seen_pairs:
                continue
            # Only flag if the conflicting standard is also a candidate
            if other_id in candidates_ids:
                seen_pairs.add(pair)
                other = by_id.get(other_id)
                evidence = list(set(
                    getattr(standard, "evidence_ids", []) +
                    (getattr(other, "evidence_ids", []) if other else [])
                ))
                rows.append(ConflictRecord(
                    conflict_type="standard_conflict",
                    description=(
                        f"{sid} and {other_id} are annotated as conflicting in the "
                        "corpus (conflicts_with relationship). Human review required."
                    ),
                    evidence_ids=evidence,
                ))

    return rows
