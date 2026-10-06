import re

def search(query, standards):
    hits = []
    # Match standard number and optional year/edition token
    for m in re.finditer(r"\bIS\s*[:\-]?\s*(\d{3,6})(?:(?:\s*[:/\-]\s*|\s+)([A-Za-z0-9]{2,6}))?\b", query, re.I):
        std_num = m.group(1)
        suffix = m.group(2)
        # If an explicit suffix is provided but contains non-digit corruption, skip exact match
        if suffix and not suffix.isdigit():
            continue
        target = f"IS {std_num}".upper().replace(" ", "")
        for s in standards:
            if s.standard_id.upper().replace(" ", "").startswith(target) and s.standard_id not in hits:
                hits.append(s.standard_id)
    return hits
