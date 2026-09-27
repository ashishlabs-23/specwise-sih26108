"""
Fresh Procurement Input Exploration — SIH26108 SpecWise
Run: python -m scripts.fresh_procurement_audit
Covers all 20 test categories. Outputs structured JSON + human-readable summary.
"""
import json
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

# ── 20 fresh test inputs ──────────────────────────────────────────────────────
TESTS = [
    # 1. OPENWELL PUMP
    {
        "id": "TC-01-OPENWELL",
        "category": "openwell_pump",
        "text": (
            "Procurement of 5 HP openwell submersible pumpsets for lift irrigation "
            "and dewatering applications at rural agricultural fields."
        ),
    },
    # 2. AGRICULTURAL MONOSET PUMP
    {
        "id": "TC-02-MONOSET",
        "category": "agricultural_monoset",
        "text": (
            "Supply of 3 HP electric monoset pumps for agricultural water supply, "
            "suitable for clear cold water, horizontal mounting, open dug well installation."
        ),
    },
    # 3. REGENERATIVE PUMP
    {
        "id": "TC-03-REGENERATIVE",
        "category": "regenerative_pump",
        "text": (
            "Procurement of single-phase regenerative peripheral pumps for domestic "
            "water supply, handling clear cold water, suitable for continuous operation "
            "in residential buildings and small farms."
        ),
    },
    # 4. CENTRIFUGAL JET PUMP
    {
        "id": "TC-04-JET-PUMP",
        "category": "centrifugal_jet",
        "text": (
            "Supply of centrifugal deep well jet pumpsets for domestic water lifting "
            "with built-in ejector, suitable for well depths up to 7 metres."
        ),
    },
    # 5. GENERAL ROTODYNAMIC PUMP
    {
        "id": "TC-05-ROTODYNAMIC",
        "category": "rotodynamic_general",
        "text": (
            "Supply of rotodynamic pumps for industrial cooling water circulation, "
            "including pump unit, motor, and drive coupling assembly."
        ),
    },
    # 6. CABLE-ONLY PROCUREMENT
    {
        "id": "TC-06-CABLE",
        "category": "cable_only",
        "text": (
            "Supply of PVC insulated unsheathed and sheathed electrical cables for "
            "working voltages up to 1100 V for fixed wiring in buildings and industrial panels."
        ),
    },
    # 7. LOW-VOLTAGE FUSE
    {
        "id": "TC-07-FUSE",
        "category": "lv_fuse",
        "text": (
            "Supply of low-voltage fuses for electrical circuit protection in residential "
            "distribution boards and consumer units — general requirements."
        ),
    },
    # 8. HISTORICAL STANDARD REFERENCE (IS 8034:2002, not IS 14220 from Ganga)
    {
        "id": "TC-08-HISTORICAL-REF",
        "category": "historical_reference",
        "text": (
            "Supply of submersible pumpsets for borewell installation conforming to "
            "IS 8034:2002 and motor conforming to IS 9283."
        ),
    },
    # 9. EXPLICIT CURRENT IS REFERENCE
    {
        "id": "TC-09-EXPLICIT-CURRENT",
        "category": "explicit_current_ref",
        "text": (
            "Procurement of submersible pumpsets strictly conforming to IS 8034:2018 "
            "for agricultural borewell water supply scheme."
        ),
    },
    # 10. EXPLICIT UNKNOWN IS REFERENCE
    {
        "id": "TC-10-FAKE-IS",
        "category": "fake_is_reference",
        "text": (
            "Supply of electric pumps conforming to IS 77777:2026 and IS 55555:2025 "
            "for sewage handling and sludge transfer applications."
        ),
    },
    # 11. AMBIGUOUS PUMP QUERY
    {
        "id": "TC-11-AMBIGUOUS",
        "category": "ambiguous_pump",
        "text": (
            "Supply of 5 HP submersible pumps for agricultural water supply — "
            "specifications to be confirmed."
        ),
    },
    # 12. MULTI-ITEM PUMP PROCUREMENT (new, not Ganga)
    {
        "id": "TC-12-MULTI-ITEM",
        "category": "multi_item_pump",
        "text": (
            "Procurement package for rural water scheme: "
            "(a) 3 HP openwell submersible pumpset for open dug well; "
            "(b) water-filled submersible motor 415V 3-phase; "
            "(c) 3-core flat PVC insulated submersible cable 1100V grade; "
            "(d) 40mm GI rising main Class C."
        ),
    },
    # 13. PARTIAL-CORPUS PROCUREMENT
    {
        "id": "TC-13-PARTIAL-CORPUS",
        "category": "partial_corpus",
        "text": (
            "Supply package for solar irrigation scheme: "
            "(a) submersible pumpset for borewell — 3 HP; "
            "(b) 3 kW mono-crystalline solar PV modules; "
            "(c) MPPT solar charge controller 48V; "
            "(d) galvanised steel module mounting structure."
        ),
    },
    # 14. NON-PUMP ELECTRICAL PROCUREMENT
    {
        "id": "TC-14-SWITCHGEAR",
        "category": "non_pump_electrical",
        "text": (
            "Supply and installation of 11 kV vacuum circuit breaker panels with "
            "numerical protection relays, current transformers, voltage transformers, "
            "copper busbars and cable termination kits."
        ),
    },
    # 15. COMPLETELY OUT-OF-CORPUS
    {
        "id": "TC-15-OOC",
        "category": "out_of_corpus",
        "text": (
            "Supply and installation of fire sprinkler system, hydrant network, "
            "hose reels, fire alarm control panel, heat detectors and smoke detectors "
            "for multi-storey commercial building."
        ),
    },
    # 16. NO EXPLICIT IS NUMBER
    {
        "id": "TC-16-NO-IS",
        "category": "no_is_number",
        "text": (
            "Supply of centrifugal water pump suitable for agricultural irrigation, "
            "5 HP motor, clear water handling, three-phase power supply, 415 volts."
        ),
    },
    # 17. FAKE/PLAUSIBLE IS NUMBER (plausible numbering style)
    {
        "id": "TC-17-PLAUSIBLE-FAKE",
        "category": "plausible_fake_is",
        "text": (
            "Supply of submersible pumpsets conforming to IS 14220:2026 (proposed revision) "
            "and motor conforming to IS 9283:2024, with ISI mark mandatory."
        ),
    },
    # 18. CONFLICTING TECHNICAL REQUIREMENTS
    {
        "id": "TC-18-CONFLICTING",
        "category": "conflicting_requirements",
        "text": (
            "Supply of openwell submersible pumpset for borewell installation, "
            "conforming to both IS 14220:2018 and IS 8034:2018 simultaneously."
        ),
    },
    # 19. VERY SHORT QUERY
    {
        "id": "TC-19-SHORT",
        "category": "very_short",
        "text": "pump",
    },
    # 20. LONG NUMBERED PROCUREMENT SPECIFICATION
    {
        "id": "TC-20-LONG-SPEC",
        "category": "long_numbered_spec",
        "text": (
            "GOVERNMENT PROCUREMENT SPECIFICATION — AGRICULTURAL WATER SUPPLY SCHEME\n"
            "1.0 SCOPE: Supply, installation and commissioning of openwell submersible "
            "pumpsets for lift irrigation from open dug wells in rural villages.\n"
            "2.0 PUMP UNIT: Multi-stage centrifugal pump, clear cold water service, "
            "5 HP output, 415V 3-phase 50Hz, ISI marked.\n"
            "3.0 MOTOR: Water-filled submersible induction motor conforming to relevant "
            "BIS specification for submersible motor windings.\n"
            "4.0 STARTER: Direct-on-line starter with overload relay and single-phase "
            "preventer mounted in weatherproof enclosure.\n"
            "5.0 CABLE: 3-core flat submersible cable, PVC insulated, 1100V grade, "
            "length as per borewell depth.\n"
            "6.0 DELIVERY MAIN: 50mm diameter galvanised iron pipes Class B.\n"
            "7.0 TESTING: Factory acceptance testing per applicable BIS code of practice "
            "for agricultural pump acceptance tests.\n"
            "8.0 WARRANTY: 24 months from date of commissioning.\n"
            "9.0 QUANTITY: 50 units per district, 5 districts total."
        ),
    },
]


def run_test(tc):
    res = client.post("/api/v1/analyze", json={"text": tc["text"]})
    assert res.status_code == 200, f"HTTP {res.status_code} for {tc['id']}"
    d = res.json()

    # Extract derived fields
    strong = [a["standard_id"] for a in d["applicability"] if a["result"] == "strong"]
    possible = [a["standard_id"] for a in d["applicability"] if a["result"] == "possible"]
    weak = [a["standard_id"] for a in d["applicability"] if a["result"] == "weak"]

    unverified_gaps = [g for g in d["gaps"] if g["state"] == "unverified_reference"]
    edition_gaps    = [g for g in d["gaps"] if g["state"] == "edition_mismatch"]
    not_covered     = [g for g in d["gaps"] if g["state"] == "not_covered"]

    top5_cands = d["candidates"][:5]
    req_categories = {}
    for r in d["requirements"]:
        cat = r["category"]
        req_categories[cat] = req_categories.get(cat, 0) + 1

    cert_states = {sid: c["state"] for sid, c in d["certification"].items()}
    lc_states   = {l["standard_id"]: l["state"] for l in d["lifecycle"]}
    appl_map    = {a["standard_id"]: a["result"] for a in d["applicability"]}

    return {
        "id": tc["id"],
        "category": tc["category"],
        "text_preview": tc["text"][:80] + "..." if len(tc["text"]) > 80 else tc["text"],
        "decision": d["decision"],
        "decision_reasons": d["decision_reasons"],
        "strong": strong,
        "possible": possible,
        "weak": weak,
        "top5_candidates": [
            {
                "id": c["standard_id"],
                "rrf": round(c["rrf_score"], 5),
                "paths": c["retrieval_paths"],
                "appl": appl_map.get(c["standard_id"], "—"),
                "lc": lc_states.get(c["standard_id"], "—"),
            }
            for c in top5_cands
        ],
        "requirements_extracted": len(d["requirements"]),
        "req_categories": req_categories,
        "gaps_total": len(d["gaps"]),
        "unverified_refs": [g["reason"] for g in unverified_gaps],
        "edition_mismatches": [g["reason"] for g in edition_gaps],
        "not_covered_reqs": [g["requirement_id"] for g in not_covered],
        "related_standards": [(r["from_standard"], r["to_standard"], r["relationship_type"]) for r in d["related_standards"]],
        "cert_states": cert_states,
        "evidence_count": len(d["evidence"]),
        "evidence_ids": [e["evidence_id"] for e in d["evidence"]],
        "conflicts": [c["description"] for c in d["conflicts"]],
        "candidates_total": len(d["candidates"]),
    }


results = []
for tc in TESTS:
    r = run_test(tc)
    results.append(r)

# ── Print structured summary ──────────────────────────────────────────────────
SEP = "=" * 72

print(SEP)
print("FRESH PROCUREMENT AUDIT — 20 TEST CASES")
print(SEP)

for r in results:
    print(f"\n{r['id']} [{r['category']}]")
    print(f"  Input   : {r['text_preview']}")
    print(f"  Decision: {r['decision']}")
    print(f"  Strong  : {r['strong']}")
    print(f"  Possible: {r['possible']}")
    print(f"  Reqs extracted: {r['requirements_extracted']}  cats={r['req_categories']}")
    print(f"  Gaps total: {r['gaps_total']}  (unverified={len(r['unverified_refs'])}, "
          f"edition_mismatch={len(r['edition_mismatches'])}, not_covered={len(r['not_covered_reqs'])})")
    print(f"  Top-5 candidates:")
    for c in r["top5_candidates"]:
        print(f"    {c['id']:22s}  rrf={c['rrf']:7.5f}  paths={c['paths']}  appl={c['appl']}  lc={c['lc']}")
    if r["unverified_refs"]:
        print(f"  Unverified refs: {r['unverified_refs']}")
    if r["edition_mismatches"]:
        print(f"  Edition mismatches: {r['edition_mismatches']}")
    if r["conflicts"]:
        print(f"  Conflicts: {r['conflicts']}")
    print(f"  Decision reasons: {r['decision_reasons'][:1]}")
    print(f"  Evidence records: {r['evidence_count']}  ids={r['evidence_ids'][:4]}")
    cert_summary = {sid: s for sid, s in r["cert_states"].items() if "not_verified" not in s}
    print(f"  Cert (non-unverified): {cert_summary}")
    if r["related_standards"]:
        print(f"  Related: {r['related_standards'][:3]}")

# ── Decision distribution summary ─────────────────────────────────────────────
print(f"\n{SEP}")
print("DECISION DISTRIBUTION")
dist = {}
for r in results:
    dist[r["decision"]] = dist.get(r["decision"], 0) + 1
for dec, count in sorted(dist.items()):
    print(f"  {dec}: {count}/{len(results)}")

# ── Primary-standard behavior ──────────────────────────────────────────────────
print(f"\n{SEP}")
print("PRIMARY STANDARD BEHAVIOR")
for r in results:
    primary = r["strong"][0] if r["strong"] else ("possible:" + r["possible"][0] if r["possible"] else "NONE")
    print(f"  {r['id']:28s}  decision={r['decision']:14s}  primary={primary}")

# ── Hallucination/safety check ────────────────────────────────────────────────
print(f"\n{SEP}")
print("HALLUCINATION CHECK")
CORPUS_IDS = {
    "IS 14220:2018", "IS 8034:2018", "IS 9079:2018", "IS 694:2010",
    "IS 9224 (Part 1):1979", "IS 8472:2019", "IS 12225:2019",
    "IS 11501:2017", "IS 5120:1977", "IS 14220:1994",
    # extended corpus IDs seen in retrieval
    "IS 9283:2024", "IS 1239:1990", "IS 14536:2018", "IS 11346:2002",
    "IS 1554:1988", "IS 10572:1983",
}
for r in results:
    all_cand_ids = {c["id"] for c in r["top5_candidates"]}
    unknown = all_cand_ids - CORPUS_IDS
    if unknown:
        print(f"  {r['id']}: UNKNOWN standard IDs in candidates: {unknown}  ← HALLUCINATION RISK")
    else:
        print(f"  {r['id']}: OK — all candidates are corpus-known IDs")

# ── Save JSON for reference ────────────────────────────────────────────────────
import os
out_path = os.path.join(os.path.dirname(__file__), "_fresh_audit_results.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nFull JSON saved to: {out_path}")
