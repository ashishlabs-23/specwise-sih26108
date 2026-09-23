from pathlib import Path

def extract_text_from_file(path: str):
    p = Path(path)
    if p.suffix.lower() == ".txt":
        return p.read_text(encoding="utf-8"), False
    if p.suffix.lower() == ".pdf":
        import fitz
        doc = fitz.open(path)
        pages = []
        ocr_used = False
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                pages.append(f"[PAGE {page.number + 1}]\n{text}")
            else:
                ocr_used = True
        doc.close()
        if not pages:
            raise ValueError("No extractable PDF text. OCR integration is required for this document.")
        return "\n".join(pages), ocr_used
    raise ValueError(f"Unsupported file type: {p.suffix}")
