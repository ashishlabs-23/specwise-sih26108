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

| Layer | Component | Status |
|:---|:---|:---|
| **Parsing** | Regex requirement extraction (IS-refs, power, voltage, flow) | ✅ IMPLEMENTED |
| **Parsing** | PyMuPDF text-layer PDF extraction | ✅ IMPLEMENTED |
| **Parsing** | Scanned / image-only PDF (OCR) | 🔷 FUTURE — raises explicit error |
| **Retrieval** | Exact IS-number identifier match | ✅ IMPLEMENTED |
| **Retrieval** | BM25 lexical retrieval | ✅ IMPLEMENTED |
| **Retrieval** | Reciprocal Rank Fusion (RRF) | ✅ IMPLEMENTED (fuses exact+BM25; dense when enabled) |
| **Retrieval** | Dense neural embeddings (sentence-transformers) | 🔷 FUTURE — disabled in deployment (`ENABLE_DENSE=false`) |
| **Retrieval** | Cross-encoder reranker | 🔷 FUTURE — disabled in deployment (`ENABLE_RERANKER=false`) |
| **Policy** | Role-aware applicability gates (inclusion/exclusion/evidence) | ✅ IMPLEMENTED |
| **Policy** | Lifecycle event-state assessment | ✅ IMPLEMENTED |
| **Policy** | Requirement-level coverage (per-requirement, not global) | ✅ IMPLEMENTED |
| **Policy** | `unverified_reference` gap detection for out-of-corpus IS citations | ✅ IMPLEMENTED |
| **Policy** | 4-state evidence routing (RECOMMEND/REVIEW/ABSTAIN/OUT_OF_CORPUS) | ✅ IMPLEMENTED |
| **Graph** | Normative reference graph traversal (max 2 hops) | ✅ IMPLEMENTED |
| **Certification** | QCO/BIS certification lookup with unverified-state guard | ✅ IMPLEMENTED |
| **Report** | Evidence-traceable HTML audit report | ✅ IMPLEMENTED |
| **Multilingual** | Hindi/regional language tender support | 🔷 FUTURE — not yet implemented or tested |
| **Procurement** | REST API + JSON + HTML report output | ✅ IMPLEMENTED (MVP integration layer) |
| **Procurement** | Direct GeM/CPPP portal integration | 🔷 FUTURE — not implemented |
| **Corpus** | 7 verified MED-20 pump-sector standards | ✅ IMPLEMENTED |
| **Corpus** | Full BIS catalogue (all sectors) | 🔷 FUTURE — requires corpus expansion |

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

## 11. OCR

Current behavior: PyMuPDF extracts text layers.
If a page has no extractable text, `ocr_used = True` is set in the response flag,
and if NO pages yield text, a `ValueError` is raised:
> "No extractable PDF text. OCR integration is required for this document."

OCR is NOT currently implemented. The flag is informational.

## 12. Multilingual

Not implemented. English-only input.
Hindi/regional tender support is the next implementation layer.

## 13. Procurement Integration (MVP)

MVP output = REST API JSON + structured `AnalysisResponse` + HTML audit report.
This is the concrete procurement integration adapter for the prototype.

Direct GeM/CPPP portal integration is future work requiring portal API access.

## 14. AI / LLM

Current implementation uses deterministic/rule-assisted extraction.
No external LLM is required.

A future LLM adapter may improve extraction, but model output must be schema-constrained
and cannot invent standards or regulatory facts.

## 15. Security

Tender documents are untrusted input. No document text is treated as executable instructions.
