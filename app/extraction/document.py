from pathlib import Path
import logging
from app.extraction.ocr import ocr_document, OCRStatus

logger = logging.getLogger(__name__)


def extract_text_from_file(path: str):
    """
    Extracts text from uploaded .txt or .pdf files.
    Maintains fast-path PyMuPDF text layer extraction for digital PDFs,
    and falls back to isolated safe OCR for scanned/image-only PDFs.
    """
    p = Path(path)
    if p.suffix.lower() == ".txt":
        return p.read_text(encoding="utf-8"), False

    if p.suffix.lower() == ".pdf":
        import fitz
        try:
            doc = fitz.open(path)
        except Exception:
            logger.exception("Unable to open uploaded PDF")
            raise ValueError("Could not read this PDF. Please upload a valid, unprotected PDF.") from None

        pages = []
        has_image_only_pages = False
        try:
            # ── 1. Fast Path: Digital PDF text layer ─────────────────────────
            for page in doc:
                text = page.get_text("text")
                if text.strip():
                    pages.append(f"[PAGE {page.number + 1}]\n{text}")
                else:
                    has_image_only_pages = True

            # If all pages have selectable text
            if pages and not has_image_only_pages:
                return "\n".join(pages), False

            # ── 2. Fallback Path: Scanned PDF OCR ────────────────────────────
            if not pages or has_image_only_pages:
                logger.info("Scanned/hybrid PDF detected. Running safe OCR fallback on %s", path)
                ocr_res = ocr_document(doc)

                if ocr_res.status == OCRStatus.OCR_UNSUPPORTED:
                    raise ValueError("No extractable PDF text. OCR integration is required for this document.")

                if ocr_res.status == OCRStatus.OCR_FAILED or not ocr_res.text.strip():
                    raise ValueError("No extractable PDF text. Scanned document contains no readable text or is blank.")

                if ocr_res.status == OCRStatus.OCR_LOW_CONFIDENCE:
                    logger.warning("Low confidence OCR extraction: %s", ocr_res.warnings)
                    raise ValueError(
                        f"No extractable PDF text with sufficient quality for reliable standard extraction. "
                        f"Confidence: {ocr_res.avg_confidence:.2f}. Warnings: {'; '.join(ocr_res.warnings)}"
                    )

                return ocr_res.text, True

        except ValueError:
            raise
        except Exception:
            logger.exception("Unable to extract text from uploaded PDF")
            raise ValueError("Could not read this PDF. Please upload a valid, unprotected PDF.") from None
        finally:
            doc.close()

    raise ValueError(f"Unsupported file type: {p.suffix}")
