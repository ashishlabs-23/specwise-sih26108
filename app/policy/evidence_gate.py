def route(candidates, applicability, lifecycle, coverage, conflicts, by_id=None):
    """
    Role-aware routing. Key changes from previous version:

    - 'strong' now means a PRIMARY_PRODUCT_STANDARD scored strongly.
      CODE_OF_PRACTICE/TEST_METHOD are capped at 'possible' in applicability,
      so they never generate false RECOMMEND collisions.
    - REVIEW reasons are specific to their actual cause.
    - ABSTAIN distinguishes 'only related/CoP candidates' from 'no signal at all'.
    """
    if not candidates:
        return "OUT_OF_CORPUS", [
            "No candidate standard in the prototype corpus scored above the "
            "relevance floor for this query. The input domain is likely outside "
            "the current curated seed corpus."
        ]

    by_id = by_id or {}
    gaps = [x for x in coverage if x.state == "not_covered"]
    strong = [x for x in applicability if x.result == "strong"]
    possible = [x for x in applicability if x.result == "possible"]

    # ── Classify strong candidates by role ────────────────────────────────────
    strong_primary = [
        a for a in strong
        if by_id.get(a.standard_id) and
           getattr(by_id[a.standard_id], "standard_role", "PRIMARY_PRODUCT_STANDARD")
           == "PRIMARY_PRODUCT_STANDARD"
    ]
    # (strong non-primary is impossible given role ceiling, but guard anyway)

    # ── RECOMMEND ─────────────────────────────────────────────────────────────
    if len(strong_primary) == 1 and not gaps and not conflicts:
        std_id = strong_primary[0].standard_id
        item = next((x for x in lifecycle if x.standard_id == std_id), None)
        if item and item.state == "supported":
            return "RECOMMEND", [
                f"Single primary product standard ({std_id}) scored strong "
                "applicability and passed all prototype evidence gates: "
                "no coverage gaps, no conflicts, lifecycle supported."
            ]

    # ── REVIEW: collect specific per-trigger reasons ───────────────────────────
    review_reasons = []

    if len(strong_primary) > 1:
        ids = ", ".join(x.standard_id for x in strong_primary)
        review_reasons.append(
            f"Multiple primary product standards scored strong ({ids}). "
            "Human disambiguation required — check product terms in the query."
        )

    if gaps:
        gap_ids = ", ".join(x.requirement_id for x in gaps)
        review_reasons.append(
            f"Insufficient product attributes: requirements [{gap_ids}] "
            "could not be covered by any candidate in the prototype corpus."
        )

    if conflicts:
        descs = "; ".join(x.description for x in conflicts)
        review_reasons.append(f"Standard conflicts detected: {descs}")

    lc_warnings = [
        x for x in lifecycle
        if x.standard_id in {s.standard_id for s in strong_primary}
        and x.state == "warning"
    ]
    if lc_warnings:
        lc_ids = ", ".join(x.standard_id for x in lc_warnings)
        review_reasons.append(
            f"Lifecycle warning on primary candidate(s): {lc_ids}. "
            "Verify current edition status before procurement."
        )

    if review_reasons:
        return "REVIEW", review_reasons

    # ── ABSTAIN: candidates exist but no primary standard scored strong ────────
    only_cop = (
        possible and
        all(
            getattr(by_id.get(a.standard_id), "standard_role", "PRIMARY_PRODUCT_STANDARD")
            in {"CODE_OF_PRACTICE", "TEST_METHOD", "RELATED_STANDARD"}
            for a in possible
        )
    )

    if only_cop:
        cop_ids = ", ".join(a.standard_id for a in possible)
        return "ABSTAIN", [
            f"Only related/code-of-practice standards ({cop_ids}) matched the query. "
            "No primary product standard in the prototype corpus covers this input. "
            "SOURCE ACCESS RESTRICTED — DETAILS NOT VERIFIED for these candidates."
        ]

    if not strong and not possible:
        return "ABSTAIN", [
            "No standard in the prototype corpus produced a sufficient applicability "
            "signal for this query. Evidence in the corpus is insufficient for a "
            "defensible recommendation. SOURCE ACCESS RESTRICTED — DETAILS NOT VERIFIED."
        ]

    return "ABSTAIN", [
        "Candidates were retrieved but available evidence in the prototype corpus "
        "is insufficient for a defensible recommendation. "
        "SOURCE ACCESS RESTRICTED — DETAILS NOT VERIFIED."
    ]
