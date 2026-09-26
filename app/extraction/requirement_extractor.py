import re
from app.models import Requirement

# Regex patterns — domain-agnostic
POWER = re.compile(r"\b(\d+(?:\.\d+)?)\s*(HP|kW)\b", re.I)
IS_REF = re.compile(
    r"\bIS\s*[:\-]?\s*(\d{3,6})(?:(?:\s*[:/\-]\s*|\s+)(?:part\s*\d+\s*[:/\-]\s*)?(\d{2,4}))?\b",
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


def extract_requirements(text: str):
    rows = []
    chunks = _sentence_chunks(text)

    for i, chunk in enumerate(chunks, 1):
        low = chunk.lower()
        page = _page(text, text.find(chunk))

        # IS reference extraction — always run, domain-agnostic
        is_matches = list(IS_REF.finditer(chunk))
        for j, m in enumerate(is_matches):
            std_num = m.group(1)
            raw_year = m.group(2)
            if raw_year:
                if len(raw_year) == 2:
                    y_int = int(raw_year)
                    year = f"19{raw_year}" if y_int >= 50 else f"20{raw_year}"
                else:
                    year = raw_year
                ref_val = f"IS {std_num}:{year}"
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
                extraction_method="regex",
                extraction_confidence=0.99,
            ))

        # Power values — domain-agnostic
        for m in POWER.finditer(chunk):
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
