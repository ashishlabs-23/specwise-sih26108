"""
Ganga Kalyana live engine audit — Task 1 through Task 8.
Run: python scripts/ganga_audit_trace.py
"""
import json
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

GANGA_TEXT = (
    "GOVERNMENT OF KARNATAKA - BACKWARD CLASSES WELFARE DEPARTMENT\n"
    "SUPPLY, INSTALLATION & COMMISSIONING OF SUBMERSIBLE PUMPS SETS WITH ACCESSORIES SUITABLE FOR 165 MM DIA BOREWELLS.\n\n"
    "Technical specifications:\n"
    "1. Submersible Pumpset: suitable for 165 mm dia borewells, multi-stage centrifugal pump conforming to IS 8034:2018.\n"
    "2. Submersible Motor: water-filled submersible motor conforming to IS 9283:2024, 3-phase, 415V, 50Hz, 5 HP.\n"
    "3. Riser Pipes: 50mm GI pipes Class B as per IS 1239 / 90.\n"
    "4. Submersible Cable: 3-core flat PVC insulated submersible cable as per IS 694-1990.\n"
    "5. Control Panel: starter panel with switchgear and capacitors conforming to IS 13947 / IS 2834."
)

DIFFERENTIAL_TEXTS = {
    "borewell_submersible": (
        "Supply of submersible pumpset suitable for 165 mm dia borewell, "
        "multi-stage centrifugal pump conforming to IS 8034:2018, 5HP motor."
    ),
    "openwell_submersible": (
        "Supply of openwell submersible pumpset for agricultural irrigation "
        "conforming to IS 14220:2018, 5HP motor, suitable for open dug wells."
    ),
    "generic_submersible": (
        "Supply of submersible pump for water supply."
    ),
}


def run_and_report(label, text):
    res = client.post("/api/v1/analyze", json={"text": text})
    assert res.status_code == 200, f"HTTP {res.status_code}"
    d = res.json()

    print(f"\n{'='*70}")
    print(f"QUERY: {label}")
    print(f"DECISION: {d['decision']}")

    print("\n-- REQUIREMENTS --")
    for r in d["requirements"]:
        print(f"  [{r['category']}] {r['value'] if 'value' in r else r['text']}")

    print("\n-- CANDIDATES (ranked) --")
    for c in d["candidates"]:
        print(f"  {c['standard_id']}  rrf={c['rrf_score']:.4f}  paths={c['retrieval_paths']}")

    print("\n-- APPLICABILITY --")
    for a in d["applicability"]:
        print(f"  {a['standard_id']}  result={a['result']}")
        for r in a["reasons"]:
            print(f"    • {r}")

    print("\n-- LIFECYCLE --")
    for lc in d["lifecycle"]:
        print(f"  {lc['standard_id']}  state={lc['state']}")

    print("\n-- COVERAGE GAPS --")
    for g in d["gaps"]:
        print(f"  [{g['state']}]  std={g['standard_id']}  req={g['requirement_id']}  reason={g['reason']}")

    print("\n-- DECISION REASONS --")
    for r in d["decision_reasons"]:
        print(f"  • {r}")

    strong = [a["standard_id"] for a in d["applicability"] if a["result"] == "strong"]
    print(f"\n-- STRONG PRIMARY STANDARDS: {strong}")

    print("\n-- CERTIFICATION --")
    for sid, cert in d["certification"].items():
        print(f"  {sid}: state={cert['state']}  mandate={cert.get('mandate_status','?')}")
        evids = cert.get("evidence_ids", [])
        print(f"    evidence_ids={evids}")

    print("\n-- EVIDENCE RECORDS INCLUDED --")
    for e in d.get("evidence", []):
        print(f"  {e['evidence_id']}  text={e['text'][:100]}")

    return d


# ── TASK 1 & 4: Local engine run on full Ganga tender ─────────────────────────
data = run_and_report("GANGA_KALYANA_FULL", GANGA_TEXT)

# ── TASK 7: QCO evidence audit ────────────────────────────────────────────────
print("\n\n" + "="*70)
print("QCO EVIDENCE AUDIT")
for sid, cert in data["certification"].items():
    print(f"\nStandard: {sid}")
    print(f"  state        = {cert['state']}")
    print(f"  mandate_status = {cert.get('mandate_status','MISSING')}")
    print(f"  qco_orders   = {cert.get('qco_orders', [])}")
    print(f"  description  = {cert.get('description','')[:200]}")
    print(f"  evidence_ids = {cert.get('evidence_ids', [])}")

# ── TASK 5: Differential test ─────────────────────────────────────────────────
diff_results = {}
for label, txt in DIFFERENTIAL_TEXTS.items():
    d2 = run_and_report(label.upper(), txt)
    strong2 = [a["standard_id"] for a in d2["applicability"] if a["result"] == "strong"]
    diff_results[label] = {
        "decision": d2["decision"],
        "strong": strong2,
        "top_candidate": d2["candidates"][0]["standard_id"] if d2["candidates"] else None,
    }

print("\n\n" + "="*70)
print("DIFFERENTIAL SUMMARY")
for label, r in diff_results.items():
    print(f"  {label}: decision={r['decision']}  strong={r['strong']}  top={r['top_candidate']}")
