from app.policy.domain_relevance import has_corpus_product_signal
from app.storage.repository import get_repository
from app.engine import RecommendationEngine
from app.models import AnalysisRequest


def test_accessory_mentions_do_not_define_primary_procurement():
    standards = get_repository().standards
    fire = (
        "Supply, installation and commissioning of automatic fire sprinkler heads, "
        "alarm valves, fire hose reels, hydrant pumps, pressure switches and panels."
    )
    solar = (
        "Supply 540 W solar PV modules, string inverters, mounting structures, "
        "DC/AC cables and monitoring system."
    )
    assert not has_corpus_product_signal(fire, standards)
    assert not has_corpus_product_signal(solar, standards)


def test_primary_cable_and_mixed_item_procurement_are_retained():
    standards = get_repository().standards
    cable = "Supply PVC insulated cable up to 1100V for electric supply."
    mixed = (
        "MIXED PROCUREMENT\n"
        "Item 1: agricultural borewell submersible pumpset, 5 HP.\n"
        "Item 2: 540 W mono PERC solar PV modules.\n"
        "Item 3: grid-tie string inverter."
    )
    assert has_corpus_product_signal(cable, standards)
    assert has_corpus_product_signal(mixed, standards)


def test_document_decisions_follow_primary_procurement_and_coverage():
    engine = RecommendationEngine()
    fire = engine.analyze(AnalysisRequest(text=(
        "Supply, installation and commissioning of automatic fire sprinkler heads, "
        "alarm valves, fire hose reels, hydrant pumps, pressure switches and panels."
    )))
    solar = engine.analyze(AnalysisRequest(text=(
        "Supply 540 W solar PV modules, string inverters, mounting structures, "
        "DC/AC cables and monitoring system."
    )))
    mixed = engine.analyze(AnalysisRequest(text=(
        "MIXED PROCUREMENT\nItem 1: agricultural borewell submersible pumpset, 5 HP.\n"
        "Item 2: 540 W mono PERC solar PV modules.\nItem 3: grid-tie string inverter."
    )))
    generic = engine.analyze(AnalysisRequest(text="submersible pump for water supply"))
    cable = engine.analyze(AnalysisRequest(text="Supply PVC insulated cable up to 1100V."))
    assert fire.decision == "OUT_OF_CORPUS" and not fire.candidates
    assert solar.decision == "OUT_OF_CORPUS" and not solar.candidates
    assert mixed.decision == "REVIEW"
    assert any(g.state == "not_covered" for g in mixed.gaps)
    assert generic.decision == "ABSTAIN"
    assert cable.candidates


def test_explicit_fake_is_reference_survives_procurement_relevance_gate():
    result = RecommendationEngine().analyze(AnalysisRequest(text=(
        "PROCUREMENT SPECIFICATION. The buyer explicitly cites IS 77777:2026."
    )))
    assert any(g.state == "unverified_reference" for g in result.gaps)
    assert result.decision == "REVIEW"
