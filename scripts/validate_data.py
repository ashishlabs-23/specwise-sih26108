import json
from pathlib import Path

data = json.loads(Path("data/standards_seed.json").read_text(encoding="utf-8"))
evidence_ids = {e["evidence_id"] for e in data["evidence"]}
standard_ids = {s["standard_id"] for s in data["standards"]}

errors = []

# Validate standard evidence_ids
for standard in data["standards"]:
    if not standard.get("evidence_ids"):
        errors.append(f"{standard['standard_id']}: no evidence_ids")
    for eid in standard.get("evidence_ids", []):
        if eid not in evidence_ids:
            errors.append(f"{standard['standard_id']}: missing evidence {eid}")

# Validate relationship evidence_ids and standard references
for rel in data.get("relationships", []):
    frm = rel.get("from_standard", "?")
    to = rel.get("to_standard", "?")
    for eid in rel.get("evidence_ids", []):
        if eid not in evidence_ids:
            errors.append(f"Relationship {frm}->{to}: missing evidence {eid}")
    if frm not in standard_ids:
        errors.append(f"Relationship: from_standard '{frm}' not in standards")
    if to not in standard_ids:
        errors.append(f"Relationship: to_standard '{to}' not in standards")

if errors:
    raise SystemExit("\n".join(errors))

n_std = len(data["standards"])
n_ev = len(data["evidence"])
n_rel = len(data.get("relationships", []))
print(f"Validated {n_std} standards, {n_ev} evidence records, {n_rel} relationships.")
