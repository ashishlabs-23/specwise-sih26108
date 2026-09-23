"""
Tests for the verified demo corpus:
- New standards (IS 9283, IS 11346, IS 10572) loaded correctly
- Relationship records verified and traversable
- Graph expansion surfaces normative references from IS 8034
- QCO/certification handling (proposed, not verified = not_verified state)
- Lifecycle: revision_under_print does not block RECOMMEND
- IS-number explicit lookup
- Related/test standards not driving RECOMMEND decisions
"""
import pytest
from app.engine import RecommendationEngine
from app.models import AnalysisRequest
from app.storage.repository import JsonRepository


@pytest.fixture(scope="module")
def repo():
    return JsonRepository("data")


@pytest.fixture(scope="module")
def engine():
    return RecommendationEngine()


# ── Corpus integrity ──────────────────────────────────────────────────────────

class TestCorpusIntegrity:
    def test_new_standards_loaded(self, repo):
        ids = {s.standard_id for s in repo.standards}
        for sid in ["IS 9283:2024", "IS 11346:2002", "IS 10572:1983"]:
            assert sid in ids, f"Expected {sid} in corpus"

    def test_all_standards_have_evidence(self, repo):
        ev_ids = {e.evidence_id for e in repo.evidence}
        for s in repo.standards:
            for eid in s.evidence_ids:
                assert eid in ev_ids, \
                    f"{s.standard_id}: evidence_id '{eid}' not found in evidence records"

    def test_relationships_loaded(self, repo):
        assert len(repo.relationships) >= 5, \
            f"Expected at least 5 relationships, got {len(repo.relationships)}"

    def test_relationship_references_exist(self, repo):
        std_ids = {s.standard_id for s in repo.standards}
        for rel in repo.relationships:
            assert rel.from_standard in std_ids, \
                f"Relationship from_standard '{rel.from_standard}' not in standards"
            assert rel.to_standard in std_ids, \
                f"Relationship to_standard '{rel.to_standard}' not in standards"

    def test_roles_assigned(self, repo):
        by_id = {s.standard_id: s for s in repo.standards}
        assert by_id["IS 14536:2018"].standard_role == "CODE_OF_PRACTICE"
        assert by_id["IS 9283:2024"].standard_role == "RELATED_STANDARD"
        assert by_id["IS 11346:2002"].standard_role == "TEST_METHOD"
        assert by_id["IS 10572:1983"].standard_role == "TEST_METHOD"
        assert by_id["IS 8034:2018"].standard_role == "PRIMARY_PRODUCT_STANDARD"


# ── Graph expansion ───────────────────────────────────────────────────────────

class TestGraphExpansion:
    def test_borewell_query_expands_to_normative_refs(self, engine):
        """IS 8034 query should expand to IS 9283, IS 14536, IS 11346 at hop=1."""
        r = engine.analyze(
            AnalysisRequest(text="submersible pumpsets for a borewell supplying agricultural water")
        )
        related_ids = {x.to_standard for x in r.related_standards}
        assert "IS 9283:2024" in related_ids, \
            f"IS 9283:2024 must be a hop-1 normative reference of IS 8034; got {related_ids}"
        assert "IS 14536:2018" in related_ids, \
            f"IS 14536:2018 must be a hop-1 normative reference of IS 8034; got {related_ids}"
        assert "IS 11346:2002" in related_ids, \
            f"IS 11346:2002 must be a hop-1 test_method reference of IS 8034; got {related_ids}"

    def test_related_standards_have_hop_distance(self, engine):
        """All expanded relationships must carry their hop distance."""
        r = engine.analyze(
            AnalysisRequest(text="submersible pumpsets for a borewell supplying agricultural water")
        )
        for rel in r.related_standards:
            assert rel.hop in {1, 2}, \
                f"Relationship {rel.from_standard}->{rel.to_standard} missing hop; got {rel.hop}"

    def test_monoset_query_expands_to_test_method(self, engine):
        """IS 9079 query should expand to IS 11346 (shared test method via MED20)."""
        r = engine.analyze(
            AnalysisRequest(text="monoset pump for clear cold water for agriculture")
        )
        related_ids = {x.to_standard for x in r.related_standards}
        assert "IS 11346:2002" in related_ids, \
            f"IS 11346:2002 must be a test_method reference of IS 9079; got {related_ids}"


# ── Related/test standards do not drive primary recommendation ────────────────

class TestRelatedStandardsRole:
    def test_test_method_not_strong(self, engine):
        """IS 11346 (TEST_METHOD) must not score 'strong' applicability."""
        r = engine.analyze(
            AnalysisRequest(text="submersible pumpsets for a borewell supplying agricultural water")
        )
        strong_ids = {a.standard_id for a in r.applicability if a.result == "strong"}
        assert "IS 11346:2002" not in strong_ids, \
            f"TEST_METHOD IS 11346:2002 must not be strong; got strong={strong_ids}"

    def test_related_standard_not_strong(self, engine):
        """IS 9283 (RELATED_STANDARD) must not score 'strong' applicability."""
        r = engine.analyze(
            AnalysisRequest(text="submersible pumpsets for a borewell supplying agricultural water")
        )
        strong_ids = {a.standard_id for a in r.applicability if a.result == "strong"}
        assert "IS 9283:2024" not in strong_ids, \
            f"RELATED_STANDARD IS 9283:2024 must not be strong; got strong={strong_ids}"


# ── Lifecycle ─────────────────────────────────────────────────────────────────

class TestLifecycle:
    def test_revision_under_print_does_not_block_recommend(self, engine):
        """revision_under_print event must not prevent RECOMMEND for IS 14220."""
        r = engine.analyze(
            AnalysisRequest(text="openwell submersible pumpset for agricultural irrigation")
        )
        assert r.decision == "RECOMMEND", \
            f"revision_under_print must not prevent RECOMMEND; got {r.decision}"
        lc = {l.standard_id: l for l in r.lifecycle}
        assert lc.get("IS 14220:2018") and lc["IS 14220:2018"].state == "supported", \
            f"IS 14220:2018 lifecycle should be 'supported'; got {lc.get('IS 14220:2018')}"


# ── Certification / QCO ───────────────────────────────────────────────────────

class TestCertification:
    def test_qco_proposed_not_verified(self, engine):
        """QCO_PROPOSED entries must surface as not_verified_in_prototype_corpus."""
        r = engine.analyze(
            AnalysisRequest(text="submersible pumpsets for a borewell supplying agricultural water")
        )
        cert = r.certification.get("IS 8034:2018")
        assert cert is not None
        assert cert.state == "not_verified_in_prototype_corpus", \
            f"QCO_PROPOSED must be not_verified; got state='{cert.state}'"
        assert cert.rule_type == "QCO_PROPOSED", \
            f"rule_type must be QCO_PROPOSED; got '{cert.rule_type}'"

    def test_qco_description_contains_restriction_notice(self, engine):
        """QCO description must contain the SOURCE ACCESS RESTRICTED notice."""
        r = engine.analyze(
            AnalysisRequest(text="openwell submersible pumpset for agricultural irrigation")
        )
        cert = r.certification.get("IS 14220:2018")
        assert cert is not None
        assert "SOURCE ACCESS RESTRICTED" in (cert.description or ""), \
            f"QCO_PROPOSED description must contain restriction notice; got: {cert.description}"

    def test_no_verified_qco_for_9079(self, engine):
        """IS 9079 has no QCO in the corpus — must return not_verified state."""
        r = engine.analyze(
            AnalysisRequest(text="monoset pump for clear cold water for agriculture")
        )
        cert = r.certification.get("IS 9079:2018")
        assert cert is not None
        assert cert.state == "not_verified_in_prototype_corpus"


# ── IS-number explicit lookup ─────────────────────────────────────────────────

class TestISNumberLookup:
    def test_is_14220_in_query_retrieved(self, engine):
        r = engine.analyze(
            AnalysisRequest(text="procurement as per IS 14220 openwell submersible pumpset")
        )
        assert any(x.standard_id == "IS 14220:2018" for x in r.candidates)

    def test_is_14220_exact_path_present(self, engine):
        r = engine.analyze(
            AnalysisRequest(text="procurement as per IS 14220 openwell submersible pumpset")
        )
        for c in r.candidates:
            if c.standard_id == "IS 14220:2018":
                assert "exact_id" in c.retrieval_paths, \
                    f"IS 14220:2018 must be retrieved via exact_id; got paths: {c.retrieval_paths}"
                break

    def test_is_8034_in_query_retrieved(self, engine):
        r = engine.analyze(
            AnalysisRequest(text="specification compliance for IS 8034 submersible pumpsets")
        )
        assert any(x.standard_id == "IS 8034:2018" for x in r.candidates)
        for c in r.candidates:
            if c.standard_id == "IS 8034:2018":
                assert "exact_id" in c.retrieval_paths, \
                    f"IS 8034:2018 must be retrieved via exact_id; got paths: {c.retrieval_paths}"
                break

    def test_certification_qco_safe_handling(self, engine):
        r = engine.analyze(
            AnalysisRequest(
                text="submersible pumpsets for a borewell supplying agricultural water with mandatory QCO ISI mark compliance"
            )
        )
        assert r.decision == "RECOMMEND"
        cert = r.certification.get("IS 8034:2018")
        assert cert is not None
        assert cert.state == "not_verified_in_prototype_corpus"
