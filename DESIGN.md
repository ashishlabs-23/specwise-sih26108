# DESIGN.md — SpecWise SIH26108

## 1. Goal

Demonstrate SIH26108 as an evidence-grounded procurement standards assurance workflow.

The system must distinguish:
- candidate retrieval;
- applicability;
- lifecycle status;
- related standards;
- certification/QCO information;
- evidence;
- uncertainty.

## 2. Tiered Architecture Status

| Layer | Component | Status | Classification |
|:---|:---|:---|:---|
| **Parsing** | Regex requirement extraction (IS-refs, power, voltage, flow) | ✅ Verified | `CURRENT PROTOTYPE` |
| **Parsing** | PyMuPDF text-layer PDF extraction | ✅ Verified | `CURRENT PROTOTYPE` |
| **Parsing** | Scanned / image-only PDF (OCR detection & safe rejection) | ⚠️ Safe Gate Active | `DEPLOYMENT-CONSTRAINED` (OCR engine deferred) |
| **Retrieval** | Exact IS-number identifier match | ✅ Verified | `CURRENT PROTOTYPE` |
| **Retrieval** | BM25 lexical retrieval | ✅ Verified | `CURRENT PROTOTYPE` |
| **Retrieval** | Reciprocal Rank Fusion (RRF) | ✅ Verified | `CURRENT PROTOTYPE` (fuses exact + BM25) |
| **Retrieval** | Dense neural embeddings (sentence-transformers) | ⏸️ Code Provisioned | `DEPLOYMENT-CONSTRAINED` (disabled in deployment: `ENABLE_DENSE=false`) |
| **Retrieval** | Cross-encoder reranker | ⏸️ Code Provisioned | `DEPLOYMENT-CONSTRAINED` (disabled in deployment: `ENABLE_RERANKER=false`) |
| **Policy** | Role-aware applicability gates (inclusion/exclusion/evidence) | ✅ Verified | `CURRENT PROTOTYPE` |
| **Policy** | Lifecycle event-state assessment | ✅ Verified | `CURRENT PROTOTYPE` |
| **Policy** | Requirement-level coverage (per-requirement, not global) | ✅ Verified | `CURRENT PROTOTYPE` |
| **Policy** | `unverified_reference` gap detection for out-of-corpus IS citations | ✅ Verified | `CURRENT PROTOTYPE` |
| **Policy** | 4-state evidence routing (RECOMMEND/REVIEW/ABSTAIN/OUT_OF_CORPUS) | ✅ Verified | `CURRENT PROTOTYPE` |
| **Policy** | Independent AI Pass 2 Verification / Challenger Layer | 🔷 Roadmap Only | `ARCHITECTURAL / PLANNED` |
| **Policy** | Calibrated Numeric Confidence Scoring (40/30/30) | 🔷 Design Model | `ARCHITECTURAL / PLANNED` |
| **Graph** | Normative reference graph traversal (max 2 hops) | ✅ Verified | `CURRENT PROTOTYPE` |
| **Certification** | QCO/BIS certification lookup with unverified-state guard | ✅ Verified | `CURRENT PROTOTYPE` (verified corpus entries only) |
| **Certification** | Automated Real-Time Gazette / e-BIS QCO Sync | 🔷 Roadmap Only | `ARCHITECTURAL / PLANNED` |
| **Report** | Evidence-traceable HTML audit report | ✅ Verified | `CURRENT PROTOTYPE` |
| **Multilingual** | 5-Language Frontend UI Localization (EN, HI, KN, TA, TE) | ✅ Verified | `CURRENT PROTOTYPE` |
| **Multilingual** | Multilingual AI Inference (IndicTrans2) | 🔬 Research Track | `DEPLOYMENT-CONSTRAINED` (isolated experimental branch) |
| **Procurement** | REST API (`/api/v1/analyze`) + JSON + HTML report output | ✅ Verified | `CURRENT PROTOTYPE` (MVP integration layer) |
| **Procurement** | Direct GeM/CPPP portal integration (Extension / Webhook) | 🔷 Roadmap Only | `ARCHITECTURAL / PLANNED` |
| **Corpus** | Curated & verified domain corpus (10 standards, 18 evidence records) | ✅ Verified | `CURRENT PROTOTYPE` |
| **Corpus** | Full national BIS catalogue (20,000+ standards, all 15 Divisions) | 🔷 Roadmap Only | `ARCHITECTURAL / PLANNED` |

## 3. Deployed Pipeline (MVP — What Actually Runs)

```text
Input text / Tender PDF (text layer only)
               │
               ▼
1. Requirement Extraction (Regex — IS refs, power, voltage, flow; PyMuPDF for PDF)
               │
               ▼
2. Retrieval: Exact IS-ID Match + BM25 → RRF fusion
   [Dense embeddings + cross-encoder reranker: disabled in deployment]
               │
               ▼
3. Role-Aware Applicability Gates
   (product_terms / application_terms / exclusion_terms / evidence guard)
               │
               ▼
4. Lifecycle Assessment (event-state, not guessed binary)
               │
               ▼
5. Requirement-Level Coverage
   covered | partial | not_covered | unverified_reference
               │
               ▼
6. Normative Graph Traversal (max 2 hops)
               │
               ▼
7. Certification / QCO Lookup (always marked not_verified_in_prototype_corpus)
               │
               ▼
8. Evidence-State Decision Routing
   RECOMMEND | REVIEW | ABSTAIN | OUT_OF_CORPUS
               │
               ▼
9. Traceable HTML Report + JSON API Response
```

## 4. Decision States

Routing is based on evidence-state conditions, NOT numeric confidence thresholds.

| State | Trigger Condition |
|:---|:---|
| **RECOMMEND** | Single PRIMARY_PRODUCT_STANDARD scores strong + lifecycle supported + no coverage gaps + no conflicts |
| **REVIEW** | Multiple strong primaries, OR unverified IS references in tender, OR lifecycle warning, OR conflicts |
| **ABSTAIN** | Candidates retrieved but no primary standard scores strong |
| **OUT_OF_CORPUS** | No candidate above relevance floor — input is outside corpus domain |

No 40/30/30 weights. No ≥90 confidence publish thresholds. Evidence states only.

## 5. Coverage States (per requirement)

| State | Meaning |
|:---|:---|
| `covered` | Strong-applicability candidate with matched terms for this specific requirement |
| `partial` | Candidate is plausible but does not fully establish coverage for this requirement |
| `not_covered` | No candidate has sufficient applicability signal for this requirement |
| `unverified_reference` | Tender cites an IS number absent from the prototype corpus |

A single primary standard DOES NOT automatically cover all requirements.

## 6. Applicability

Retrieval similarity is not treated as proof.

Applicability checks product/category/domain terms and source-backed scope metadata.
These are transparent rules expanded only with evidence.

Role ceiling:
- PRIMARY_PRODUCT_STANDARD → up to `strong`
- CODE_OF_PRACTICE → at most `possible`
- TEST_METHOD → at most `possible`
- RELATED_STANDARD → at most `weak`

## 7. Lifecycle

Store lifecycle as events rather than a guessed current/withdrawn binary.

Example:
- IS 8034:2002 was revised to IS 8034:2018; withdrawal documented after 2019-04-04.
- 2026 BIS committee material lists revision work. That does not itself prove published editions are withdrawn.

Tender-cited historical editions (e.g., "IS 694-1990") remain distinct from
the current known edition ("IS 694:2010"). The system NEVER silently replaces
the tender's cited number.

## 8. Relationship Graph

MVP uses relational edges.
Maximum traversal = 2 hops.
Only verified relationships should be added.

## 9. Evidence

Every recommendation must be traceable:
Requirement → Candidate → Evidence.

Evidence stores: source_id, URL, page (where known), text, verified flag.

## 10. Certification / QCO

Safe wording only:
> "No verified certification/QCO mapping available in the current prototype knowledge base."

The system never infers mandatory or non-mandatory status without a confirmed gazette source.
All QCO entries are `not_verified_in_prototype_corpus` until a confirmed gazette is added.

## 11. OCR (`DEPLOYMENT-CONSTRAINED`)

Current behavior: PyMuPDF extracts selectable text layers from digital PDFs.
If a page has no extractable text, `ocr_used = True` is set in the response flag,
and if NO pages yield text, a `ValueError` is raised:
> "No extractable PDF text. OCR integration is required for this document."

OCR extraction (e.g. Tesseract/Surya) is NOT currently enabled in deployment. The system provides safe detection and explicit failure reporting rather than false extraction.

## 12. Multilingual Support (`CURRENT PROTOTYPE` UI / `RESEARCH TRACK` AI)

- **Frontend UI Localization:** Fully implemented across 5 languages: English (`en`), Hindi (`hi`), Kannada (`kn`), Tamil (`ta`), Telugu (`te`).
- **Multilingual AI Inference:** An isolated experimental research track (IndicTrans2 200M) exists on evaluation branches. While Kannada preprocessing was validated, known technical semantic drift prevents merging AI inference into the production main branch at this stage.

## 13. Procurement Integration (MVP — `CURRENT PROTOTYPE`)

MVP output = REST API JSON (`/api/v1/analyze`) + structured `AnalysisResponse` + downloadable HTML audit report.
This is the concrete procurement integration adapter for the prototype.

Direct GeM/CPPP portal integration (browser extension / API webhooks) is `ARCHITECTURAL / PLANNED` future work.

## 14. AI / Verification Architecture (`CURRENT PROTOTYPE` vs `ARCHITECTURAL / PLANNED`)

- **Current Trust Model (`CURRENT PROTOTYPE`):** Deterministic NLP parameter extraction + rigorous deterministic rule gates (applicability, inclusion/exclusion, event-state lifecycle, requirement-level coverage, conflict checking). No ungrounded LLM inference is required in production.
- **AI Pass 1 & Pass 2 Independent Challenger (`ARCHITECTURAL / PLANNED`):** The dual-agent LLM cross-verification diagram in the presentation represents our target multi-model consensus architecture. In the current prototype, deterministic policy gates serve as the reliable verification mechanism.
- **Calibrated Numeric Confidence (`ARCHITECTURAL / PLANNED`):** The 40% retrieval + 30% AI + 30% evidence formula is a design-phase metric. The current working prototype enforces an evidence-controlled 4-state routing model (`RECOMMEND`, `REVIEW`, `ABSTAIN`, `OUT_OF_CORPUS`).

## 15. Security

Tender documents are untrusted input. No document text is treated as executable instructions.
