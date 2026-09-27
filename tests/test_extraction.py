import pytest
from app.extraction.requirement_extractor import extract_requirements
from app.engine import RecommendationEngine
from app.models import AnalysisRequest


def test_power_extracted():
    """CON-01: power regex must fire regardless of product keywords."""
    rows = extract_requirements("5 HP openwell submersible pumpset for agricultural irrigation.")
    assert any(x.attribute == "rated_power" and x.value == "5" for x in rows), \
        "Expected a rated_power requirement for '5 HP'"


def test_general_product_row_emitted():
    """CON-01: a general product row is emitted for any substantive sentence."""
    rows = extract_requirements("5 HP openwell submersible pumpset for agricultural irrigation.")
    assert any(x.category == "product" for x in rows), \
        "Expected at least one product category row"


def test_is_reference_extracted():
    """IS-number regex must be domain-agnostic."""
    rows = extract_requirements("Supply as per IS 14220 and IS 8034:2018.")
    ref_values = [r.value for r in rows if r.category == "reference"]
    assert "IS 14220" in ref_values, f"Expected IS 14220, got {ref_values}"
    assert "IS 8034:2018" in ref_values, f"Expected IS 8034:2018, got {ref_values}"


def test_line_wrapped_is_reference_is_normalized_without_losing_page():
    rows = extract_requirements("[PAGE 2]\nComply with\nIS\n77777:2026\r\n.")
    refs = [r for r in rows if r.category == "reference"]
    assert [r.value for r in refs] == ["IS 77777:2026"]
    assert refs[0].source_page == 2


def test_normalized_supported_and_older_is_references():
    rows = extract_requirements("IS\n8034:2018. IS 14220:1994.")
    assert {r.value for r in rows if r.category == "reference"} == {
        "IS 8034:2018", "IS 14220:1994"
    }


def test_arbitrary_numbers_are_not_references():
    rows = extract_requirements("The equipment is sized for 77777 units and 2026 cycles.")
    assert not [r for r in rows if r.category == "reference"]


@pytest.mark.parametrize("citation", [
    "IS 1554 (Part 1):1988",
    "IS 1554(Part 1):1988",
    "IS 1554 Part 1:1988",
    "IS 1554 (Part-1):1988",
    "IS 1554 (Part 1):\n1988",
])
def test_is_reference_preserves_part_year_and_source_citation(citation):
    rows = extract_requirements(f"Cable shall conform to {citation}.")
    reference = next(r for r in rows if r.category == "reference")
    assert reference.standard_number == "IS 1554"
    assert reference.part == "Part 1"
    assert reference.year == "1988"
    assert reference.value == "IS 1554 Part 1:1988"
    assert "IS 1554" in reference.source_citation
    assert "1988" in reference.source_citation
    if "\n" in citation:
        assert reference.source_citation == citation


def test_is_reference_preserves_part_year_for_line_wrapped_citation():
    source = "Cable shall conform to\r\nIS 1554 (Part 1):\r\n1988."
    reference = next(r for r in extract_requirements(source) if r.category == "reference")
    assert reference.value == "IS 1554 Part 1:1988"
    assert reference.part == "Part 1"
    assert reference.year == "1988"
    assert reference.source_citation == "IS 1554 (Part 1):\r\n1988"


def test_part_year_reference_matches_existing_edition_without_inventing_revision():
    result = RecommendationEngine().analyze(AnalysisRequest(text=(
        "Supply PVC insulated cable and glands to IS 1554 (Part 1):1988."
    )))
    reference = next(r for r in result.requirements if r.category == "reference")
    assert reference.value == "IS 1554 Part 1:1988"
    assert any(
        item.standard_id == "IS 1554:1988" and item.state != "edition_mismatch"
        for item in result.coverage
    )
    assert not any(
        item.state == "unverified_reference" and "1554" in item.reason
        for item in result.coverage
    )


def test_fallback_for_empty_input():
    """Fallback requirement must be emitted when no other patterns fire."""
    rows = extract_requirements("some text with no patterns")
    assert rows, "Expected at least a fallback requirement"
