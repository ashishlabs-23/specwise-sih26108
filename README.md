# SpecWise — Evidence-Grounded Indian Standards Recommendation & Assurance Engine

**Smart India Hackathon 2026 Prototype · Problem Statement: SIH26108**

> **Disclaimer:** SpecWise is an independent hackathon prototype developed for SIH26108. It is not an official Bureau of Indian Standards (BIS) portal or product, nor does it claim live access to the full national standards database.

---

## Live Deployment

```text
┌─────────────────────────────────────────────────────────────┐
│  Firebase Hosting (Next.js App)                             │
│  https://specwise-sih26108.web.app                          │
└──────────────────────────────┬──────────────────────────────┘
                               │  HTTPS API
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  Render Web Service (FastAPI Engine)                        │
│  https://specwise-sih26108.onrender.com                     │
│  Interactive API Docs: .../docs                             │
└──────────────────────────────┬──────────────────────────────┘
                               │  Google Cloud SDK
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  Google Cloud Firestore (Production Knowledge Base)         │
│  7 Standards · 15 Evidence · 5 Relationships · 5 Sources   │
└─────────────────────────────────────────────────────────────┘
```

* **Frontend App:** [https://specwise-sih26108.web.app](https://specwise-sih26108.web.app)
* **Backend API:** [https://specwise-sih26108.onrender.com](https://specwise-sih26108.onrender.com)
* **API Documentation (Swagger UI):** [https://specwise-sih26108.onrender.com/docs](https://specwise-sih26108.onrender.com/docs)

---

## 1. SIH26108 Problem Statement

Government buyers, public procurement officers, MSMEs, and tender creators frequently struggle to identify the exact applicable Indian Standards (BIS) for technical goods and equipment:

* **Vocabulary Mismatch:** Tender descriptions use commercial trade jargon (e.g. *"5 HP openwell submersible pump for farm irrigation"*) that does not match formal standard titles.
* **Citation Errors & Legal Risk:** Referencing incorrect or superseded standards leads to non-compliant tenders, rejected bids, and procurement delays.
* **Ungrounded AI Hallucinations:** Generic LLMs often hallucinate invalid standard numbers or fabricate mandatory compliance mandates without evidence.
* **Component & Normative Gaps:** Primary equipment standards often depend on companion specifications (e.g. motor specs, hydraulic test acceptance codes, and installation practices) that buyers omit.

**SIH26108 Goal:** Build a reliable, evidence-grounded decision support system that maps procurement specifications to applicable Indian Standards while handling technical requirements, verified evidence, related standards, certification status, and explicit uncertainty.

---

## 2. Our Solution

SpecWise implements a dual-layer architectural philosophy:

1. **AI for Language & Requirement Parsing:** Natural language processing parses procurement text or uploaded tender PDFs to isolate structured parameters (product category, power ratings, discharge flow, and application domain).
2. **Deterministic Checks for Regulatory Truth:** Standards applicability, lifecycle validity, and normative references are evaluated exclusively through deterministic rule gates and verified BIS publication evidence.

If specifications are ambiguous or outside the domain, SpecWise explicitly declines false certainty through structured four-state decision routing.

---

## 3. How It Works (Actual Implemented Pipeline)

```text
User Text Description / Tender PDF
               │
               ▼
1. Requirement Extraction (Regex / Rule Parameter Isolation & PyMuPDF Text Layer Extraction)
               │
               ▼
2. Retrieval — Deployed MVP: Exact IS-Identifier Match + BM25 Lexical Scoring
   [Future / Provisioned: Dense Neural Embeddings + Cross-Encoder Reranker (disabled)]
               │
               ▼
3. Deterministic Applicability Gates (Inclusion / Exclusion Terms & Evidence Grounding Checks)
               │
               ▼
4. Requirement-Level Coverage Assessment
   (covered | partial | not_covered | unverified_reference — per requirement, not global)
               │
               ▼
5. Normative Knowledge Graph Traversal (Max 2 Hops: Motors, Codes of Practice, Test Standards)
               │
               ▼
6. Certification & QCO Verification (Regulatory notices tagged with verification status)
               │
               ▼
7. Evidence-State Decision Synthesis (RECOMMEND, REVIEW, ABSTAIN, OUT_OF_CORPUS)
               │
               ▼
8. Traceable Output & Audit Report Generation (Interactive UI & Standalone HTML Report)
```

---

## 4. The Four Decision States

To ensure safety and prevent misleading recommendations in public procurement, SpecWise routes every query into one of four unambiguous states:

| Decision State | Meaning | Trigger Condition |
| :--- | :--- | :--- |
| **`RECOMMEND`** | **Definitive Match** | Input matches primary standard scope, satisfies deterministic gates, and has verified evidence citations. |
| **`REVIEW`** | **Human Review Needed** | Multiple candidate standards are plausible or specific operating parameters require engineer discretion. |
| **`ABSTAIN`** | **Insufficient Info** | Query is too generic (e.g. *"submersible pump"*) to distinguish between openwell (IS 14220) and borewell (IS 8034). |
| **`OUT_OF_CORPUS`** | **Outside Corpus** | The requested equipment is outside the verified prototype corpus (prevents false matches). |

---

## 5. Current Prototype Knowledge Base

> **Important Corpus Notice:**
> *"Prototype corpus — currently 7 verified standards. This is not the full BIS catalogue."*

The prototype operates on a curated, verified knowledge base focused on the mechanical pump and water handling sector (BIS Technical Committee **MED 20**):

| Entity Type | Exact Count | Description |
| :--- | :---: | :--- |
| **Standards** | **7** | IS 14220, IS 8034, IS 9079, IS 14536, IS 9283, IS 11346, IS 10572 |
| **Evidence Records** | **15** | Grounded excerpts from official BIS documents, scopes, and committee records |
| **Relationships** | **5** | Normative graph links (motors, acceptance tests, codes of practice) |
| **Source Documents** | **5** | Official BIS portal URLs and committee work programmes |
| **Benchmark Cases** | **10** | Internal regression evaluation suite |
| **Certification Records** | **2** | QCO verification notices (marked `not_verified_in_prototype_corpus` where unconfirmed) |

---

## 6. Technology Stack

Only active, verified technologies used in the current deployment are listed:

* **Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS, Lucide Icons
* **Backend:** Python 3.11, FastAPI, Pydantic v2, Uvicorn
* **Database & Cloud Storage:** Google Cloud Firestore (serverless NoSQL database)
* **Document Processing:** PyMuPDF (PDF text layer extraction — image-only PDFs require OCR, not yet implemented)
* **Retrieval (Deployed MVP):** Exact IS-Identifier Matching + BM25 Lexical Retrieval
* **Retrieval (Future / Provisioned):** Dense Neural Embeddings (`ENABLE_DENSE=true`) + Cross-Encoder Reranker (`ENABLE_RERANKER=true`) — disabled in current deployment
* **Hosting & Infrastructure:** Firebase Hosting (Frontend), Render (Backend Web Service)

---

## 7. Prototype Capabilities

The deployed prototype provides the following verified capabilities:

* **Natural Specification Analysis:** Accepts free-form commercial procurement descriptions and technical trade text.
* **Tender PDF Document Upload:** Ingests tender PDFs, extracts text layers via PyMuPDF, and runs requirement isolation. Image-only/scanned PDFs (no text layer) return an explicit OCR-required error — OCR is not yet implemented.
* **Requirement-Level Coverage:** Every extracted requirement is assessed independently. Tender-cited IS numbers absent from the corpus are surfaced as `unverified_reference` gaps, not silently masked.
* **Evidence-Grounded Traceability:** Every recommendation displays the exact BIS clause, scope text, and official source link.
* **Normative Reference Graph:** Automatically discovers companion standards (e.g. electric motors under IS 9283 for submersible pumps).
* **Transparent Regulatory Status:** Displays Quality Control Order (QCO) notices with explicit verification flags. No mandatory/non-mandatory status is inferred without a confirmed gazette source.
* **Audit Report Generator:** Produces auditable HTML reports detailing parameter coverage and gap analysis.
* **Out-of-Corpus Safety Gate:** Accurately rejects out-of-domain queries without emitting false standard recommendations.
* **Corpus Explorer:** Dedicated Resources explorer page allowing full browsing and searching of all 7 standards and 15 evidence records.
* **Procurement API:** REST JSON output (`AnalysisResponse`) is the MVP procurement integration layer. Direct GeM/CPPP portal integration is future work.

---

## 8. Current Limitations

* **Curated Corpus Scope:** The verified corpus currently covers 7 Indian Standards in the pump sector (MED 20).
* **Retrieval MVP:** Active deployment uses Exact IS-ID + BM25 only. Dense neural embeddings and cross-encoder rerankers are provisioned but disabled (`ENABLE_DENSE=false`, `ENABLE_RERANKER=false`).
* **Text-Based PDF Extraction Only:** PyMuPDF extracts text layers. Scanned or image-only PDFs without text layers return an explicit error — OCR integration is a future step.
* **English-Only Input:** Multilingual (Hindi/regional language) tender support is not yet implemented.
* **Procurement Output:** API + HTML report (MVP). Direct GeM/CPPP portal integration is not yet implemented.
* **Render Free-Tier Spin-Down:** Render backend instances may experience a 30–50 second cold-start delay after 15 minutes of inactivity (mitigated by automated client keep-alive pings).

---

## 9. Verification & Testing

The deployed prototype has been verified end-to-end across the full stack:

1. **Automated Test Suite:** Unit and integration tests cover requirement extraction, retrieval, applicability gates, graph traversal, and API routes (`pytest`).
2. **Data Validation:** Automated checks ensure 100% schema compliance for all standards, evidence records, and graph relationships (`validate_data.py`).
3. **End-to-End Evaluation:** Playwright browser tests verify user journeys on the live Firebase frontend against the Render backend.

*(Note: The internal 10-case evaluation benchmark is a regression test suite for prototype verification, not a claim of real-world national accuracy).*

---

## 10. Local Development

### Backend Setup
```bash
# Clone repository
git clone https://github.com/Ashish-Arya1/bis-standards-engine-full.git
cd bis-standards-engine-full

# Virtual environment setup
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# Install dependencies & run backend
pip install -r requirements.txt
uvicorn app.api.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 11. Project Structure

```text
bis-standards-engine-full/
├── app/
│   ├── api/          # FastAPI routes, endpoints & request models
│   ├── extraction/   # Requirement & parameter extraction
│   ├── graph/        # Normative reference graph traversal
│   ├── policy/       # Deterministic applicability & lifecycle gates
│   ├── report/       # Auditable HTML report generation
│   ├── retrieval/    # Exact-ID and BM25 lexical search engine
│   └── storage/      # Firestore client and JSON seed loader
├── data/             # Frozen verified corpus (standards, evidence, sources)
├── evaluation/       # Benchmark regression suite
├── frontend/         # Next.js 14 web application
├── scripts/          # Corpus validation and deployment keep-alive tools
└── tests/            # Pytest test suite & fixtures
```
