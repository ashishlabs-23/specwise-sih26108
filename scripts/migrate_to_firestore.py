#!/usr/bin/env python3
"""
Deterministic, idempotent migration script to import the verified BIS corpus
into Google Cloud Firestore.

Collections populated:
- standards (7 documents)
- evidence (15 documents)
- relationships (5 documents)
- sources (5 documents)
- benchmark_cases (10 documents)
- certification (2 documents)

Idempotence Guarantee:
Every document uses a deterministic document ID derived from its canonical key.
Writes use `set(..., merge=True)` so re-running this migration is completely safe
and never creates duplicates.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.storage.repository import JsonRepository, FirestoreRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("migrate_to_firestore")


def sanitize_doc_id(raw_id: str) -> str:
    """Converts a standard identifier or key into a safe, deterministic Firestore doc ID."""
    return raw_id.strip().replace(" ", "_").replace(":", "_").replace("/", "_")


def build_migration_payloads(repo: JsonRepository) -> dict[str, dict[str, dict[str, Any]]]:
    """
    Extracts and formats all verified corpus records with deterministic document IDs.
    Returns a dict of: {collection_name: {doc_id: doc_dict}}
    """
    payloads: dict[str, dict[str, dict[str, Any]]] = {
        FirestoreRepository.COLLECTION_STANDARDS: {},
        FirestoreRepository.COLLECTION_EVIDENCE: {},
        FirestoreRepository.COLLECTION_RELATIONSHIPS: {},
        FirestoreRepository.COLLECTION_SOURCES: {},
        FirestoreRepository.COLLECTION_BENCHMARKS: {},
        FirestoreRepository.COLLECTION_CERTIFICATION: {},
    }

    # 1. Standards
    for std in repo.standards:
        doc_id = sanitize_doc_id(std.standard_id)
        data = std.model_dump()
        payloads[FirestoreRepository.COLLECTION_STANDARDS][doc_id] = data

    # 2. Evidence
    for ev in repo.evidence:
        doc_id = sanitize_doc_id(ev.evidence_id)
        data = ev.model_dump()
        payloads[FirestoreRepository.COLLECTION_EVIDENCE][doc_id] = data

    # 3. Relationships
    for rel in repo.relationships:
        doc_id = sanitize_doc_id(f"{rel.from_standard}_{rel.to_standard}_{rel.relationship_type}")
        data = rel.model_dump()
        payloads[FirestoreRepository.COLLECTION_RELATIONSHIPS][doc_id] = data

    # 4. Sources
    for src in repo.sources:
        doc_id = sanitize_doc_id(src.source_id)
        data = src.model_dump()
        payloads[FirestoreRepository.COLLECTION_SOURCES][doc_id] = data

    # 5. Benchmark Cases
    for case in repo.benchmark_cases:
        doc_id = sanitize_doc_id(case.id)
        data = case.model_dump()
        payloads[FirestoreRepository.COLLECTION_BENCHMARKS][doc_id] = data

    # 6. Certification
    for rule in repo.certification:
        doc_id = sanitize_doc_id(f"{rule.get('standard_id', '')}_{rule.get('rule_type', '')}")
        payloads[FirestoreRepository.COLLECTION_CERTIFICATION][doc_id] = rule

    return payloads


def run_migration(
    data_dir: str = "data",
    dry_run: bool = False,
    project_id: str | None = None,
    database: str = "(default)",
    credentials_path: str | None = None,
) -> bool:
    logger.info("Loading local verified corpus from '%s'...", data_dir)
    repo = JsonRepository(data_dir=data_dir)
    payloads = build_migration_payloads(repo)

    total_records = sum(len(docs) for docs in payloads.values())
    logger.info(
        "Prepared %d records across %d collections for migration:",
        total_records,
        len(payloads),
    )
    for col_name, docs in payloads.items():
        logger.info("  - %-18s: %d documents", col_name, len(docs))

    if dry_run:
        logger.info("DRY-RUN MODE ENABLED: No changes will be written to Firestore.")
        for col_name, docs in payloads.items():
            print(f"\n=== Collection: {col_name} ({len(docs)} docs) ===")
            for doc_id, data in docs.items():
                print(f"  Doc ID: {doc_id} -> {list(data.keys())}")
        logger.info("Dry-run validation complete. All %d records validated successfully.", total_records)
        return True

    # Live migration to Firestore
    try:
        from google.cloud import firestore
        from google.oauth2 import service_account

        kwargs: dict[str, Any] = {"database": database}
        if project_id:
            kwargs["project"] = project_id

        if credentials_path and os.path.exists(credentials_path):
            kwargs["credentials"] = service_account.Credentials.from_service_account_file(credentials_path)

        db = firestore.Client(**kwargs)
        logger.info("Connected to Firestore (Project: %s, Database: %s)", project_id or "default", database)

        # Batch upserts
        for col_name, docs in payloads.items():
            batch = db.batch()
            count = 0
            for doc_id, data in docs.items():
                doc_ref = db.collection(col_name).document(doc_id)
                batch.set(doc_ref, data, merge=True)
                count += 1
            batch.commit()
            logger.info("Successfully committed %d documents to '%s'", count, col_name)

        logger.info("Firestore migration completed successfully with %d total records upserted.", total_records)
        return True

    except Exception as exc:
        logger.error("Firestore migration failed: %s", exc)
        return False


def main():
    parser = argparse.ArgumentParser(description="Deterministic Firestore migration for SpecWise corpus")
    parser.add_argument("--dry-run", action="store_true", help="Validate and display payloads without writing to Firestore")
    parser.add_argument("--data-dir", default="data", help="Local directory containing seed JSON files")
    parser.add_argument("--project", default=os.getenv("FIRESTORE_PROJECT_ID"), help="GCP project ID")
    parser.add_argument("--database", default=os.getenv("FIRESTORE_DATABASE", "(default)"), help="Firestore database name")
    parser.add_argument("--credentials", default=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"), help="Path to GCP service account JSON")

    args = parser.parse_args()
    success = run_migration(
        data_dir=args.data_dir,
        dry_run=args.dry_run,
        project_id=args.project,
        database=args.database,
        credentials_path=args.credentials,
    )
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
