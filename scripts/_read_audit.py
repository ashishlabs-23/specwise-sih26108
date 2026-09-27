"""Extract just TC-01 through TC-04 results and TC-11 through TC-16 from saved JSON."""
import json

with open("scripts/_fresh_audit_results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

for r in results:
    tid = r["id"]
    if tid in {"TC-01-OPENWELL","TC-02-MONOSET","TC-03-REGENERATIVE","TC-04-JET-PUMP",
               "TC-11-AMBIGUOUS","TC-12-MULTI-ITEM","TC-13-PARTIAL-CORPUS",
               "TC-14-SWITCHGEAR","TC-15-OOC","TC-16-NO-IS"}:
        print(f"\n{tid} [{r['category']}]")
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
        print(f"  Reasons: {r['decision_reasons']}")
        print(f"  Evidence: {r['evidence_count']} records  {r['evidence_ids'][:4]}")
