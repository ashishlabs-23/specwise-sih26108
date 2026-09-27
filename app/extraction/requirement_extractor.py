import re
from app.models import Requirement

# Regex patterns — domain-agnostic
POWER = re.compile(r"\b(\d+(?:\.\d+)?)\s*(HP|kW)\b", re.I)
IS_REF = re.compile(
    r"\bIS\s*[:\-]?\s*(\d{3,6})"
    r"(?:\s*\(\s*part\s*[- ]?\s*(\d+)\s*\)|\s+part\s*[- ]?\s*(\d+))?"
    r"(?:\s*[:/\-]\s*|\s+)?(\d{2,4})?\b",
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
            # Preserve only explicit list starts. Other PDF line breaks are
            # wrapping noise and must remain joinable for references/clauses.
            protected = re.sub(
                r"\n\s*(?=(?:item\s+\d+\s*[:.)-]?|\(?[a-z]\)|\d{1,3}[.)]|[-*•])\s*)",
                "\uE000",
                part,
                flags=re.I,
            )
            normalized.append(re.sub(r"\s+", " ", protected).replace("\uE000", "\n").strip())
    return "".join(normalized)


_ITEM_MARKER = re.compile(
    r"^\s*(?:item\s+\d+\s*[:.)-]?|\(?[a-z]\)|\d+[.)]|[-*•])\s*",
    re.I,
)
_INLINE_ITEM_MARKER = re.compile(r"(?:\([a-z]\)|\bitem\s+\d+\s*[:.)-]?)", re.I)
_ADMINISTRATIVE = re.compile(
    r"^\s*(?:title|eligibility|bid(?:ding)?\s+terms|delivery\s+terms|"
    r"warranty|inspection|payment|instructions|general\s+conditions)\b",
    re.I,
)


def _procurement_chunks(text: str):
    """Split explicit procurement items before ordinary sentence extraction.

    Item markers and semicolons carry procurement structure across arbitrary
    domains.  Commas deliberately remain inside an item so attributes such as
    power, voltage, head, and material stay with their equipment.
    """
    pieces = re.split(r";|\n+", text)
    out = []
    item_number = 0
    for piece in pieces:
        markers = list(_INLINE_ITEM_MARKER.finditer(piece))
        segments = []
        if markers:
            if piece[:markers[0].start()].strip():
                segments.append((None, piece[:markers[0].start()]))
            for index, marker in enumerate(markers):
                end = markers[index + 1].start() if index + 1 < len(markers) else len(piece)
                segments.append((marker.group(0), piece[marker.end():end]))
        else:
            marker = _ITEM_MARKER.match(piece)
            segments.append((marker.group(0) if marker else None, piece[marker.end():] if marker else piece))

        for marker_text, part in segments:
            part = part.strip()
            if not part:
                continue
            item_id = None
            if marker_text:
                item_number += 1
                item_id = f"ITEM-{item_number:03d}"
            for sentence in _sentence_chunks(part):
                if _ADMINISTRATIVE.match(sentence):
                    continue
                out.append((item_id, sentence))
    return out


def extract_requirements(text: str):
    rows = []
    source_references = list(IS_REF.finditer(text))
    source_reference_index = 0
    text = _normalize_for_extraction(text)
    chunks = _procurement_chunks(text)

    for i, (item_id, chunk) in enumerate(chunks, 1):
        low = chunk.lower()
        page = _page(text, text.find(chunk))

        # IS reference extraction — always run, domain-agnostic
        is_matches = list(IS_REF.finditer(chunk))
        for j, m in enumerate(is_matches):
            std_num = m.group(1)
            part_number = m.group(2) or m.group(3)
            raw_year = m.group(4)
            part = f"Part {part_number}" if part_number else None
            if raw_year:
                if len(raw_year) == 2:
                    y_int = int(raw_year)
                    year = f"19{raw_year}" if y_int >= 50 else f"20{raw_year}"
                else:
                    year = raw_year
                ref_val = f"IS {std_num}{' ' + part if part else ''}:{year}"
            else:
                ref_val = f"IS {std_num}{' ' + part if part else ''}"

            source_citation = m.group(0)
            if source_reference_index < len(source_references):
                source_match = source_references[source_reference_index]
                source_citation = source_match.group(0)
                source_reference_index += 1

            req_suffix = f"-IS-{j+1}" if len(is_matches) > 1 else "-IS"
            rows.append(Requirement(
                requirement_id=f"REQ-{i:03d}{req_suffix}",
                item_id=item_id,
                category="reference",
                attribute="is_number",
                value=ref_val,
                standard_number=f"IS {std_num}",
                part=part,
                year=year if raw_year else None,
                source_citation=source_citation,
                text=chunk,
                source_page=page,
                extraction_method="regex",
                extraction_confidence=0.99,
            ))

        # Power values — domain-agnostic
        for m in POWER.finditer(chunk):
            rows.append(Requirement(
                requirement_id=f"REQ-{i:03d}-POWER",
                item_id=item_id,
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
                item_id=item_id,
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
                item_id=item_id,
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
        alpha_tokens = re.findall(r"[a-z]{3,}", low)
        if alpha_tokens and not any(r.text == chunk and r.category == "product" for r in rows):
            rows.append(Requirement(
                requirement_id=f"REQ-{i:03d}",
                item_id=item_id,
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
