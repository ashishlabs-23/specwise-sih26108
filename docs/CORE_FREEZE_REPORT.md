# SIH26108 CORE ENGINE FREEZE REPORT

## 1. TEST RESULTS
- **Pytest Suite**: `61 passed in 0.42s` (100% pass rate across unit, applicability, lifecycle, graph traversal, retrieval, report, and extraction tests).
- **Data Validation (`scripts/validate_data.py`)**: `Validated 7 standards, 15 evidence records, 5 relationships.` Zero schema or orphan reference errors.
- **Benchmark Run (`evaluation/run_benchmark.py`)**:
  - `candidate_hit_rate`: **1.0 (100%)**
  - `decision_hit_rate`: **1.0 (100%)**
  - `cert_hit_rate`: **1.0 (100%)**
  - Total evaluation cases tested: **10 / 10 passed**

## 2. END-TO-END RESULTS
All 10 target workflow pathways were verified end-to-end:
1. **Supported Recommendation**: `openwell-primary-recommend` correctly recommends `IS 14220:2018` with strong applicability and evidence gating.
2. **Multiple/Ambiguous Candidate**: `ambiguous-submersible-generic` honestly abstains (`ABSTAIN`) while preserving retrieved candidates without arbitrary guessing.
3. **OUT_OF_CORPUS Handling**: `unsupported-out-of-corpus` queries (e.g. robotic mining) correctly trigger `OUT_OF_CORPUS` routing with empty candidates and clear explanation.
4. **Explicit IS Lookup**: Domain-agnostic regex and exact ID retrieval resolve `IS 14220` and `IS 8034` queries directly via `exact_id` path.
5. **Lifecycle Handling**:
   - `revision_under_print` correctly preserved as `supported` per BIS committee evidence.
   - `withdrawn_after_revision` properly raises a `warning` state.
6. **Related-Standard Traversal**:
   - Primary candidate `IS 8034:2018` graph expansion surfaces `IS 9283:2024` (normative motor reference), `IS 14536:2018` (normative CoP), and `IS 11346:2002` (test method) with exact hop counts.
   - Related standards and Codes of Practice are strictly prevented from masquerading as primary product recommendations.
7. **Certification/QCO Handling**:
   - Unverified/proposed QCOs resolve safely as `not_verified_in_prototype_corpus` with `SOURCE ACCESS RESTRICTED` notice.
   - No false negative inference ("certification not required") is made.
8. **PDF Input Extraction**: PyMuPDF extraction handles multi-page document streams, flags OCR requirements when text layers are absent, and flows into requirement extraction.
9. **Evidence/Report Generation**: HTML audit reports generate with all required sections (`decision`, `requirements`, `primary`, `related-cands`, `coverage`, `gaps`, `conflicts`, `graph`, `evidence`, `timings`) and provenance citations.
10. **API Endpoints**: FastAPI endpoints (`/api/v1/health`, `/api/v1/analyze`, `/api/v1/standards/{id}`) validated.

## 3. DETERMINISM RESULT
- **Determinism Check**: **100% IDENTICAL across 2x consecutive runs on all benchmark cases**.
- Decision outcomes, candidate rankings, related standard graph hops, and strong applicability sets are fully deterministic.

## 4. DATA STATUS
- **Corpus State**: **FROZEN (7 standards, 15 evidence items, 5 verified relationships)**.
- Every standard record contains verified provenance citations (`source_id`, official URL, extract text, and verification date).
- No invented or ungrounded BIS claims exist in the dataset.

## 5. KNOWN LIMITATIONS
1. **Corpus Domain Scope**: Frozen prototype corpus covers the pump domain (`MED 20`). Out-of-domain queries properly route to `OUT_OF_CORPUS`.
2. **QCO Gazette Verification**: Official DPIIT gazette notification numbers and enforcement dates remain unverified in public open data and are marked `not_verified_in_prototype_corpus`.
3. **Embeddings/Cross-Encoder**: Dense retrieval and Cross-Encoder reranking are disabled in default lightweight mode; BM25 and exact ID paths provide deterministic retrieval.

## 6. FAILURES
- **None**. 0 test failures, 0 validation errors, 0 benchmark regressions.

## 7. FINAL STATUS
**READY FOR UI**
The core recommendation engine, deterministic policy gates, graph traversal, and reporting modules are verified, robust, and frozen for UI integration.
