from app.extraction.requirement_extractor import extract_requirements


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


def test_fallback_for_empty_input():
    """Fallback requirement must be emitted when no other patterns fire."""
    rows = extract_requirements("some text with no patterns")
    assert rows, "Expected at least a fallback requirement"
