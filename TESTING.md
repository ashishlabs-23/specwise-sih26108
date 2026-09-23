# TESTING.md

## Automated

```bash
pytest -q
python scripts/validate_data.py
python -m evaluation.run_benchmark
```

## API

```bash
uvicorn app.api.main:app --reload --port 8000
```

Open:

http://127.0.0.1:8000/docs

## Manual scenarios

### 1. Supported / evidence-backed
`openwell submersible pumpset for agricultural irrigation`

Expected:
- requirements extracted;
- IS 14220:2018 appears as a candidate;
- evidence is returned;
- lifecycle revision note does not automatically mean withdrawal.

### 2. Unsupported
`advanced underwater robotic mining vehicle`

Expected:
`OUT_OF_CORPUS` or `ABSTAIN`.

### 3. Explicit standard reference
`Please check IS 8034:2018 for a submersible pumpset`

Expected:
- exact-ID path appears in retrieval provenance.

### 4. PDF
Pass a local text-based PDF through `file_path`.

Expected:
- text extracted;
- page markers preserved where available;
- OCR flag is true only when no page text is extractable.

## Final acceptance

- pytest passes;
- provenance validation passes;
- API starts;
- supported query returns source evidence;
- unsupported query does not invent an IS number;
- UI is not required yet.
