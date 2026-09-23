from datetime import date
from app.models import StandardRecord
from app.policy.lifecycle import assess


def test_revision_under_print_is_supported():
    """
    revision_under_print does NOT mean the standard is withdrawn.
    Per DESIGN lifecycle rules, 'supported' is the correct state —
    the BIS note explicitly says 'this does not by itself prove withdrawal'.
    """
    s = StandardRecord(
        standard_id="IS 8034:2018", title="Submersible Pumpsets",
        scope="Submersible pumpsets", category="pumps",
        lifecycle_events=[{"event": "revision_under_print", "date": "2026-06-02",
                           "evidence_ids": ["E-8034-REVISION-2026"]}],
        evidence_ids=["E-8034-REVISION-2026"]
    )
    result = assess(s, date(2026, 9, 22))
    assert result.state == "supported", (
        f"revision_under_print should not trigger 'warning'; got '{result.state}'. "
        "Only 'withdrawn_after_revision' is a lifecycle warning."
    )
    assert result.reasons, "Expected at least one reason string"


def test_withdrawn_after_revision_is_warning():
    """withdrawn_after_revision event must trigger lifecycle warning."""
    s = StandardRecord(
        standard_id="IS TEST:2002", title="Test Standard",
        scope="Test scope", category="test",
        lifecycle_events=[{"event": "withdrawn_after_revision", "date": "2019-04-04",
                           "evidence_ids": []}],
        evidence_ids=[]
    )
    result = assess(s, date(2026, 9, 22))
    assert result.state == "warning", (
        f"withdrawn_after_revision should trigger 'warning'; got '{result.state}'"
    )
