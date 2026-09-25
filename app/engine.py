import logging
import time
import uuid
from typing import Optional
from app.config import settings

from app.models import AnalysisRequest, AnalysisResponse, RetrievalResult
from app.storage.repository import get_repository, BaseRepository
from app.extraction.document import extract_text_from_file
from app.extraction.requirement_extractor import extract_requirements
from app.extraction.validator import validate_requirements
from app.retrieval.exact_id import search as exact_search
from app.retrieval.bm25 import BM25
from app.retrieval.dense import DenseRetriever
from app.retrieval.fusion import rrf
from app.retrieval.reranker import CrossEncoderReranker
from app.policy.applicability import assess
from app.policy.lifecycle import assess as lifecycle_assess
from app.policy.coverage import build
from app.policy.conflicts import detect
from app.policy.evidence_gate import route
from app.policy.certification import CertificationRepository
from app.graph.relationships import expand
from app.report.builder import build_html

logger = logging.getLogger(__name__)


class RecommendationEngine:
    def __init__(self, repository: Optional[BaseRepository] = None):
        self.repo = repository or get_repository()
        self.standards = self.repo.standards
        self.by_id = {x.standard_id: x for x in self.standards}

        self.bm25 = BM25([
            f"{s.standard_id} {s.title} {s.scope} {' '.join(s.keywords)}"
            for s in self.standards
        ])

        self.dense = DenseRetriever(settings.embedding_model)
        if settings.enable_dense:
            # CON-08: report failure clearly instead of silently degrading
            ok = self.dense.build(self.standards)
            if not ok:
                logger.warning(
                    "ENABLE_DENSE=true but sentence_transformers is not installed "
                    "or failed to load model '%s'. Dense retrieval is DISABLED.",
                    settings.embedding_model,
                )

        self.reranker = CrossEncoderReranker(settings.reranker_model)
        if settings.enable_reranker:
            ok = self.reranker.load()
            if not ok:
                logger.warning(
                    "ENABLE_RERANKER=true but cross-encoder model '%s' failed to load. "
                    "Reranker is DISABLED.",
                    settings.reranker_model,
                )

        self.cert_repo = CertificationRepository(self.repo.certification)

    def _input(self, request):
        if request.text is not None:
            if not request.text.strip():
                raise ValueError("Input text must not be empty or whitespace-only.")
            return request.text, False
        if request.file_path:
            return extract_text_from_file(request.file_path)
        raise ValueError("Provide text or file_path.")

    def analyze(self, request: AnalysisRequest):
        # CON-07: capture true start time for total_ms
        t_start = time.perf_counter()
        timings = {}

        t = time.perf_counter()
        text, ocr_used = self._input(request)
        timings["input_ms"] = (time.perf_counter() - t) * 1000

        t = time.perf_counter()
        requirements = extract_requirements(text)
        validate_requirements(requirements)
        timings["extraction_ms"] = (time.perf_counter() - t) * 1000

        t = time.perf_counter()
        exact_ids = exact_search(text, self.standards)
        bm25_hits = self.bm25.search(text, settings.max_candidates)
        bm25_ids = [self.standards[h.doc_index].standard_id for h in bm25_hits]
        lists = {"exact_id": exact_ids, "bm25": bm25_ids}

        if settings.enable_dense and self.dense.model is not None:
            dense_ids = [
                self.standards[i].standard_id
                for i, _ in self.dense.search(text, settings.max_candidates)
            ]
            lists["dense"] = dense_ids

        fused = rrf(lists)

        # CON-05: filter by relevance floor — if max score is below floor the
        # query is outside the corpus; candidates list stays empty → OUT_OF_CORPUS
        if fused and fused[0][1] >= settings.relevance_floor:
            top_fused = fused[:settings.max_candidates]
        else:
            top_fused = []

        rows = []
        for sid, score, paths in top_fused:
            s = self.by_id[sid]
            rows.append({
                "standard_id": sid,
                "title": s.title,
                "scope": s.scope,
                "retrieval_paths": paths,
                "rrf_score": score,
            })

        if settings.enable_reranker and self.reranker.model is not None and rows:
            rows = self.reranker.rerank(text, rows, settings.max_candidates)

        candidates = [RetrievalResult(
            standard_id=x["standard_id"],
            title=x["title"],
            retrieval_paths=x["retrieval_paths"],
            rrf_score=x["rrf_score"],
            rerank_score=x.get("rerank_score"),
        ) for x in rows]
        timings["retrieval_ms"] = (time.perf_counter() - t) * 1000

        t = time.perf_counter()
        applicability = [assess(self.by_id[c.standard_id], requirements) for c in candidates]
        lifecycle = [lifecycle_assess(self.by_id[c.standard_id], request.tender_date) for c in candidates]
        coverage = build(requirements, applicability)
        gaps = [x for x in coverage if x.state in {"not_covered", "unverified_reference", "edition_mismatch"}]
        related = expand([c.standard_id for c in candidates], self.repo.relationships, settings.max_related_hops)

        product_text = " ".join(r.text for r in requirements)
        certification = {c.standard_id: self.cert_repo.lookup(c.standard_id, product_text) for c in candidates}

        # CON-06: pass by_id so conflicts.detect can look up conflicts_with
        conflicts = detect([c.standard_id for c in candidates], applicability, lifecycle, self.by_id)

        decision, reasons = route(
            [c.standard_id for c in candidates],
            applicability, lifecycle, coverage, conflicts,
            by_id=self.by_id
        )
        timings["policy_ms"] = (time.perf_counter() - t) * 1000

        ids = set()
        for c in candidates:
            ids.update(self.by_id[c.standard_id].evidence_ids)
        for a in applicability:
            ids.update(a.evidence_ids)
        for l in lifecycle:
            ids.update(l.evidence_ids)
        for g in coverage:
            ids.update(g.evidence_ids)
        for r in related:
            ids.update(r.evidence_ids)
        for x in certification.values():
            ids.update(x.evidence_ids)

        evidence = [e for e in self.repo.evidence if e.evidence_id in ids]
        result = AnalysisResponse(
            analysis_id=f"AN-{uuid.uuid4().hex[:12]}",
            input_text=text,
            requirements=requirements,
            candidates=candidates,
            applicability=applicability,
            lifecycle=lifecycle,
            related_standards=related,
            certification=certification,
            coverage=coverage,
            gaps=gaps,
            conflicts=conflicts,
            decision=decision,
            decision_reasons=reasons + ([f"OCR used: {ocr_used}"] if ocr_used else []),
            evidence=evidence,
            timings_ms=timings,
        )
        result.report_html = build_html(result, by_id=self.by_id)
        # CON-07: total_ms uses t_start captured at beginning of analyze()
        result.timings_ms["total_ms"] = (time.perf_counter() - t_start) * 1000
        return result
