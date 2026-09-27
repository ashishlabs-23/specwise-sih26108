import logging
import time
import uuid
from typing import Optional
from app.config import settings

from app.models import AnalysisRequest, AnalysisResponse, Evidence, LanguageInfo, RetrievalResult
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
from app.policy.domain_relevance import has_corpus_product_signal
from app.policy.certification import CertificationRepository
from app.graph.relationships import expand
from app.report.builder import build_html
from app.multilingual import Translator, prepare_input

logger = logging.getLogger(__name__)


class RecommendationEngine:
    def __init__(self, repository: Optional[BaseRepository] = None, translator: Optional[Translator] = None):
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
        self.translator = translator

    def _input(self, request):
        if request.text is not None:
            if not request.text.strip():
                raise ValueError("Input text must not be empty or whitespace-only.")
            return request.text, False
        if request.file_path:
            return extract_text_from_file(request.file_path)
        raise ValueError("Provide text or file_path.")

    def _evidence_with_provenance(self, coverage, applicability, certification):
        """Return requirement-linked support and separately labeled context.

        Corpus evidence records are immutable.  This method copies only the
        records needed for the analysis response and adds analysis-time
        provenance, so a retrieved candidate cannot make all of its source
        material look applicable to the procurement.
        """
        by_evidence_id = {item.evidence_id: item for item in self.repo.evidence}
        supporting: dict[tuple[str, str], Evidence] = {}
        support_requirements: dict[str, set[str]] = {}
        strong_standard_ids = {
            assessment.standard_id
            for assessment in applicability
            if assessment.result == "strong"
        }

        for entry in coverage:
            if (
                entry.standard_id
                and entry.state in {"covered", "partial", "edition_mismatch"}
                and entry.standard_id in strong_standard_ids
            ):
                support_requirements.setdefault(entry.standard_id, set()).add(entry.requirement_id)
                for evidence_id in entry.evidence_ids:
                    source = by_evidence_id.get(evidence_id)
                    if source:
                        key = (evidence_id, entry.standard_id)
                        prior = supporting.get(key)
                        requirement_ids = set(prior.requirement_ids) if prior else set()
                        requirement_ids.add(entry.requirement_id)
                        supporting[key] = source.model_copy(update={
                            "requirement_ids": sorted(requirement_ids),
                            "candidate_standard_id": entry.standard_id,
                            "evidence_scope": "supporting",
                            "inclusion_reason": (
                                "Supports the requirement-to-standard coverage relationship."
                            ),
                        })

        # Certification claims only support a decision when the same standard
        # supports at least one concrete procurement requirement.
        for standard_id, cert in certification.items():
            requirement_ids = support_requirements.get(standard_id)
            if not requirement_ids:
                continue
            for evidence_id in cert.evidence_ids:
                source = by_evidence_id.get(evidence_id)
                if source:
                    supporting[(evidence_id, standard_id)] = source.model_copy(update={
                        "requirement_ids": sorted(requirement_ids),
                        "candidate_standard_id": standard_id,
                        "evidence_scope": "supporting",
                        "inclusion_reason": (
                            "Certification/QCO status for a standard that supports the listed requirement(s)."
                        ),
                    })

        context: dict[tuple[str, str], Evidence] = {}
        for assessment in applicability:
            # Supporting records above already carry a requirement relationship.
            if assessment.standard_id in support_requirements:
                continue
            for evidence_id in assessment.evidence_ids:
                source = by_evidence_id.get(evidence_id)
                if source:
                    context[(evidence_id, assessment.standard_id)] = source.model_copy(update={
                        "requirement_ids": [],
                        "candidate_standard_id": assessment.standard_id,
                        "evidence_scope": "context_only",
                        "inclusion_reason": (
                            "Retrieved candidate context only; no covered procurement requirement is linked to this evidence."
                        ),
                    })

        return list(supporting.values()), list(context.values())

    def _safe_multilingual_result(self, original_text, prepared, request, timings):
        """Return a non-recommending result without running English retrieval.

        This deliberately retains only source-derived requirements (such as an
        explicit IS citation) so unavailable or failed normalization cannot
        create an English lexical match or fabricated product recommendation.
        """
        requirements = extract_requirements(original_text)
        validate_requirements(requirements)
        coverage = build(requirements, [], known_standard_ids=self.by_id)
        gaps = [entry for entry in coverage if entry.state in {
            "not_covered", "unverified_reference", "edition_mismatch"
        }]
        decision, reasons = route([], [], [], coverage, [], by_id=self.by_id)
        reason = prepared.failure_reason or "Multilingual normalization could not be verified."
        result = AnalysisResponse(
            analysis_id=f"AN-{uuid.uuid4().hex[:12]}",
            input_text=original_text,
            language=LanguageInfo(**prepared.metadata.__dict__),
            requirements=requirements,
            candidates=[], applicability=[], lifecycle=[], related_standards=[],
            certification={}, coverage=coverage, gaps=gaps, conflicts=[],
            decision=decision,
            decision_reasons=[reason, *reasons],
            evidence=[], context_evidence=[],
            tender_cited_standards=[
                requirement for requirement in requirements
                if requirement.category == "reference" and requirement.attribute == "is_number"
            ],
            timings_ms=timings,
        )
        result.report_html = build_html(result, by_id=self.by_id)
        return result

    def analyze(self, request: AnalysisRequest):
        # CON-07: capture true start time for total_ms
        t_start = time.perf_counter()
        timings = {}

        t = time.perf_counter()
        original_text, ocr_used = self._input(request)
        timings["input_ms"] = (time.perf_counter() - t) * 1000

        t = time.perf_counter()
        prepared = prepare_input(original_text, self.translator)
        timings["language_processing_ms"] = (time.perf_counter() - t) * 1000
        if prepared.normalized_english_text is None:
            result = self._safe_multilingual_result(original_text, prepared, request, timings)
            result.timings_ms["total_ms"] = (time.perf_counter() - t_start) * 1000
            return result
        # Downstream remains the existing English-only stack. input_text below
        # always remains the original submitted wording for audit/reporting.
        text = prepared.normalized_english_text

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

        # A product/requirement signal keeps weak lexical matches available to
        # applicability routing, which can ABSTAIN when intent is underspecified.
        # The document-intent gate already removes incidental accessory mentions.
        if fused and has_corpus_product_signal(text, self.standards):
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
        coverage = build(requirements, applicability, known_standard_ids=self.by_id)
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

        evidence, context_evidence = self._evidence_with_provenance(
            coverage, applicability, certification
        )
        tender_cited_standards = [
            requirement for requirement in requirements
            if requirement.category == "reference" and requirement.attribute == "is_number"
        ]
        result = AnalysisResponse(
            analysis_id=f"AN-{uuid.uuid4().hex[:12]}",
            input_text=original_text,
            language=LanguageInfo(**prepared.metadata.__dict__),
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
            context_evidence=context_evidence,
            tender_cited_standards=tender_cited_standards,
            timings_ms=timings,
        )
        result.report_html = build_html(result, by_id=self.by_id)
        # CON-07: total_ms uses t_start captured at beginning of analyze()
        result.timings_ms["total_ms"] = (time.perf_counter() - t_start) * 1000
        return result
