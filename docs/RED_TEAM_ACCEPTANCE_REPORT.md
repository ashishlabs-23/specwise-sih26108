# RED-TEAM + FINAL ACCEPTANCE REPORT
## SIH26108 SPECWISE — BIS Standards Recommendation Engine

**Date:** 2026-09-23  
**Scope:** Complete red-team and final acceptance test covering backend edge cases, PDF handling, and API contract validation.  
**Result:** ✅ **100 / 100 tests pass** (39 red-team + 61 prior)

---

## Test Suite Location

`tests/test_redteam.py` — 39 test cases grouped into 5 classes:
- `TestBackendEdgeCases` — Cases 1–20
- `TestPdfEdgeCases` — Cases 21–25
- `TestAPIEdgeCases` — Cases 26–30
- `TestDeterminismDoubleRun` — 4 critical paths × 2 runs
- `TestInvariants` — Cross-cutting quality guards

---

## BACKEND CASES (1–20)

| # | Case | Input | Expected | Pass? |
|---|------|-------|----------|-------|
| 1 | Empty input | `""` | `ValueError` raised | ✅ |
| 2 | Whitespace-only input | `"   \t\n  "` | `ValueError` raised | ✅ (defect fixed) |
| 3 | Very long input (10 000 chars) | Repeated valid query | Structured response | ✅ |
| 4 | Malformed/nonsense text | `"xqzpq zzplf mmrkl @@##"` | `OUT_OF_CORPUS` or `ABSTAIN` | ✅ |
| 5 | Unknown IS number | `"IS 99999:2099"` | Not hallucinated | ✅ |
| 6 | Withdrawn/superseded standard | `"IS 8034:1974"` | 1974 edition absent; no hallucination | ✅ |
| 7 | Revision/amendment query | `"Amendment No. 1 to IS 14220:2018"` | IS 14220:2018 surfaces correctly | ✅ |
| 8 | Ambiguous product | `"submersible pump for water supply"` | `RECOMMEND`/`REVIEW`/`ABSTAIN` | ✅ |
| 9 | Multiple product requirements | Both IS 8034 and IS 9079 in query | Structured; no hallucination | ✅ |
| 10 | Missing attributes | `"pump standard required"` | Structured response + reasons | ✅ |
| 11 | Unsupported domain | `"advanced underwater robotic mining vehicle"` | `OUT_OF_CORPUS`, 0 candidates | ✅ |
| 12 | Prompt injection | IGNORE PREVIOUS INSTRUCTIONS + real query | IS 99999 absent; no false cert claim | ✅ |
| 13 | Invalid tender date | `tender_date=None` | No crash | ✅ |
| 14 | Missing cert/QCO evidence | IS 9079 query | `not_verified_in_prototype_corpus` | ✅ |
| 15 | Unverified QCO record | IS 8034 + "ISI mark mandatory" | `not_verified_in_prototype_corpus` + restriction notice | ✅ |
| 16 | Missing relationship data | `expand([], [])` | Returns `[]`, no crash | ✅ |
| 17 | Relationship cycle | A→B→A synthetic cycle | Terminates; hop ≤ 2 | ✅ |
| 18 | More than 2 graph hops | Live corpus traversal | All hops ≤ 2 | ✅ |
| 19 | Repeated identical query | Same query × 2 | Identical decision + candidates | ✅ |
| 20 | Missing/corrupt dataset | Empty-structure corpus | `OUT_OF_CORPUS`, 0 candidates | ✅ (test bug fixed) |

---

## PDF CASES (21–25)

| # | Case | Input | Expected | Pass? |
|---|------|-------|----------|-------|
| 21 | Valid text PDF | Tender spec PDF | Structured response | ✅ |
| 22 | Empty PDF (blank page) | No text layer | `ValueError: No extractable PDF text` | ✅ |
| 23 | Malformed PDF (corrupt bytes) | Random binary | Exception raised | ✅ |
| 24 | Scanned/OCR PDF (image-only) | White rect page | `ValueError: No extractable PDF text` | ✅ |
| 25 | Invalid file type | `.docx` file | `ValueError: Unsupported file type` | ✅ |

---

## API CASES (26–30)

| # | Case | Input | Expected Status | Pass? |
|---|------|-------|-----------------|-------|
| 26 | Invalid JSON | `{ this is not valid }` | HTTP 422 | ✅ |
| 27 | Missing required fields | `{}` | HTTP 400 or 422 | ✅ |
| 28 | Unknown endpoint | `GET /api/v1/nonexistent` | HTTP 404 | ✅ |
| 29 | Backend unavailable (unit) | Engine raises `RuntimeError` | HTTP 400 | ✅ |
| 30 | Server error handling | Engine raises unexpected `Exception` | HTTP 500; no raw traceback | ✅ |

---

## DETERMINISM DOUBLE-RUN

| Query | Run 1 | Run 2 | Match? |
|-------|-------|-------|--------|
| openwell submersible pumpset | RECOMMEND | RECOMMEND | ✅ |
| borewell submersible pumpset | RECOMMEND | RECOMMEND | ✅ |
| advanced underwater robotic vehicle | OUT_OF_CORPUS | OUT_OF_CORPUS | ✅ |
| submersible pump for water supply | same | same | ✅ |

---

## INVARIANTS VERIFIED

| Invariant | Status |
|-----------|--------|
| Every RECOMMEND has ≥ 1 evidence record | ✅ |
| Report HTML contains all 6 required sections | ✅ |
| `GET /api/v1/health` returns `status=ok`, `standards_loaded > 0` | ✅ |
| `GET /api/v1/standards/IS 8034:2018` returns 200 with standard data | ✅ |
| `GET /api/v1/standards/IS 00000:9999` returns 404 | ✅ |

---

## DEFECTS FOUND AND FIXED

### Defect 1 — Whitespace-only input silently processed (Case 2)
- **Symptom:** `engine.analyze(AnalysisRequest(text="   "))` returned a structured BM25 result instead of raising.
- **Root cause:** `_input()` in `app/engine.py` tested `if request.text:` — a whitespace string is truthy in Python.
- **Fix:** Changed to `if request.text is not None:` with an explicit `not request.text.strip()` guard that raises `ValueError("Input text must not be empty or whitespace-only.")`.

### Defect 2 — Case 20 test used wrong JSON structure (test bug, not engine bug)
- **Symptom:** Test wrote `[]` as `standards_seed.json` but `JsonRepository` expects `{"standards": [], "evidence": [], ...}`.
- **Fix:** Updated test to write the correct dict-with-keys structure matching the actual repository format.

---

## FINAL TEST COUNTS

```
pytest -q
100 passed, 1 warning in 1.10s

  ├── 61  prior tests (corpus, engine, applicability, lifecycle, report, extraction)
  └── 39  red-team tests (30 cases + 4 determinism × 2 + 5 invariants)

validate_data.py:    7 standards, 15 evidence records, 5 relationships — PASS
evaluation benchmark: 10/10 cases, 100% decision + candidate + cert accuracy
```

---

## SAFETY PROPERTIES CONFIRMED

| Property | Verified |
|----------|----------|
| No hallucinated IS number ever enters a recommendation | ✅ |
| No `cert.state = "verified"` in prototype corpus | ✅ |
| `QCO_PROPOSED` always carries SOURCE ACCESS RESTRICTED notice | ✅ |
| Primary and related/CoP/test standards strictly separated | ✅ |
| `OUT_OF_CORPUS` / `ABSTAIN` / `REVIEW` / `RECOMMEND` exclusive and exhaustive | ✅ |
| Graph traversal bounded at 2 hops | ✅ |
| Deterministic output for identical inputs | ✅ |
| Empty/whitespace text rejected before retrieval | ✅ |
| Prompt injection treated as plain text; no behavioral change | ✅ |
| API error responses are structured JSON, never raw tracebacks | ✅ |
