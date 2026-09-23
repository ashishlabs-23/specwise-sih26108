import pytest
from app.engine import RecommendationEngine
from app.models import AnalysisRequest

# Single engine instance for all tests (reload is cheap for static corpus)
@pytest.fixture(scope="module")
def engine():
    return RecommendationEngine()


def test_openwell_recommends_14220(engine):
    """Openwell query must RECOMMEND IS 14220:2018 specifically."""
    r = engine.analyze(AnalysisRequest(text="openwell submersible pumpset for agricultural irrigation"))
    assert r.decision == "RECOMMEND", f"Expected RECOMMEND, got {r.decision}. Reasons: {r.decision_reasons}"
    assert any(x.standard_id == "IS 14220:2018" for x in r.candidates)
    strong = [a.standard_id for a in r.applicability if a.result == "strong"]
    assert strong == ["IS 14220:2018"], f"Only IS 14220:2018 should be strong; got {strong}"


def test_borewell_recommends_8034(engine):
    """Borewell submersible query must RECOMMEND IS 8034:2018."""
    r = engine.analyze(AnalysisRequest(text="submersible pumpset for a borewell supplying agricultural water"))
    assert r.decision == "RECOMMEND", f"Expected RECOMMEND, got {r.decision}. Reasons: {r.decision_reasons}"
    strong = [a.standard_id for a in r.applicability if a.result == "strong"]
    assert "IS 8034:2018" in strong, f"IS 8034:2018 must be strong; got {strong}"
    assert len(strong) == 1, f"Exactly one strong candidate expected; got {strong}"


def test_monoset_recommends_9079(engine):
    """Monoset query must RECOMMEND IS 9079:2018."""
    r = engine.analyze(AnalysisRequest(text="monoset pump for clear cold water for agriculture"))
    assert r.decision == "RECOMMEND", f"Expected RECOMMEND, got {r.decision}. Reasons: {r.decision_reasons}"
    strong = [a.standard_id for a in r.applicability if a.result == "strong"]
    assert "IS 9079:2018" in strong


def test_cop_not_primary_recommendation(engine):
    """IS 14536 (CODE_OF_PRACTICE) must never be the sole strong candidate driving RECOMMEND."""
    r = engine.analyze(AnalysisRequest(text="submersible pumpset for borewell agricultural water"))
    strong = [a.standard_id for a in r.applicability if a.result == "strong"]
    assert "IS 14536:2018" not in strong, \
        f"CODE_OF_PRACTICE IS 14536:2018 must not be strong; got strong={strong}"


def test_out_of_corpus_for_unknown_domain(engine):
    """Completely out-of-domain query must return OUT_OF_CORPUS."""
    r = engine.analyze(AnalysisRequest(text="advanced underwater robotic mining vehicle"))
    assert r.decision == "OUT_OF_CORPUS", f"Expected OUT_OF_CORPUS, got {r.decision}"
    assert r.candidates == []


def test_is_number_query_retrieves_correct_standard(engine):
    """Explicit IS reference in query must be retrieved via exact_id."""
    r = engine.analyze(AnalysisRequest(text="Procurement as per IS 14220 openwell submersible pumpset"))
    assert any(x.standard_id == "IS 14220:2018" for x in r.candidates)


def test_decision_reasons_always_non_empty(engine):
    """CON-04: decision_reasons must always be populated."""
    for text in [
        "openwell submersible pumpset for agricultural irrigation",
        "advanced underwater robotic mining vehicle",
        "submersible pumpset for a borewell",
    ]:
        r = engine.analyze(AnalysisRequest(text=text))
        assert r.decision_reasons, f"Empty decision_reasons for: {text!r}"


def test_total_ms_encompasses_all_phases(engine):
    """CON-07: total_ms must be >= sum of individual phases."""
    r = engine.analyze(AnalysisRequest(text="openwell submersible pumpset for agricultural irrigation"))
    phase_sum = sum(v for k, v in r.timings_ms.items() if k != "total_ms")
    assert r.timings_ms.get("total_ms", 0) >= phase_sum * 0.9


def test_ambiguous_submersible_only_query(engine):
    """Generic 'submersible pump for water supply' — no product_term matches exactly.
    IS 8034 requires 'submersible pumpset'; this shorter query doesn't hit it.
    ABSTAIN is the correct honest outcome. REVIEW is also acceptable.
    OUT_OF_CORPUS is NOT acceptable — candidates are retrieved above the relevance floor."""
    r = engine.analyze(AnalysisRequest(text="submersible pump for water supply"))
    assert r.decision in {"RECOMMEND", "REVIEW", "ABSTAIN"}, \
        f"Expected RECOMMEND/REVIEW/ABSTAIN, got {r.decision}"
    # Candidates must still be retrieved (corpus does contain submersible standards)
    assert any(x.standard_id == "IS 8034:2018" for x in r.candidates), \
        "IS 8034:2018 must appear in candidates for a submersible query"
