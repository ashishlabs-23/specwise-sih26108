from dataclasses import dataclass, field
import os


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: list[str]) -> list[str]:
    value = os.getenv(name)
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    data_dir: str = os.getenv("DATA_DIR", "data")
    # Storage repository backend: LOCAL_DATA (default) or FIRESTORE
    data_backend: str = os.getenv("DATA_BACKEND", "LOCAL_DATA").upper()
    firestore_project_id: str | None = os.getenv("FIRESTORE_PROJECT_ID", None)
    firestore_database: str = os.getenv("FIRESTORE_DATABASE", "(default)")
    firestore_credentials_path: str | None = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", None)
    port: int = int(os.getenv("PORT", "8000"))
    cors_origins: list[str] = field(
        default_factory=lambda: env_list(
            "CORS_ORIGINS",
            [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:8000",
                "http://127.0.0.1:8000",
                "https://specwise-sih26108.web.app",
                "https://specwise-sih26108.firebaseapp.com",
            ]
        )
    )
    enable_dense: bool = env_bool("ENABLE_DENSE", False)
    enable_reranker: bool = env_bool("ENABLE_RERANKER", False)
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    reranker_model: str = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    max_candidates: int = int(os.getenv("MAX_CANDIDATES", "8"))
    max_related_hops: int = int(os.getenv("MAX_RELATED_HOPS", "2"))
    # CON-05: minimum RRF score required to treat a BM25 hit as in-corpus
    relevance_floor: float = float(os.getenv("RELEVANCE_FLOOR", "0.005"))


settings = Settings()

