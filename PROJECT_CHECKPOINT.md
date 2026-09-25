# SIH26108 PROJECT CHECKPOINT

## Current Phase
Core Engine Frozen & Verified. Multi-Standard Tender Ingestion & Live Firestore Integration Active.

## Status
- **Core Engine**: Fully tested, validated, and frozen under determinism invariants.
- **Corpus**: 10 verified standards (Pumps & Key Tender-Cited Accessories), 18 evidence records, 5 verified relationships, 8 source documents.
- **Tender-Cited Expansions**: Added verified records for IS 1239:1990 (GI Pipes), IS 694:2010 (PVC Submersible Cables), IS 1554:1988 (Armored Cables) cited in Karnataka Ganga Kalyana Scheme tender.
- **Storage Layer**: Dual-mode repository active (Local JSON + Google Cloud Firestore live sync).
- **Validation**:
  - 115/115 pytest tests passing (17 skipped for optional external models).
  - 10/10 benchmark cases passing (100% decision and candidate accuracy).
  - 100% deterministic routing across evaluation cases.
- **Freeze Invariants**: Verified via `scripts/freeze_check.py` and `scripts/validate_data.py`.

## Frozen Principles
1. Retrieval is candidate generation; policy/evidence gates determine applicability.
2. Verified provenance required for every standard recommendation.
3. Unverified QCO/certification data is marked `not_verified_in_prototype_corpus` with source access restrictions.
4. Primary standards and Codes of Practice / Related / Test standards are strictly separated with role ceilings.
5. Deterministic four-state decision routing: `RECOMMEND`, `REVIEW`, `ABSTAIN`, `OUT_OF_CORPUS`.

## Current Scope & UI Readiness
- Backend APIs (`/api/v1/analyze`, `/api/v1/health`, `/api/v1/resources`, `/api/v1/benchmark/run`) fully functional and contract-tested.
- Frontend React/Vite dashboard ready for live tender parsing, evidence drill-down, graph exploration, and export reports.
