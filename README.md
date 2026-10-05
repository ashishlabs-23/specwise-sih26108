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
> *"Prototype corpus — currently 27 verified standards. This is not the full national BIS catalogue."*

The prototype operates on a curated, verified knowledge base focused on the mechanical pump and water handling sector (BIS Technical Committee **MED 20**), electrical machinery (**ETD 15**), switchgear (**ETD 07**), plastic piping (**CED 53 / CED 50**), and waterworks infrastructure (**CED 22**):

| Entity Type | Exact Count | Description |
| :--- | :---: | :--- |
| **Standards** | **27** | Verified standards covering pumps (IS 14220, IS 8034, IS 9079, IS 8472, IS 12225, IS 1520, IS 1710, IS 5120), testing codes (IS 11346, IS 10572), motors & switchgear (IS 9283, IS 12615, IS 996, IS/IEC 60947-4-1), piping & casing (IS 1239, IS 4984, IS 4985, IS 12818, IS 8329), cables (IS 694, IS 1554), valves (IS 778, IS 5312-1, IS 14846), water meters (IS 779), and safety codes (IS 14536, IS 3043) |
| **Evidence Records** | **35** | Grounded excerpts from official BIS publications, scopes, and committee records |
| **Relationships** | **17** | Normative graph links (submersible motors, testing codes, companion piping, valves, starters, earthing safety) |
| **Source Documents** | **14** | Official BIS portal URLs and committee work programmes |
| **Benchmark Cases** | **15** | Internal regression evaluation suite |
| **Certification Records** | **2** | QCO verification notices (marked `not_verified_in_prototype_corpus` where unconfirmed) |

---

## 6. Technology Stack

Only active, verified technologies used in the current deployment are listed:

* **Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS, Lucide Icons
* **Backend:** Python 3.11, FastAPI, Pydantic v2, Uvicorn
* **Database & Cloud Storage:** Google Cloud Firestore (serverless NoSQL database)
* **Document Processing:** PyMuPDF (PDF text layer extraction — scanned/image-only PDFs are detected and safely flagged for OCR)
* **Retrieval (Deployed MVP):** Exact IS-Identifier Matching + BM25 Lexical Retrieval (`ENABLE_DENSE=false`, `ENABLE_RERANKER=false`)
* **Retrieval (Provisioned / Architectural):** Dense Neural Embeddings (Sentence-Transformers) + Cross-Encoder Reranker
* **Hosting & Infrastructure:** Firebase Hosting (Frontend), Render (Backend Web Service)

---

## 7. Prototype Capabilities

The deployed prototype provides the following verified capabilities:

* **Natural Specification Analysis:** Accepts free-form commercial procurement descriptions and technical trade text.
* **Tender PDF Document Ingestion:** Ingests digital tender PDFs, extracts selectable text layers via PyMuPDF, and isolates requirements. Scanned/image-only PDFs (no text layer) are safely flagged for OCR.
* **5-Language UI Localization:** Full interface translation across English, Hindi, Kannada, Tamil, and Telugu with persistent preference and automatic fallback.
* **Requirement-Level Coverage:** Every extracted requirement is assessed independently. Tender-cited IS numbers absent from the corpus are surfaced as `unverified_reference` gaps, not silently masked.
* **Evidence-Grounded Traceability:** Every recommendation displays the exact BIS clause, scope text, and official source link.
* **Normative Reference Graph:** Automatically discovers companion standards (e.g. electric motors under IS 9283 for submersible pumps).
* **Transparent Regulatory Status:** Displays Quality Control Order (QCO) notices with explicit verification flags. No mandatory/non-mandatory status is inferred without a confirmed gazette source.
* **Audit Report Generator:** Produces auditable HTML reports detailing parameter coverage and gap analysis.
* **Out-of-Corpus Safety Gate:** Accurately rejects out-of-domain queries without emitting false standard recommendations.
* **Corpus Explorer:** Dedicated Resources explorer page allowing full browsing and searching of all verified standards and evidence records.
* **Procurement API:** REST JSON output (`AnalysisResponse`) is the MVP procurement integration layer. Direct GeM/CPPP portal integration is future work.

---

## 8. SIH26108 Portal Requirements vs. Prototype Status

> **Prototype Disclosure:** SpecWise is an end-to-end working prototype (Proof-of-Concept) created for SIH26108. The current deployment demonstrates the dual-layer architecture, deterministic verification gates, normative graph traversal, and zero-hallucination recommendation pipeline. The remaining enterprise-scale features from the official SIH portal are planned for the upcoming production phase.

### Comprehensive SIH Requirement Compliance Matrix

| # | SIH Portal Requirement | Current Prototype Status | Status | What We Are Building Next (Production Roadmap) |
|---|---|---|:---:|---|
| **1** | **National BIS Standards Scale** (20,000+ standards across 15 Division Councils) | Curated & frozen verified knowledge base of **7 standards** in MED 20 (Pumps & Water Handling). | 🟡 **Prototype** | Automated multi-division BIS ingestion pipeline, structured clause parser, and full national standards repository covering CED, ETD, TXD, FAD, etc. |
| **2** | **OCR for Scanned Tenders & Image PDFs** | Text-layer extraction via PyMuPDF. Scanned PDFs without text layers are detected and flagged. | 🟡 **Next Phase** | Multi-engine OCR integration (Tesseract / Surya OCR / PaddleOCR) with table structure extraction and multi-column document layout analysis. |
| **3** | **Multilingual Support (Indic / Regional Languages)** | English-only processing in live deployment. (IndicTrans2 200M model validated in research notebook). | 🟡 **Next Phase** | Direct integration of AI4Bharat IndicTrans2 / Bhashini API for end-to-end tender parsing and bilingual recommendations in Hindi, Tamil, Telugu, Marathi, Bengali, etc. |
| **4** | **GFR 144(i) & Anti-Bias Procurement Auditing** | Parameter coverage & missing IS specification gap detection. | 🟡 **Next Phase** | Automated scanning for proprietary brand bias, restrictive non-standard clauses, discriminatory turnover thresholds, and GFR 144(i) anti-competitive flags. |
| **5** | **Real-Time QCO & e-Gazette Synchronization** | Quality Control Order records tagged with manual verification status. | 🟡 **Next Phase** | Live automated crawler and synchronizer with e-BIS portal, Ministry gazette notifications, and mandatory certification schedules. |
| **6** | **Direct GeM & CPPP Portal Workflow Integration** | Standalone Next.js Web UI, REST API (`/api/v1/analyze`), and downloadable HTML audit reports. | 🟡 **Next Phase** | Browser Extension for GeM/CPPP tender creation pages, webhook connectors for e-Procurement platforms, and 1-click BoQ standard export. |
| **7** | **Enterprise Knowledge Graph (Neo4j)** | In-memory graph traversal (max 2 hops, 5 companion links). | 🟡 **Next Phase** | Neo4j enterprise graph database mapping multi-hop cross-sector relationships (raw materials, safety codes, environmental & testing standards). |
| **8** | **Hybrid Dense + Lexical Retrieval at Scale** | BM25 Lexical + Exact IS-ID matching active (Dense embeddings provisioned but toggled off for lightweight hosting). | 🟢 **Provisioned** | Scaled Vector Database (Qdrant / pgvector) with fine-tuned domain bi-encoders and cross-encoder rerankers enabled. |
| **9** | **Human-in-the-Loop Officer Approval Workflow** | Four-state deterministic routing (`RECOMMEND`, `REVIEW`, `ABSTAIN`, `OUT_OF_CORPUS`). | 🟢 **Fulfilled** | Multi-role RBAC (Tender Creator, Technical Evaluator, Approving Officer) with digitally signed audit certificates. |

---

## 9. Current Limitations (Prototype Scope)

* **Curated Corpus Scope:** The verified corpus currently covers 7 Indian Standards in the pump sector (MED 20).
* **Retrieval MVP:** Active deployment uses Exact IS-ID + BM25 only. Dense neural embeddings and cross-encoder rerankers are provisioned but disabled (`ENABLE_DENSE=false`, `ENABLE_RERANKER=false`).
* **Text-Based PDF Extraction Only:** PyMuPDF extracts text layers. Scanned or image-only PDFs without text layers return an explicit error — OCR integration is part of the next phase.
* **English-Only Input:** Multilingual (Hindi/regional language) tender support is validated in research and queued for next build.
* **Procurement Output:** API + HTML report (MVP). Direct GeM/CPPP portal integration is planned for the next release.
* **Render Free-Tier Spin-Down:** Render backend instances may experience a 30–50 second cold-start delay after 15 minutes of inactivity (mitigated by automated client keep-alive pings).

---

## 10. Verification & Testing

The deployed prototype has been verified end-to-end across the full stack:

1. **Automated Test Suite:** Unit and integration tests cover requirement extraction, retrieval, applicability gates, graph traversal, and API routes (`pytest`).
2. **Data Validation:** Automated checks ensure 100% schema compliance for all standards, evidence records, and graph relationships (`validate_data.py`).
3. **End-to-End Evaluation:** Playwright browser tests verify user journeys on the live Firebase frontend against the Render backend.

*(Note: The internal 10-case evaluation benchmark is a regression test suite for prototype verification, not a claim of real-world national accuracy).*

---

## 11. Local Development

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
