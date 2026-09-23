# BIS Standards Recommendation & Assurance Engine

## Smart India Hackathon 2026 — SIH26108

Backend/core prototype for SIH26108. UI is intentionally deferred until the engine is tested.

## Core workflow

```text
Tender / Product Description
        ↓
Document Processing + OCR
        ↓
Atomic Requirement Extraction
        ↓
Hybrid Retrieval: Exact-ID + BM25 + Dense
        ↓
RRF Fusion + Cross-Encoder Reranking
        ↓
Applicability + Lifecycle
        ↓
Coverage + Related Standards
        ↓
Certification / QCO lookup
        ↓
Evidence + Conflict Gate
        ↓
RECOMMEND / REVIEW / ABSTAIN / OUT_OF_CORPUS
        ↓
Evidence-Traceable Report
```

## Important non-hallucination rule

This repository does NOT claim:
- the complete BIS catalogue;
- a live BIS API;
- complete QCO/certification coverage;
- calibrated confidence probabilities;
- production government integration;
- continuous learning from officer feedback.

The prototype data is small and source-traceable.

## Included verified-source prototype examples

The seed corpus includes pump-sector examples sourced from BIS material:
- IS 14220:2018 — Openwell Submersible Pumpsets
- IS 8034:2018 — Submersible Pumpsets
- IS 9079:2018 — Monoset Pumps for Clear, Cold Water for Agricultural and Water Supply
- IS 14536:2018 — Selection, Installation, Operation and Maintenance of Submersible Pumpset — Code of Practice

The repository stores source URLs and evidence notes. It does not infer unsupported lifecycle or certification conclusions.

## Architecture rule

AI is used for understanding/explanation. Regulatory facts are controlled by structured data and deterministic checks.

## Local run

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

uvicorn app.api.main:app --reload --port 8000
```

API docs:
http://127.0.0.1:8000/docs

CLI:

```bash
python -m cli.main "openwell submersible pumpset for agricultural irrigation"
```

Tests:

```bash
pytest -q
```

Benchmark:

```bash
python -m evaluation.run_benchmark
```

## API example

```bash
curl -X POST http://127.0.0.1:8000/api/v1/analyze ^
  -H "Content-Type: application/json" ^
  -d "{"text":"openwell submersible pumpset for agricultural irrigation"}"
```

## Project structure

```text
app/
  api/
  extraction/
  graph/
  policy/
  report/
  retrieval/
  storage/
data/
cli/
evaluation/
tests/
docs/
```

## Future

After the core engine is validated:
1. expand the verified corpus;
2. benchmark retrieval;
3. strengthen applicability/lifecycle;
4. add UI;
5. perform red-team testing;
6. build the final SIH demo.

Always update documentation to match actual implementation state.
