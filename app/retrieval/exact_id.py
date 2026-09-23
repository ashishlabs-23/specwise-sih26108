import re

def search(query, standards):
    hits = []
    for m in re.finditer(r"\bIS\s*[:\-]?\s*(\d{3,6})", query, re.I):
        target = f"IS {m.group(1)}".upper().replace(" ", "")
        for s in standards:
            if s.standard_id.upper().replace(" ", "").startswith(target) and s.standard_id not in hits:
                hits.append(s.standard_id)
    return hits
