import re
from app.models import Requirement

POWER = re.compile(r"\b(\d+(?:\.\d+)?)\s*(HP|kW)\b", re.I)
POWER_CORRUPTED = re.compile(r"\b([A-Za-z]+|\d+[A-Za-z]+|[A-Za-z]+\d+)\s*(HP|kW)\b", re.I)
IS_REF = re.compile(
    r"\bIS\s*[:\-]?\s*(\d{3,6})(?:(?:\s*[:/\-]\s*)(?:part\s*\d+\s*[:/\-]\s*)?(?!\bIS\b)([A-Za-z0-9]{2,6})|\s+(?:part\s*\d+\s*[:/\-]\s*)?(\d{2,4}|[12][09oOiI][0-9oOiIsSbB]{2,3}))?\b",
    re.I,
)
VOLTAGE = re.compile(r"\b(\d+(?:\.\d+)?)\s*(V|kV|volt)\b", re.I)
FLOW = re.compile(r"\b(\d+(?:\.\d+)?)\s*(LPS|LPM|m3/h|GPM)\b", re.I)


def _page(text: str, index: int):
    matches = list(re.finditer(r"\[PAGE\s+(\d+)\]", text[:index], re.I))
    return int(matches[-1].group(1)) if matches else None


def _sentence_chunks(text: str):
    # Preserve common numbered procurement-item prefixes ("2. 10 kW ...") as
    # one clause instead of splitting off the list number as a sentence.
    text = re.sub(r"(?<![\d.])(\d+)\.\s+(?=[A-Z0-9])", r"\1) ", text)
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+|\n+", text) if x.strip()]


def _normalize_for_extraction(text: str) -> str:
    """Join PDF line wraps while retaining page markers for provenance.

    This normalized copy is only used for requirement extraction; callers keep
    the original input text for display. Page markers remain hard boundaries.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    pages = re.split(r"(\[PAGE\s+\d+\])", text, flags=re.I)
    normalized = []
    for part in pages:
        if re.fullmatch(r"\[PAGE\s+\d+\]", part, flags=re.I):
            normalized.append("\n" + part + "\n")
        else:
            normalized.append(re.sub(r"\s+", " ", part).strip())
    return "".join(normalized)


def extract_requirements(text: str):
    rows = []
    text = _normalize_for_extraction(text)
    chunks = _sentence_chunks(text)

    for i, chunk in enumerate(chunks, 1):
        low = chunk.lower()
        page = _page(text, text.find(chunk))

        # IS reference extraction — always run, domain-agnostic
        is_matches = list(IS_REF.finditer(chunk))
        for j, m in enumerate(is_matches):
            std_num = m.group(1)
            raw_suffix = m.group(2) or m.group(3)
            method = "regex"
            confidence = 0.99

            if raw_suffix:
                if raw_suffix.isdigit():
                    if len(raw_suffix) == 2:
                        y_int = int(raw_suffix)
                        year = f"19{raw_suffix}" if y_int >= 50 else f"20{raw_suffix}"
                    else:
                        year = raw_suffix
                    ref_val = f"IS {std_num}:{year}"
                else:
                    # Malformed/corrupted year suffix (e.g. 201B, 20I8, 2O18)
                    ref_val = f"IS {std_num}:{raw_suffix}"
                    method = "ocr_corrupted_reference"
                    confidence = 0.50
            else:
                ref_val = f"IS {std_num}"

            req_suffix = f"-IS-{j+1}" if len(is_matches) > 1 else "-IS"
            rows.append(Requirement(
                requirement_id=f"REQ-{i:03d}{req_suffix}",
                category="reference",
                attribute="is_number",
                value=ref_val,
                text=chunk,
                source_page=page,
                extraction_method=method,
                extraction_confidence=confidence,
            ))

        # Power values — domain-agnostic
        power_matched = False
        for m in POWER.finditer(chunk):
            power_matched = True
            rows.append(Requirement(
                requirement_id=f"REQ-{i:03d}-POWER",
                category="performance",
                attribute="rated_power",
                value=m.group(1),
                unit=m.group(2).lower(),
                text=chunk,
                source_page=page,
                extraction_confidence=0.93,
            ))

        # Corrupted power values (e.g. 'S HP', 'O kW') when clean power did not match
        if not power_matched:
            for m in POWER_CORRUPTED.finditer(chunk):
                raw_token = m.group(1)
                # Ignore non-corrupted English words like 'high hp' or 'motor hp'
                if len(raw_token) <= 4 or any(c.isdigit() for c in raw_token):
                    rows.append(Requirement(
                        requirement_id=f"REQ-{i:03d}-POWER-UNCERTAIN",
                        category="performance",
                        attribute="rated_power_uncertain",
                        value=raw_token,
                        unit=m.group(2).lower(),
                        text=chunk,
                        source_page=page,
                        extraction_method="ocr_corrupted_numeric",
                        extraction_confidence=0.40,
                    ))

        # Voltage values
        for m in VOLTAGE.finditer(chunk):
            rows.append(Requirement(
                requirement_id=f"REQ-{i:03d}-VOLT",
                category="performance",
                attribute="voltage",
                value=m.group(1),
                unit=m.group(2).lower(),
                text=chunk,
                source_page=page,
                extraction_confidence=0.90,
            ))

        # Flow values
        for m in FLOW.finditer(chunk):
            rows.append(Requirement(
                requirement_id=f"REQ-{i:03d}-FLOW",
                category="performance",
                attribute="flow_rate",
                value=m.group(1),
                unit=m.group(2).lower(),
                text=chunk,
                source_page=page,
                extraction_confidence=0.90,
            ))

        # General product-description row: emit one per sentence that carries
        # any substantive noun content (avoids duplicating pure-numeric sentences)
        alpha_tokens = [w for w in low.split() if w.isalpha() and len(w) > 2]
        if alpha_tokens and not any(r.text == chunk and r.category == "product" for r in rows):
            rows.append(Requirement(
                requirement_id=f"REQ-{i:03d}",
                category="product",
                text=chunk,
                source_page=page,
                extraction_method="general_text",
                extraction_confidence=0.60,
            ))

    # Absolute fallback — entire input as a single general requirement
    if not rows and text.strip():
        rows.append(Requirement(
            requirement_id="REQ-001",
            category="general",
            text=text.strip(),
            extraction_method="fallback",
            extraction_confidence=0.40,
        ))
    return rows
