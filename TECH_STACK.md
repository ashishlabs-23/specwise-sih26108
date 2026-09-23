# TECH_STACK.md

## MVP stack

- Python 3.11+
- FastAPI
- Pydantic
- PyMuPDF
- custom BM25 implementation
- optional Sentence Transformers dense retrieval
- optional CrossEncoder reranking
- JSON prototype data
- pytest
- Docker / Docker Compose

## Why JSON first?

The prototype needs transparent, inspectable, source-traceable data before a larger database is introduced.

## Future scale

PostgreSQL + pgvector can replace the JSON repository while keeping the same API/data contracts.

## Deliberately excluded from MVP

- blockchain
- multi-agent orchestration
- Kafka
- Kubernetes
- Neo4j
- Elasticsearch
- Celery/Redis
- custom LLM training

Only add these after a measured requirement justifies them.

## UI

UI is intentionally deferred. The API is the stable contract for the future frontend.
