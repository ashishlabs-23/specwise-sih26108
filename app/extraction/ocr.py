"""
OCR adapter module for scanned procurement PDFs.
Provides a deployment-safe, isolated abstraction for optical character recognition
with confidence scoring, entity validation, and fallback handling.
"""

from dataclasses import dataclass, field
from enum import Enum
import logging
import os
import re
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class OCRStatus(str, Enum):
    OCR_SUCCESS = "OCR_SUCCESS"
    OCR_LOW_CONFIDENCE = "OCR_LOW_CONFIDENCE"
    OCR_FAILED = "OCR_FAILED"
    OCR_UNSUPPORTED = "OCR_UNSUPPORTED"


@dataclass
class PageOCRResult:
    page_number: int
    text: str
    confidence: float
    status: OCRStatus
    warnings: List[str] = field(default_factory=list)
    has_tables: bool = False
    detected_entities: List[str] = field(default_factory=list)


@dataclass
class OCRResult:
    text: str
    pages: List[PageOCRResult]
    method: str
    status: OCRStatus
    avg_confidence: float
    warnings: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0


# Regexes for entity detection and OCR corruption auditing
RE_IS_STANDARD = re.compile(r"\bIS\s*(\d{3,6})(?::(\d{4}))?\b", re.IGNORECASE)
RE_CORRUPTED_IS = re.compile(r"\bIS\s*(\d{3,6})[:/]([A-Za-z0-9+*]{1,5})\b")
RE_POWER = re.compile(r"\b(\d+(?:\.\d+)?)\s*(?:HP|kW|kV|MW)\b", re.IGNORECASE)
RE_DIMENSION = re.compile(r"\b(\d+(?:\.\d+)?)\s*(?:mm|cm|m|inch|inches)\b", re.IGNORECASE)
RE_TABLE_ROW = re.compile(r"^[|\t+].*[|\t+]$|^\s*\d+[\s\t]+[A-Za-z].*[\s\t]+\d+", re.MULTILINE)


def get_tessdata_path() -> Optional[str]:
    """Find local or system tessdata directory."""
    app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidates = [
        os.path.join(app_root, "data", "tessdata"),
        os.path.join(os.getcwd(), "data", "tessdata"),
        os.path.join(app_root, "scratch", "tessdata"),
        os.path.join(os.getcwd(), "scratch", "tessdata"),
        "/app/data/tessdata",
        "/usr/share/tesseract-ocr/5/tessdata",
        "/usr/share/tesseract-ocr/4.00/tessdata",
        "/usr/share/tessdata",
        os.environ.get("TESSDATA_PREFIX", ""),
    ]
    for c in candidates:
        if c and os.path.isdir(c) and os.path.exists(os.path.join(c, "eng.traineddata")):
            return c
    return None


def audit_ocr_text_safety(text: str) -> Tuple[OCRStatus, float, List[str]]:
    """
    Evaluates OCR quality, detects corruption patterns, and assigns confidence.
    """
    warnings = []
    if not text or len(text.strip()) < 10:
        return OCRStatus.OCR_FAILED, 0.0, ["Empty or unreadable OCR output"]

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    total_chars = len(text)
    if total_chars == 0:
        return OCRStatus.OCR_FAILED, 0.0, ["Zero characters in OCR text"]

    # Calculate printable ASCII / unicode ratio
    printable_chars = sum(1 for c in text if c.isprintable() and not c.isspace())
    alpha_num_chars = sum(1 for c in text if c.isalnum())
    
    if alpha_num_chars / max(1, total_chars) < 0.35:
        warnings.append("High ratio of non-alphanumeric noise characters detected.")

    # Check for corrupted IS identifiers (e.g. IS 14220:201B instead of IS 14220:2018)
    for match in RE_CORRUPTED_IS.finditer(text):
        suffix = match.group(2)
        if not suffix.isdigit() or len(suffix) != 4:
            warnings.append(
                f"Suspicious corrupted BIS standard reference detected: '{match.group(0)}'. "
                "OCR noise may have altered numeric standard year."
            )

    # Check for character substitution indicators (e.g. S HP vs 5 HP)
    if re.search(r"\b[S|s]\s*HP\b", text):
        warnings.append("Possible OCR character substitution ('S HP' instead of '5 HP') detected.")

    # Heuristic confidence calculation
    confidence = 0.90
    if len(warnings) > 0:
        confidence -= 0.15 * len(warnings)
    if len(lines) < 2 and total_chars < 50:
        confidence -= 0.20
        warnings.append("Low text density page.")

    confidence = max(0.0, min(1.0, confidence))

    if confidence < 0.60:
        status = OCRStatus.OCR_LOW_CONFIDENCE
    else:
        status = OCRStatus.OCR_SUCCESS

    return status, confidence, warnings


def ocr_page_with_pymupdf(page, page_num: int, tessdata: Optional[str] = None, dpi: int = 150) -> PageOCRResult:
    """Runs OCR on an individual fitz Page object."""
    try:
        tess_dir = tessdata or get_tessdata_path()
        if not tess_dir:
            return PageOCRResult(
                page_number=page_num,
                text="",
                confidence=0.0,
                status=OCRStatus.OCR_UNSUPPORTED,
                warnings=["Tessdata not found. OCR cannot proceed."],
            )

        tp = page.get_textpage_ocr(language="eng", dpi=dpi, tessdata=tess_dir, full=True)
        raw_text = tp.extractText()

        status, confidence, warnings = audit_ocr_text_safety(raw_text)

        # Detect entities
        entities = []
        for m in RE_IS_STANDARD.finditer(raw_text):
            entities.append(m.group(0))
        for m in RE_POWER.finditer(raw_text):
            entities.append(m.group(0))
        for m in RE_DIMENSION.finditer(raw_text):
            entities.append(m.group(0))

        has_tables = bool(RE_TABLE_ROW.search(raw_text))
        if has_tables:
            warnings.append("Tabular layout detected; verify column alignments.")

        return PageOCRResult(
            page_number=page_num,
            text=raw_text,
            confidence=confidence,
            status=status,
            warnings=warnings,
            has_tables=has_tables,
            detected_entities=entities,
        )
    except Exception as exc:
        logger.exception("OCR page execution failed on page %d", page_num)
        return PageOCRResult(
            page_number=page_num,
            text="",
            confidence=0.0,
            status=OCRStatus.OCR_FAILED,
            warnings=[f"OCR page failure: {str(exc)}"],
        )


def ocr_document(doc, tessdata: Optional[str] = None, dpi: int = 150) -> OCRResult:
    """Processes all pages of a fitz Document through safe OCR."""
    import time
    t0 = time.perf_counter()
    page_results: List[PageOCRResult] = []
    combined_pages: List[str] = []
    all_warnings: List[str] = []

    for idx, page in enumerate(doc):
        p_num = idx + 1
        res = ocr_page_with_pymupdf(page, p_num, tessdata=tessdata, dpi=dpi)
        page_results.append(res)
        all_warnings.extend(res.warnings)
        if res.text.strip():
            combined_pages.append(f"[PAGE {p_num}]\n{res.text.strip()}")

    t_elapsed = (time.perf_counter() - t0) * 1000

    if not page_results:
        return OCRResult(
            text="",
            pages=[],
            method="PyMuPDF-Tesseract",
            status=OCRStatus.OCR_FAILED,
            avg_confidence=0.0,
            warnings=["Document contains 0 pages."],
            execution_time_ms=t_elapsed,
        )

    avg_conf = sum(p.confidence for p in page_results) / len(page_results)
    
    # Overall status
    if any(p.status == OCRStatus.OCR_UNSUPPORTED for p in page_results):
        overall_status = OCRStatus.OCR_UNSUPPORTED
    elif any(p.status == OCRStatus.OCR_FAILED for p in page_results) and not combined_pages:
        overall_status = OCRStatus.OCR_FAILED
    elif avg_conf < 0.60 or any(p.status == OCRStatus.OCR_LOW_CONFIDENCE for p in page_results):
        overall_status = OCRStatus.OCR_LOW_CONFIDENCE
    else:
        overall_status = OCRStatus.OCR_SUCCESS

    return OCRResult(
        text="\n\n".join(combined_pages),
        pages=page_results,
        method="PyMuPDF-Tesseract",
        status=overall_status,
        avg_confidence=avg_conf,
        warnings=list(dict.fromkeys(all_warnings)),  # deduplicate
        execution_time_ms=t_elapsed,
    )
