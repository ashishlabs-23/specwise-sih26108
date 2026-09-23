"""
Repository Abstraction and Backend -> Frontend Data Contract Tests.

Validates:
1. Repository interface (JsonRepository, FirestoreRepository, factory get_repository)
2. Multi-domain schema compatibility
3. Deterministic migration payload generation & idempotency
4. Backend-to-Frontend complete field contract mapping
5. End-to-end data flow: backend response matches exact frontend rendered requirements
"""

import pytest
from unittest.mock import MagicMock
from app.storage.repository import (
    BaseRepository,
    JsonRepository,
    FirestoreRepository,
    get_repository,
)
from app.models import (
    AnalysisRequest,
    AnalysisResponse,
    StandardRecord,
    Evidence,
    Relationship,
    SourceRecord,
    BenchmarkCase,
)
from app.engine import RecommendationEngine
from app.api.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def json_repo():
    return JsonRepository("data")


@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)


# ── 1. Repository Abstraction Tests ──────────────────────────────────────────

class TestRepositoryAbstraction:
    def test_json_repo_exact_counts(self, json_repo):
        assert len(json_repo.standards) == 7, "Corpus must have exactly 7 standards"
        assert len(json_repo.evidence) == 15, "Corpus must have exactly 15 evidence records"
        assert len(json_repo.relationships) == 5, "Corpus must have exactly 5 relationships"
        assert len(json_repo.sources) == 5, "Corpus must have exactly 5 source documents"
        assert len(json_repo.benchmark_cases) == 10, "Corpus must have exactly 10 benchmark cases"
        assert len(json_repo.certification) == 2, "Corpus must have exactly 2 certification rules"

    def test_json_repo_health_summary(self, json_repo):
        summary = json_repo.get_health_summary()
        assert summary["data_source"] == "local"
        assert summary["standards_count"] == 7
        assert summary["evidence_count"] == 15
        assert summary["relationships_count"] == 5
        assert summary["sources_count"] == 5
        assert summary["benchmark_cases_count"] == 10

    def test_get_standard_and_evidence(self, json_repo):
        std = json_repo.get_standard("IS 14220:2018")
        assert std is not None
        assert std.standard_id == "IS 14220:2018"
        assert std.title == "Openwell Submersible Pumpsets"
        assert std.domain == "pumps"
        assert std.category == "pumps"

        ev = json_repo.get_evidence("E-14220-SCOPE")
        assert ev is not None
        assert ev.source_id == "BIS-14220-SUMMARY-2024"
        assert ev.verified is True

    def test_factory_get_repository_local(self):
        repo = get_repository(backend="LOCAL_DATA", data_dir="data")
        assert isinstance(repo, JsonRepository)
        assert repo.data_source == "local"

    def test_firestore_repo_with_mock_client(self, json_repo):
        """Validates that FirestoreRepository parses streams correctly into typed models."""
        mock_db = MagicMock()

        def make_mock_doc(data_dict):
            doc = MagicMock()
            doc.to_dict.return_value = data_dict
            return doc

        mock_std_docs = [make_mock_doc(s.model_dump()) for s in json_repo.standards]
        mock_src_docs = [make_mock_doc(s.model_dump()) for s in json_repo.sources]
        mock_ev_docs = [make_mock_doc(e.model_dump()) for e in json_repo.evidence]
        mock_rel_docs = [make_mock_doc(r.model_dump()) for r in json_repo.relationships]
        mock_cert_docs = [make_mock_doc(c) for c in json_repo.certification]
        mock_bench_docs = [make_mock_doc(b.model_dump()) for b in json_repo.benchmark_cases]

        def mock_collection(name):
            col = MagicMock()
            if name == "standards":
                col.stream.return_value = mock_std_docs
            elif name == "sources":
                col.stream.return_value = mock_src_docs
            elif name == "evidence":
                col.stream.return_value = mock_ev_docs
            elif name == "relationships":
                col.stream.return_value = mock_rel_docs
            elif name == "certification":
                col.stream.return_value = mock_cert_docs
            elif name == "benchmark_cases":
                col.stream.return_value = mock_bench_docs
            return col

        mock_db.collection.side_effect = mock_collection

        fs_repo = FirestoreRepository(firestore_client=mock_db)
        assert fs_repo.data_source == "firestore"
        assert len(fs_repo.standards) == 7
        assert len(fs_repo.evidence) == 15
        assert len(fs_repo.relationships) == 5
        assert len(fs_repo.sources) == 5
        assert len(fs_repo.benchmark_cases) == 10
        assert len(fs_repo.certification) == 2


# ── 2. Multi-Domain & Vector Schema Support ──────────────────────────────────

class TestMultiDomainAndVectorSchema:
    def test_domain_fields_present(self, json_repo):
        for std in json_repo.standards:
            assert hasattr(std, "domain"), f"Standard {std.standard_id} must have 'domain' field"
            assert std.domain != "", "Domain must not be empty"
            assert hasattr(std, "category"), f"Standard {std.standard_id} must have 'category' field"
            assert hasattr(std, "embedding"), f"Standard {std.standard_id} must have 'embedding' field"
            assert hasattr(std, "embedding_model"), f"Standard {std.standard_id} must have 'embedding_model' field"
            assert hasattr(std, "metadata"), f"Standard {std.standard_id} must have 'metadata' field"

    def test_evidence_domain_present(self, json_repo):
        for ev in json_repo.evidence:
            assert hasattr(ev, "domain"), f"Evidence {ev.evidence_id} must have 'domain' field"


# ── 3. Migration Payload Idempotency ─────────────────────────────────────────

class TestMigrationPayloads:
    def test_deterministic_doc_ids(self, json_repo):
        from scripts.migrate_to_firestore import build_migration_payloads

        payloads1 = build_migration_payloads(json_repo)
        payloads2 = build_migration_payloads(json_repo)

        assert payloads1.keys() == payloads2.keys()
        for col in payloads1:
            assert payloads1[col].keys() == payloads2[col].keys(), f"Mismatch in collection {col}"
            assert len(payloads1[col]) == len(payloads2[col])

        # Verify key document IDs are sanitized and deterministic
        assert "IS_14220_2018" in payloads1["standards"]
        assert "IS_8034_2018" in payloads1["standards"]
        assert "E-14220-SCOPE" in payloads1["evidence"]
        assert "BIS-14220-SUMMARY-2024" in payloads1["sources"]
        assert "openwell-primary-recommend" in payloads1["benchmark_cases"]


# ── 4. Backend -> Frontend Contract Verification ─────────────────────────────

class TestBackendFrontendContract:
    def test_health_endpoint_contract(self, test_client):
        res = test_client.get("/api/v1/health")
        assert res.status_code == 200
        data = res.json()
        assert "status" in data and data["status"] == "ok"
        assert "data_source" in data and data["data_source"] in {"local", "firestore"}
        assert "standards_count" in data and data["standards_count"] == 7
        assert "evidence_count" in data and data["evidence_count"] == 15
        assert "relationships_count" in data and data["relationships_count"] == 5
        assert "sources_count" in data and data["sources_count"] == 5

    def test_resources_endpoint_contract(self, test_client):
        res = test_client.get("/api/v1/resources")
        assert res.status_code == 200
        data = res.json()

        # Summary
        summary = data["summary"]
        assert summary["standards_count"] == 7
        assert summary["evidence_count"] == 15
        assert summary["relationships_count"] == 5
        assert summary["sources_count"] == 5
        assert summary["benchmark_cases_count"] == 10

        # Standards list
        assert len(data["standards"]) == 7
        for std in data["standards"]:
            assert "standard_id" in std
            assert "title" in std
            assert "scope" in std
            assert "standard_role" in std
            assert "evidence_ids" in std

        # Evidence list
        assert len(data["evidence"]) == 15
        for ev in data["evidence"]:
            assert "evidence_id" in ev
            assert "source_name" in ev
            assert "text" in ev
            assert "verified" in ev

        # Relationships list
        assert len(data["relationships"]) == 5
        for rel in data["relationships"]:
            assert "from_standard" in rel
            assert "to_standard" in rel
            assert "relationship_type" in rel

        # Benchmark cases list
        assert len(data["benchmark_cases"]) == 10
        for b in data["benchmark_cases"]:
            assert "id" in b
            assert "query" in b
            assert "expected_contains" in b

    def test_analyze_endpoint_contract_and_values(self, test_client):
        """
        Tests that backend /api/v1/analyze response contains all fields required
        by the frontend components and validates exact values for IS 14220:2018.
        """
        payload = {"text": "openwell submersible pumpset for agricultural irrigation"}
        res = test_client.post("/api/v1/analyze", json=payload)
        assert res.status_code == 200
        data = res.json()

        # Top-level fields
        assert "analysis_id" in data
        assert "input_text" in data
        assert "requirements" in data
        assert "candidates" in data
        assert "applicability" in data
        assert "lifecycle" in data
        assert "related_standards" in data
        assert "certification" in data
        assert "coverage" in data
        assert "gaps" in data
        assert "conflicts" in data
        assert "decision" in data
        assert "decision_reasons" in data
        assert "evidence" in data
        assert "report_html" in data
        assert "timings_ms" in data

        # Specific Value Checks for openwell query:
        # 1. Decision State
        assert data["decision"] == "RECOMMEND"

        # 2. Standard Number and Title
        assert len(data["candidates"]) >= 1
        top_cand = data["candidates"][0]
        assert top_cand["standard_id"] == "IS 14220:2018"
        assert top_cand["title"] == "Openwell Submersible Pumpsets"

        # 3. Evidence Citation
        ev_ids = {e["evidence_id"] for e in data["evidence"]}
        assert "E-14220-SCOPE" in ev_ids

        # 4. Related Standard Expansion
        related_targets = {r["to_standard"] for r in data["related_standards"]}
        assert "IS 14536:2018" in related_targets

        # 5. Certification Info
        assert "IS 14220:2018" in data["certification"]
        assert data["certification"]["IS 14220:2018"]["state"] in {
            "verified",
            "not_verified_in_prototype_corpus",
        }

    def test_recommend_endpoint_alias(self, test_client):
        """Tests that /api/v1/recommend behaves identically as /api/v1/analyze."""
        payload = {"text": "openwell submersible pumpset"}
        res = test_client.post("/api/v1/recommend", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["decision"] == "RECOMMEND"
        assert len(data["candidates"]) >= 1

    def test_security_no_credentials_leaked(self, test_client):
        """Ensures that health, resources, and analyze endpoints never expose secrets/credentials."""
        for endpoint in ["/api/v1/health", "/api/v1/resources"]:
            res = test_client.get(endpoint)
            assert res.status_code == 200
            text_payload = res.text.lower()
            assert "private_key" not in text_payload
            assert "client_secret" not in text_payload
            assert "service_account" not in text_payload
            assert "begin private key" not in text_payload

    def test_firestore_startup_missing_credentials_file(self):
        """Tests that a clear FileNotFoundError is raised when credentials path does not exist."""
        with pytest.raises(FileNotFoundError, match="Firebase credentials file not found"):
            FirestoreRepository(
                project_id="test-project",
                credentials_path="/non/existent/path/creds.json"
            )

    def test_firestore_startup_missing_project_id(self):
        """Tests that ValueError is raised when FIRESTORE_PROJECT_ID is missing."""
        with pytest.raises(ValueError, match="FIRESTORE_PROJECT_ID must be set"):
            FirestoreRepository(
                project_id="",
                credentials_path=None
            )

