import json
import os
import tempfile
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.engine import RecommendationEngine
from app.models import AnalysisRequest, AnalysisResponse

# Runtime availability flag for PDF extraction (PyMuPDF / fitz)
try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except Exception:
    FITZ_AVAILABLE = False

app = FastAPI(
    title="SIH26108 BIS Standards Recommendation Engine",
    version="0.1.0",
    description="Evidence-grounded SIH26108 prototype."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https://.*(web\.app|firebaseapp\.com|onrender\.com)|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = RecommendationEngine()

_MAX_PDF_BYTES = 25 * 1024 * 1024  # 25 MB hard cap

@app.get("/api/v1/health")
def health():
    summary = engine.repo.get_health_summary()
    return {
        "status": "ok",
        "data_source": summary["data_source"],
        "standards_count": summary["standards_count"],
        "evidence_count": summary["evidence_count"],
        "relationships_count": summary["relationships_count"],
        "sources_count": summary["sources_count"],
        "standards_loaded": len(engine.standards),
        "dense_enabled": engine.dense.model is not None,
        "reranker_enabled": engine.reranker.model is not None,
        "pdf_runtime": FITZ_AVAILABLE,
    }

@app.get("/api/v1/resources")
def resources():
    """
    Returns actual corpus metadata, standards, evidence, relationships, sources, and evaluation benchmark cases.
    """
    benchmarks = [b.model_dump() for b in engine.repo.benchmark_cases]
    return {
        "summary": {
            "standards_count": len(engine.repo.standards),
            "evidence_count": len(engine.repo.evidence),
            "relationships_count": len(engine.repo.relationships),
            "benchmark_cases_count": len(benchmarks),
            "sources_count": len(engine.repo.sources),
        },
        "standards": engine.repo.standards,
        "evidence": engine.repo.evidence,
        "relationships": engine.repo.relationships,
        "sources": engine.repo.sources,
        "benchmark_cases": benchmarks,
    }


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest):
    try:
        return engine.analyze(request)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/api/v1/recommend", response_model=AnalysisResponse)
def recommend(request: AnalysisRequest):
    """Alias for /api/v1/analyze."""
    try:
        return engine.analyze(request)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/api/v1/upload-pdf", response_model=AnalysisResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Multipart PDF upload.  Accepts a single .pdf file ≤ 25 MB.
    Saves to a temp file, runs the full extraction + analysis pipeline,
    then cleans up.  Returns the same AnalysisResponse as /api/v1/analyze.
    """
    # Fail fast if PDF runtime dependency is missing
    if not FITZ_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail=("PDF extraction runtime is unavailable on this server. "
                    "Install PyMuPDF (pip install PyMuPDF) to enable PDF uploads.")
        )

    # ── 1. MIME / extension guard ────────────────────────────────────────────
    filename = file.filename or ""
    content_type = file.content_type or ""
    if not filename.lower().endswith(".pdf") and "pdf" not in content_type:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only PDF files (.pdf) are accepted."
        )

    # ── 2. Read + size guard ─────────────────────────────────────────────────
    raw = await file.read()
    if len(raw) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(raw) > _MAX_PDF_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds the 25 MB size limit ({len(raw) // (1024*1024)} MB received)."
        )

    # ── 3. Write to temp file and run pipeline ────────────────────────────────
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(raw)
            tmp_path = tmp.name

        request = AnalysisRequest(file_path=tmp_path)
        return engine.analyze(request)

    except (ValueError, RuntimeError, Exception) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

@app.get("/api/v1/standards/{standard_id}")
def standard(standard_id: str):
    s = engine.repo.get_standard(standard_id)
    if not s:
        raise HTTPException(status_code=404, detail="Standard not found in prototype corpus.")
    evidence = [e for e in engine.repo.evidence if e.evidence_id in s.evidence_ids]
    return {"standard": s, "evidence": evidence}

