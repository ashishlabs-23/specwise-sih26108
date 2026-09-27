from app.engine import RecommendationEngine
from app.extraction.requirement_extractor import extract_requirements
from app.models import AnalysisRequest


def _product_items(text):
    return [item for item in extract_requirements(text) if item.category == "product" and item.item_id]


def test_lettered_mixed_items_keep_independent_item_ids():
    text = (
        "Supply package: (a) borewell submersible pumpset, 5 HP, 415 V; "
        "(b) solar PV modules; (c) MPPT inverter/controller; "
        "(d) galvanized mounting structure."
    )
    items = _product_items(text)
    assert [item.item_id for item in items] == ["ITEM-001", "ITEM-002", "ITEM-003", "ITEM-004"]
    assert "borewell" in items[0].text.lower()
    assert "solar" in items[1].text.lower()
    assert "inverter" in items[2].text.lower()
    assert "mounting" in items[3].text.lower()


def test_attributes_stay_with_one_numbered_pump_item():
    text = (
        "1. Supply a 5 HP borewell submersible pumpset, 415 V, 3-phase, "
        "24 m head, 12 L/s discharge, cast iron casing, complete with accessories."
    )
    items = _product_items(text)
    assert len(items) == 1
    assert items[0].item_id == "ITEM-001"
    assert "cast iron casing" in items[0].text.lower()


def test_semicolon_and_numbered_component_boundaries_are_domain_agnostic():
    cases = [
        "(a) borewell pump; (b) cable; (c) GI pipe.",
        "1. openwell pump\n2. control panel\n3. cable",
        "(a) laboratory centrifuge; (b) UPS; (c) computer workstation.",
        "(a) fire sprinkler system; (b) fire pump; (c) control panel.",
    ]
    for text in cases:
        items = _product_items(text)
        assert len(items) == 3
        assert len({item.item_id for item in items}) == 3


def test_mixed_pump_and_solar_is_review_with_uncovered_component_items():
    text = (
        "Supply package: (a) borewell submersible pumpset, 3 HP; "
        "(b) solar PV modules; (c) MPPT inverter/controller; "
        "(d) galvanized mounting structure."
    )
    result = RecommendationEngine().analyze(AnalysisRequest(text=text))
    assert result.decision == "REVIEW"
    pump = [item for item in result.requirements if item.item_id == "ITEM-001"]
    other_ids = {item.requirement_id for item in result.requirements if item.item_id in {"ITEM-002", "ITEM-003", "ITEM-004"}}
    assert any(entry.requirement_id in {item.requirement_id for item in pump} and entry.standard_id == "IS 8034:2018" and entry.state == "covered" for entry in result.coverage)
    assert other_ids <= {entry.requirement_id for entry in result.gaps if entry.state == "not_covered"}


def test_single_item_pump_preserves_existing_recommendation():
    result = RecommendationEngine().analyze(AnalysisRequest(text=(
        "Supply a 5 HP borewell submersible pumpset, 415 V, 3-phase, "
        "24 m head, 12 L/s discharge, cast iron casing, complete with accessories."
    )))
    assert result.decision == "RECOMMEND"

