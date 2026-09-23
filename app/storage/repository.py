import json
import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

from app.config import settings
from app.models import (
    BenchmarkCase,
    Evidence,
    Relationship,
    SourceRecord,
    StandardRecord,
)

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """
    Abstract Base Class defining the data-access interface for BIS standards,
    evidence, relationships, sources, certification rules, and benchmark cases.
    """

    @property
    @abstractmethod
    def data_source(self) -> str:
        """Returns 'local' or 'firestore'."""
        pass

    @property
    @abstractmethod
    def standards(self) -> list[StandardRecord]:
        pass

    @property
    @abstractmethod
    def sources(self) -> list[SourceRecord]:
        pass

    @property
    @abstractmethod
    def evidence(self) -> list[Evidence]:
        pass

    @property
    @abstractmethod
    def relationships(self) -> list[Relationship]:
        pass

    @property
    @abstractmethod
    def certification(self) -> list[dict[str, Any]]:
        pass

    @property
    @abstractmethod
    def benchmark_cases(self) -> list[BenchmarkCase]:
        pass

    @abstractmethod
    def get_standard(self, standard_id: str) -> Optional[StandardRecord]:
        pass

    @abstractmethod
    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        pass

    def get_health_summary(self) -> dict[str, Any]:
        return {
            "data_source": self.data_source,
            "standards_count": len(self.standards),
            "evidence_count": len(self.evidence),
            "relationships_count": len(self.relationships),
            "sources_count": len(self.sources),
            "benchmark_cases_count": len(self.benchmark_cases),
        }


class JsonRepository(BaseRepository):
    """
    Local JSON-based repository reading from verified frozen seed files.
    Used for offline development, local unit tests, and continuous evaluation.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        seed_path = self.data_dir / "standards_seed.json"
        if not seed_path.exists():
            raise FileNotFoundError(f"Missing standards seed file at {seed_path}")

        payload = json.loads(seed_path.read_text(encoding="utf-8"))
        self._standards = [StandardRecord.model_validate(x) for x in payload.get("standards", [])]
        self._sources = [SourceRecord.model_validate(x) for x in payload.get("sources", [])]
        self._evidence = [Evidence.model_validate(x) for x in payload.get("evidence", [])]
        self._relationships = [Relationship.model_validate(x) for x in payload.get("relationships", [])]

        cert_path = self.data_dir / "certification_mapping.json"
        if cert_path.exists():
            cert = json.loads(cert_path.read_text(encoding="utf-8"))
            self._certification = cert.get("rules", [])
        else:
            self._certification = []

        eval_path = self.data_dir / "evaluation_cases.json"
        if eval_path.exists():
            eval_payload = json.loads(eval_path.read_text(encoding="utf-8"))
            self._benchmark_cases = [
                BenchmarkCase.model_validate(x) for x in eval_payload.get("cases", [])
            ]
        else:
            self._benchmark_cases = []

        # Fast lookup indexes
        self._standards_by_id = {
            s.standard_id.upper().replace(" ", ""): s for s in self._standards
        }
        self._evidence_by_id = {e.evidence_id: e for e in self._evidence}

    @property
    def data_source(self) -> str:
        return "local"

    @property
    def standards(self) -> list[StandardRecord]:
        return list(self._standards)

    @property
    def sources(self) -> list[SourceRecord]:
        return list(self._sources)

    @property
    def evidence(self) -> list[Evidence]:
        return list(self._evidence)

    @property
    def relationships(self) -> list[Relationship]:
        return list(self._relationships)

    @property
    def certification(self) -> list[dict[str, Any]]:
        return list(self._certification)

    @property
    def benchmark_cases(self) -> list[BenchmarkCase]:
        return list(self._benchmark_cases)

    def get_standard(self, standard_id: str) -> Optional[StandardRecord]:
        key = standard_id.upper().replace(" ", "")
        return self._standards_by_id.get(key)

    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        return self._evidence_by_id.get(evidence_id)


class FirestoreRepository(BaseRepository):
    """
    Cloud Firestore-backed repository implementation.
    Reads verified standards, evidence, relationships, sources, and benchmarks
    from cloud collections. Supports multi-domain partitioning and future vector indexing.
    """

    COLLECTION_STANDARDS = "standards"
    COLLECTION_EVIDENCE = "evidence"
    COLLECTION_RELATIONSHIPS = "relationships"
    COLLECTION_SOURCES = "sources"
    COLLECTION_BENCHMARKS = "benchmark_cases"
    COLLECTION_CERTIFICATION = "certification"

    def __init__(
        self,
        project_id: Optional[str] = None,
        database: str = "(default)",
        credentials_path: Optional[str] = None,
        firestore_client: Any = None,
    ):
        self._project_id = project_id or settings.firestore_project_id
        self._database = database or settings.firestore_database
        self._credentials_path = credentials_path or settings.firestore_credentials_path

        if firestore_client is not None:
            self._db = firestore_client
        else:
            self._db = self._init_client()

        self._standards: list[StandardRecord] = []
        self._sources: list[SourceRecord] = []
        self._evidence: list[Evidence] = []
        self._relationships: list[Relationship] = []
        self._certification: list[dict[str, Any]] = []
        self._benchmark_cases: list[BenchmarkCase] = []

        self._standards_by_id: dict[str, StandardRecord] = {}
        self._evidence_by_id: dict[str, Evidence] = {}

        self.refresh()

    def _init_client(self):
        try:
            from google.cloud import firestore  # type: ignore
            from google.oauth2 import service_account  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "google-cloud-firestore package is required when DATA_BACKEND=FIRESTORE. "
                "Install with: pip install google-cloud-firestore"
            ) from exc

        # 1. Credentials file validation
        credentials = None
        if self._credentials_path:
            if not os.path.exists(self._credentials_path):
                raise FileNotFoundError(
                    f"Firebase credentials file not found at '{self._credentials_path}'. "
                    "When deploying to Render, ensure Secret File path is configured in GOOGLE_APPLICATION_CREDENTIALS."
                )
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    self._credentials_path
                )
            except Exception as exc:
                raise ValueError(
                    f"Failed to parse Firebase service-account credentials from '{self._credentials_path}': {exc}"
                ) from exc

        # 2. Project ID resolution
        project_id = self._project_id
        if not project_id and credentials and hasattr(credentials, "project_id"):
            project_id = credentials.project_id

        if not project_id:
            raise ValueError(
                "Missing required environment variable: FIRESTORE_PROJECT_ID must be set when DATA_BACKEND=FIRESTORE."
            )

        kwargs: dict[str, Any] = {"database": self._database, "project": project_id}
        if credentials:
            kwargs["credentials"] = credentials

        try:
            client = firestore.Client(**kwargs)
            return client
        except Exception as exc:
            logger.error("Failed to initialize Firestore client: %s", exc)
            raise RuntimeError(
                f"Firestore connection failed: {exc}. "
                f"Ensure project '{project_id}' exists and Cloud Firestore API is enabled."
            ) from exc

    def refresh(self):
        """Fetches all documents from Firestore collections into in-memory cached structures."""
        try:
            # 1. Standards
            std_docs = self._db.collection(self.COLLECTION_STANDARDS).stream()
            self._standards = [
                StandardRecord.model_validate(doc.to_dict()) for doc in std_docs
            ]

            # 2. Sources
            src_docs = self._db.collection(self.COLLECTION_SOURCES).stream()
            self._sources = [
                SourceRecord.model_validate(doc.to_dict()) for doc in src_docs
            ]

            # 3. Evidence
            ev_docs = self._db.collection(self.COLLECTION_EVIDENCE).stream()
            self._evidence = [
                Evidence.model_validate(doc.to_dict()) for doc in ev_docs
            ]

            # 4. Relationships
            rel_docs = self._db.collection(self.COLLECTION_RELATIONSHIPS).stream()
            self._relationships = [
                Relationship.model_validate(doc.to_dict()) for doc in rel_docs
            ]

            # 5. Certification
            cert_docs = self._db.collection(self.COLLECTION_CERTIFICATION).stream()
            self._certification = [doc.to_dict() for doc in cert_docs]

            # 6. Benchmark cases
            bench_docs = self._db.collection(self.COLLECTION_BENCHMARKS).stream()
            self._benchmark_cases = [
                BenchmarkCase.model_validate(doc.to_dict()) for doc in bench_docs
            ]

            # Update fast lookup indexes
            self._standards_by_id = {
                s.standard_id.upper().replace(" ", ""): s for s in self._standards
            }
            self._evidence_by_id = {e.evidence_id: e for e in self._evidence}

            logger.info(
                "Firestore cache refreshed: %d standards, %d evidence, %d relationships, %d sources, %d benchmarks",
                len(self._standards),
                len(self._evidence),
                len(self._relationships),
                len(self._sources),
                len(self._benchmark_cases),
            )
        except Exception as exc:
            logger.error("Error refreshing Firestore collections: %s", exc)
            raise

    @property
    def data_source(self) -> str:
        return "firestore"

    @property
    def standards(self) -> list[StandardRecord]:
        return list(self._standards)

    @property
    def sources(self) -> list[SourceRecord]:
        return list(self._sources)

    @property
    def evidence(self) -> list[Evidence]:
        return list(self._evidence)

    @property
    def relationships(self) -> list[Relationship]:
        return list(self._relationships)

    @property
    def certification(self) -> list[dict[str, Any]]:
        return list(self._certification)

    @property
    def benchmark_cases(self) -> list[BenchmarkCase]:
        return list(self._benchmark_cases)

    def get_standard(self, standard_id: str) -> Optional[StandardRecord]:
        key = standard_id.upper().replace(" ", "")
        return self._standards_by_id.get(key)

    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        return self._evidence_by_id.get(evidence_id)


def get_repository(
    backend: Optional[str] = None, data_dir: Optional[str] = None
) -> BaseRepository:
    """
    Factory function returning the configured repository instance.
    Defaults to JsonRepository (LOCAL_DATA). Switches to FirestoreRepository when
    DATA_BACKEND=FIRESTORE.
    """
    selected_backend = (backend or settings.data_backend or "LOCAL_DATA").upper()
    if selected_backend in {"FIRESTORE", "GCP_FIRESTORE", "CLOUD"}:
        return FirestoreRepository(
            project_id=settings.firestore_project_id,
            database=settings.firestore_database,
            credentials_path=settings.firestore_credentials_path,
        )
    return JsonRepository(data_dir or settings.data_dir)
