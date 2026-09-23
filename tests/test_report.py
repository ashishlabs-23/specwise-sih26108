"""
Tests for app/report/builder.py

Verifies:
- Primary vs CoP candidate separation
- Presence of all required report sections
- Correct certification/QCO source-access wording
- No false inference of non-applicability
"""
import pytest
from app.engine import RecommendationEngine
from app.models import AnalysisRequest
from app.report.builder import _CERT_RESTRICTED, _CERT_NOT_IN_KB


@pytest.fixture(scope="module")
def engine():
    return RecommendationEngine()


@pytest.fixture(scope="module")
def openwell_report(engine):
    r = engine.analyze(AnalysisRequest(text="openwell submersible pumpset for agricultural irrigation"))
    return r.report_html


@pytest.fixture(scope="module")
def ooc_report(engine):
    r = engine.analyze(AnalysisRequest(text="advanced underwater robotic mining vehicle"))
    return r.report_html


class TestReportSections:
    REQUIRED_ANCHORS = [
        "decision", "requirements", "primary", "related-cands",
        "coverage", "gaps", "conflicts", "graph", "evidence", "timings",
    ]

    def test_all_anchors_present(self, openwell_report):
        for anchor in self.REQUIRED_ANCHORS:
            assert f'id="{anchor}"' in openwell_report, \
                f"Expected anchor id='{anchor}' in report"

    def test_decision_section_present(self, openwell_report):
        assert "Decision" in openwell_report
        assert "RECOMMEND" in openwell_report

    def test_requirements_section_present(self, openwell_report):
        assert "Requirements Extracted" in openwell_report

    def test_primary_standards_section_present(self, openwell_report):
        assert "Primary Product Standards" in openwell_report

    def test_related_cop_section_present(self, openwell_report):
        assert "Related / Code of Practice Standards" in openwell_report

    def test_coverage_section_present(self, openwell_report):
        assert "Coverage Matrix" in openwell_report

    def test_evidence_provenance_section_present(self, openwell_report):
        assert "Evidence Provenance" in openwell_report

    def test_disclaimer_present(self, openwell_report):
        assert "Prototype Disclaimer" in openwell_report


class TestPrimaryVsRelatedSeparation:
    def test_primary_standard_in_primary_section(self, openwell_report):
        """IS 14220:2018 (PRIMARY_PRODUCT_STANDARD) must appear in the Primary section."""
        primary_section_start = openwell_report.find('id="primary"')
        related_section_start = openwell_report.find('id="related-cands"')
        assert primary_section_start != -1
        assert related_section_start != -1
        primary_region = openwell_report[primary_section_start:related_section_start]
        assert "IS 14220:2018" in primary_region, \
            "IS 14220:2018 should appear in the Primary Product Standards section"

    def test_cop_standard_in_related_section(self, openwell_report):
        """IS 14536:2018 (CODE_OF_PRACTICE) must appear in the Related/CoP section."""
        related_section_start = openwell_report.find('id="related-cands"')
        coverage_section_start = openwell_report.find('id="coverage"')
        assert related_section_start != -1
        assert coverage_section_start != -1
        related_region = openwell_report[related_section_start:coverage_section_start]
        assert "IS 14536:2018" in related_region, \
            "IS 14536:2018 (CODE_OF_PRACTICE) should appear in the Related/CoP section"

    def test_cop_label_present_in_related_section(self, openwell_report):
        """CODE_OF_PRACTICE role label must be present in the related section."""
        related_section_start = openwell_report.find('id="related-cands"')
        coverage_section_start = openwell_report.find('id="coverage"')
        related_region = openwell_report[related_section_start:coverage_section_start]
        assert "CODE_OF_PRACTICE" in related_region, \
            "Role label CODE_OF_PRACTICE must appear in Related section"


class TestCertificationWording:
    def test_source_access_restricted_wording(self, openwell_report):
        """All unverified certification must show SOURCE ACCESS RESTRICTED."""
        assert _CERT_RESTRICTED in openwell_report or _CERT_NOT_IN_KB in openwell_report, \
            f"Expected '{_CERT_RESTRICTED}' or '{_CERT_NOT_IN_KB}' for unverified certification"

    def test_no_false_non_applicability_inference(self, openwell_report):
        """Report must not claim a standard does not need certification."""
        forbidden = [
            "certification not required",
            "QCO not applicable",
            "no certification needed",
            "exempt from",
        ]
        for phrase in forbidden:
            assert phrase.lower() not in openwell_report.lower(), \
                f"Report must not infer non-applicability: found '{phrase}'"

    def test_ooc_report_has_no_primary_candidates(self, ooc_report):
        """OUT_OF_CORPUS report must note no primary standards retrieved."""
        assert "No primary product standards retrieved" in ooc_report or \
               "OUT_OF_CORPUS" in ooc_report, \
               "OOC report must reflect that no candidates were found"


class TestApplicabilityInPrimaryBlock:
    def test_applicability_badge_present(self, openwell_report):
        """Primary candidate block must include applicability badge text."""
        assert "strong" in openwell_report or "possible" in openwell_report, \
            "Applicability result badge must appear in report"

    def test_lifecycle_state_present(self, openwell_report):
        """Primary candidate block must include lifecycle state."""
        assert "supported" in openwell_report or "warning" in openwell_report, \
            "Lifecycle state must appear in primary candidate block"

    def test_retrieval_paths_present(self, openwell_report):
        """Primary candidate block must include retrieval path information."""
        assert "bm25" in openwell_report or "exact_id" in openwell_report or \
               "Retrieval Paths" in openwell_report, \
               "Retrieval paths must appear in primary candidate block"
