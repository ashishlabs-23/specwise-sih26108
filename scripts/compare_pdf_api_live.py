import json
from pathlib import Path
import requests

ROOT = Path("tests/live_pdf_redteam_20260926")
LOCAL = "http://127.0.0.1:8000"
LIVE = "https://specwise-sih26108.onrender.com"

def summarize_response(response):
    record = {"http_status": response.status_code}
    try:
        data = response.json()
    except Exception:
        record["error"] = response.text[:500]
        return record
    if response.ok:
        record.update({
            "decision": data.get("decision"),
            "primary": [a.get("standard_id") for a in data.get("applicability", []) if a.get("result") == "strong"],
            "candidates": [c.get("standard_id") for c in data.get("candidates", [])],
            "applicability": [{"standard_id": a.get("standard_id"), "result": a.get("result")} for a in data.get("applicability", [])],
            "coverage": [{"requirement_id": c.get("requirement_id"), "standard_id": c.get("standard_id"), "state": c.get("state")} for c in data.get("coverage", [])],
            "gaps": [{"requirement_id": c.get("requirement_id"), "standard_id": c.get("standard_id"), "state": c.get("state")} for c in data.get("gaps", [])],
            "unverified_references": [{"requirement_id": c.get("requirement_id"), "state": c.get("state"), "reason": c.get("reason")} for c in data.get("coverage", []) if c.get("state") in ("unverified_reference", "edition_mismatch")],
            "evidence_ids": [e.get("evidence_id") for e in data.get("evidence", [])],
            "certification": {key: value.get("state") for key, value in data.get("certification", {}).items()},
            "input_text": data.get("input_text", "")[:300],
        })
    else:
        record["error"] = data.get("detail", str(data))
    return record

def upload(base, name, payload=None, content_type="application/pdf", filename=None):
    if payload is None:
        payload = (ROOT / name).read_bytes()
    if filename is None:
        filename = name
    return requests.post(base + "/api/v1/upload-pdf", files={"file": (filename, payload, content_type)}, timeout=180)

results = {}
for name in [f"pdf-{i:02d}-" for i in []]:
    pass
files = sorted(p for p in ROOT.glob("pdf-*.pdf"))
for path in files:
    results[path.name] = {}
    for label, base in (("local", LOCAL), ("live", LIVE)):
        try:
            response = upload(base, path.name)
            results[path.name][label] = summarize_response(response)
        except Exception as exc:
            results[path.name][label] = {"error": f"{type(exc).__name__}: {exc}"}

invalids = {
    "empty_pdf": (b"", "empty.pdf", "application/pdf"),
    "renamed_text": (b"not a pdf document", "renamed.pdf", "application/pdf"),
    "corrupt_pdf": ((ROOT / "pdf-07-corrupt.pdf").read_bytes(), "corrupt.pdf", "application/pdf"),
    "oversized_pdf": (b"%PDF-1.4\n" + b"0" * (25 * 1024 * 1024), "oversized.pdf", "application/pdf"),
}
results["invalid_inputs"] = {}
for name, (payload, filename, content_type) in invalids.items():
    results["invalid_inputs"][name] = {}
    for label, base in (("local", LOCAL), ("live", LIVE)):
        try:
            response = upload(base, name, payload, content_type, filename)
            results["invalid_inputs"][name][label] = summarize_response(response)
        except Exception as exc:
            results["invalid_inputs"][name][label] = {"error": f"{type(exc).__name__}: {exc}"}

health = {}
for label, base in (("local", LOCAL), ("live", LIVE)):
    try:
        response = requests.get(base + "/api/v1/health", timeout=180)
        health[label] = {"status": response.status_code, "body": response.json()}
    except Exception as exc:
        health[label] = {"error": f"{type(exc).__name__}: {exc}"}

(ROOT / "api_results.json").write_text(json.dumps({"health": health, "uploads": results}, indent=2), encoding="utf-8")
print(json.dumps({"health": health, "uploads": results}, indent=2))
