# TECH_STACK.md — SpecWise SIH26108

## MVP Stack (Active in Deployment)

| Component | Technology | Notes |
|:---|:---|:---|
| **Backend** | Python 3.11, FastAPI, Pydantic v2, Uvicorn | Core API runtime |
| **Document Processing** | PyMuPDF (fitz) | Text-layer PDF extraction only (no OCR) |
| **Retrieval** | Custom BM25 implementation | Lexical lexical scoring |
| **Retrieval** | Exact IS-number identifier match | Regex-based corpus lookup |
| **Retrieval** | RRF fusion | Fuses exact-id + BM25 (+ dense when enabled) |
| **Data** | JSON prototype corpus (`data/standards_seed.json`) | Frozen, validated, version-controlled |
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS | Firebase Hosting |
| **Database** | Google Cloud Firestore | Production knowledge base backend |
| **Hosting** | Firebase Hosting (frontend), Render (backend) | Free-tier deployment |
| **Testing** | pytest | Unit + integration + API tests |
| **Validation** | `scripts/validate_data.py`, `scripts/freeze_check.py` | Corpus integrity and determinism |

## Provisioned / Future (Code Exists, Disabled in Deployment)

| Component | Technology | Flag / Condition |
|:---|:---|:---|
| **Dense Retrieval** | sentence-transformers (`all-MiniLM-L6-v2`) | `ENABLE_DENSE=true` — disabled (free tier) |
| **Cross-encoder Reranker** | cross-encoder (`ms-marco-MiniLM-L-6-v2`) | `ENABLE_RERANKER=true` — disabled (free tier) |
| **OCR** | Not yet integrated | Raises explicit error for image-only PDFs |
| **Multilingual** | Not yet implemented | English-only input |
| **Procurement Portal Integration** | REST API output (MVP layer) | GeM/CPPP direct integration: future |

## Why JSON-First?

The prototype needs transparent, inspectable, source-traceable data before a larger database is introduced.
JSON enables full offline operation and reproducible corpus validation.

## Future Scale (If Required by Measurement)

- PostgreSQL + pgvector can replace the JSON repository while keeping the same API/data contracts.
- Full BIS catalogue ingestion requires a structured extraction pipeline per sector.

## Deliberately Excluded from MVP

- blockchain
- multi-agent orchestration
- Kafka / Celery / Redis
- Kubernetes
- Neo4j / Elasticsearch
- custom LLM fine-tuning

Only add these after a measured requirement justifies them.
