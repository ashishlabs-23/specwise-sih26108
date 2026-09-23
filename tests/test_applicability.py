import pytest
from app.models import StandardRecord, Requirement
from app.policy.applicability import assess

# ── Shared fixtures ───────────────────────────────────────────────────────────

def _std(sid, title, scope, role, product_terms, app_terms, exclusion_terms, keywords, evidence_ids=None):
    return StandardRecord(
        standard_id=sid, title=title, scope=scope, category="pumps",
        standard_role=role,
        product_terms=product_terms,
        application_terms=app_terms,
        exclusion_terms=exclusion_terms,
        keywords=keywords,
        evidence_ids=evidence_ids or ["E-DUMMY"],
    )


def _req(text):
    return [Requirement(requirement_id="R1", category="product", text=text)]


IS_14220 = _std(
    "IS 14220:2018", "Openwell Submersible Pumpsets",
    "Openwell submersible pumpsets for clear, cold water.",
    "PRIMARY_PRODUCT_STANDARD",
    product_terms=["openwell", "open well"],
    app_terms=["agriculture", "irrigation", "water supply"],
    exclusion_terms=["borewell", "borehole", "tubewell", "monoset", "installation", "maintenance"],
    keywords=["openwell", "submersible", "pumpset", "agriculture", "irrigation"],
)

IS_8034 = _std(
    "IS 8034:2018", "Submersible Pumpsets",
    "Submersible pumpsets for boreholes/borewells/tubewells.",
    "PRIMARY_PRODUCT_STANDARD",
    product_terms=["submersible pumpset", "submersible pump"],
    app_terms=["borewell", "borehole", "tubewell", "agriculture", "water supply"],
    exclusion_terms=["openwell", "monoset", "installation", "maintenance"],
    keywords=["submersible", "pumpset", "borewell", "agriculture"],
)

IS_9079 = _std(
    "IS 9079:2018", "Monoset Pumps",
    "Monoset pumps for clear, cold water for agricultural and water supply.",
    "PRIMARY_PRODUCT_STANDARD",
    product_terms=["monoset", "monoset pump"],
    app_terms=["agriculture", "water supply", "clear water", "cold water"],
    exclusion_terms=[],  # no evidence-supported exclusions
    keywords=["monoset", "pump", "agriculture", "water supply"],
)

IS_14536 = _std(
    "IS 14536:2018", "Selection, Installation, Operation and Maintenance of Submersible Pumpset — CoP",
    "Code of practice for selection, installation, operation and maintenance.",
    "CODE_OF_PRACTICE",
    product_terms=[],
    app_terms=["selection", "installation", "operation", "maintenance"],
    exclusion_terms=[],
    keywords=["submersible", "pumpset", "installation", "maintenance"],
)


# ── Applicability unit tests ──────────────────────────────────────────────────

class TestOpenwell:
    def test_strong_on_openwell_query(self):
        r = assess(IS_14220, _req("openwell submersible pumpset for agricultural irrigation"))
        assert r.result == "strong", f"Expected strong, got {r.result}. Reasons: {r.reasons}"

    def test_excluded_when_borewell_in_query(self):
        r = assess(IS_14220, _req("submersible pumpset for a borewell"))
        assert r.result in {"weak", "unknown"}, \
            f"IS 14220 should be excluded for borewell query; got {r.result}"

    def test_excluded_when_monoset_in_query(self):
        r = assess(IS_14220, _req("monoset pump for agriculture"))
        assert r.result in {"weak", "unknown"}


class TestBorewellSubmersible:
    def test_strong_on_borewell_query(self):
        r = assess(IS_8034, _req("submersible pumpset for a borewell supplying agricultural water"))
        assert r.result == "strong", f"Expected strong, got {r.result}. Reasons: {r.reasons}"

    def test_excluded_when_openwell_in_query(self):
        r = assess(IS_8034, _req("openwell submersible pumpset for irrigation"))
        assert r.result in {"weak", "unknown"}, \
            f"IS 8034 should be excluded for openwell query; got {r.result}"


class TestMonoset:
    def test_strong_on_monoset_query(self):
        r = assess(IS_9079, _req("monoset pump for clear cold water for agriculture"))
        assert r.result == "strong", f"Expected strong, got {r.result}. Reasons: {r.reasons}"

    def test_not_strong_on_non_monoset_query(self):
        """IS 9079 has no evidence-supported exclusion_terms.
        A submersible pumpset query has no monoset product_term match, so IS 9079
        must not score 'strong' — it will score at most 'possible' via keyword overlap."""
        r = assess(IS_9079, _req("submersible pumpset for borewell water supply"))
        assert r.result in {"possible", "weak", "unknown"}, \
            f"IS 9079 should not be 'strong' for a non-monoset query; got {r.result}"


class TestCodeOfPractice:
    def test_cop_never_strong(self):
        """IS 14536 is CODE_OF_PRACTICE — role ceiling prevents strong."""
        r = assess(IS_14536, _req("submersible pumpset for borewell agriculture irrigation"))
        assert r.result in {"possible", "weak", "unknown"}, \
            f"CODE_OF_PRACTICE must not be 'strong'; got {r.result}"

    def test_cop_role_ceiling_applies(self):
        """CODE_OF_PRACTICE must always be at most 'possible', never 'strong'.
        The ceiling may be applied silently (raw already ≤ possible) or explicitly."""
        r = assess(IS_14536, _req("submersible pumpset installation for agriculture"))
        assert r.result in {"possible", "weak", "unknown"}, \
            f"CODE_OF_PRACTICE must not be 'strong'; got {r.result}. Reasons: {r.reasons}"


class TestNoEvidence:
    def test_no_evidence_caps_at_possible(self):
        std = _std(
            "IS TEST:2024", "Test Standard", "Test scope",
            "PRIMARY_PRODUCT_STANDARD",
            product_terms=["test product"],
            app_terms=["agriculture"],
            exclusion_terms=[],
            keywords=["test"],
            evidence_ids=[],  # intentionally empty — no verified evidence
        )
        # _std helper passes evidence_ids=[] because we override it:
        std = std.model_copy(update={"evidence_ids": []})
        r = assess(std, _req("test product for agriculture"))
        assert r.result in {"possible", "weak", "unknown"}, \
            f"No-evidence standard must not reach 'strong'; got {r.result}"
        assert any("SOURCE ACCESS RESTRICTED" in reason for reason in r.reasons)
