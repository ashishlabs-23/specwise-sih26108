# DESIGN.md

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

## 2. Design

```text
Input
→ Parse
→ Requirements
→ Validate
→ Normalize
→ Exact/BM25/Dense
→ RRF
→ Rerank
→ Applicability
→ Lifecycle
→ Coverage
→ Relationship Expansion
→ Certification/QCO
→ Evidence/Conflict Gate
→ Routing
→ Report
```

## 3. Decision states

RECOMMEND:
Evidence and required policy checks pass.

REVIEW:
A plausible result exists but ambiguity/conflict/missing evidence remains.

ABSTAIN:
Evidence is insufficient.

OUT_OF_CORPUS:
The prototype corpus does not contain a supported candidate.

## 4. Applicability

Retrieval similarity is not treated as proof.

MVP applicability checks product/category/domain terms and source-backed scope metadata. These are transparent rules and must be expanded only with evidence.

## 5. Lifecycle

Store lifecycle as events rather than a guessed current/withdrawn binary.

Example:
- IS 8034:2002 was revised to IS 8034:2018 and old edition withdrawal was documented after 2019-04-04 by BIS implementation guidance.
- 2026 BIS committee material lists revision work for IS 8034:2018 and IS 14220:2018. That does not itself prove that the published editions have been withdrawn.

## 6. Relationship graph

MVP uses relational edges.
Maximum traversal = 2 hops.
Only verified relationships should be added.
No iterative feedback loop is used.

## 7. Evidence

Every recommendation should be traceable to:
Requirement → Candidate → Evidence.

Evidence stores source, URL, page where known, text and verification flag.

## 8. Confidence

MVP uses evidence states rather than a calibrated probability:
HIGH → RECOMMEND
MEDIUM → REVIEW
LOW → ABSTAIN

No arbitrary confidence weights are claimed.

## 9. AI

The current implementation uses deterministic/rule-assisted extraction so the project can run without an external LLM.

A future LLM adapter may improve extraction, but model output must be schema constrained and cannot invent standards or regulatory facts.

## 10. Reporting

Reports are generated from structured analysis state, not free-form model output.

## 11. Security

Tender documents are untrusted input. No document text is treated as executable instructions.
