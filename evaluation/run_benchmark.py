"""
SpecWise Benchmark Runner v2
============================
Runs the full evaluation suite and reports:
  - Per-case results
  - Aggregate rates: candidate_hit, decision_hit, cert_hit
  - Per-category breakdown
  - Safety failures (false RECOMMEND / false non-OOC)
  - Failure root-cause table
"""

import json
import sys
import time
from pathlib import Path

# Allow running from either project root or evaluation/ dir
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.engine import RecommendationEngine
from app.models import AnalysisRequest


SAFETY_FORBIDDEN_DECISIONS = {"RECOMMEND"}  # decisions that must NOT appear on safety cases


def is_safety_case(case: dict) -> bool:
    """A case is a safety case if it expects OUT_OF_CORPUS and expected_contains is empty."""
    return (
        case.get("expected_decision") in {"OUT_OF_CORPUS"}
        and not case.get("expected_contains")
    ) or case.get("category") == "adversarial_safety"


def run_case(engine: RecommendationEngine, case: dict) -> dict:
    t0 = time.perf_counter()
    r = engine.analyze(AnalysisRequest(text=case["query"]))
    elapsed_ms = (time.perf_counter() - t0) * 1000

    actual_candidates = {x.standard_id for x in r.candidates}
    related_ids = {x.to_standard for x in r.related_standards}
    all_retrieved = actual_candidates | related_ids

    expected_candidates = set(case.get("expected_contains", []))
    expected_decision = case.get("expected_decision")

    # candidate_hit: at least one expected standard was retrieved
    if expected_candidates:
        candidate_hit = bool(expected_candidates & all_retrieved)
        missing = sorted(expected_candidates - all_retrieved)
        extra = sorted(all_retrieved - expected_candidates)
    else:
        # For OOC/safety cases: a hit means we correctly produce no candidates
        candidate_hit = r.decision in {"OUT_OF_CORPUS", "ABSTAIN"}
        missing = []
        extra = sorted(actual_candidates)

    decision_hit = (expected_decision is None) or (r.decision == expected_decision)

    # Certification check
    expected_cert = case.get("expected_cert") or {}
    cert_hit = True
    cert_failures = []
    for sid, exp_state in expected_cert.items():
        actual_state = r.certification.get(sid).state if sid in r.certification else None
        if actual_state != exp_state:
            cert_hit = False
            cert_failures.append({
                "standard_id": sid,
                "expected": exp_state,
                "actual": actual_state,
            })

    # Safety check: safety cases must never produce RECOMMEND
    is_safe = True
    safety_violation = None
    if is_safety_case(case) and r.decision in SAFETY_FORBIDDEN_DECISIONS:
        is_safe = False
        safety_violation = f"Safety case produced forbidden decision: {r.decision}"

    # Determine overall pass/fail
    passed = candidate_hit and decision_hit and cert_hit and is_safe

    return {
        "id": case["id"],
        "category": case.get("category", "unknown"),
        "decision": r.decision,
        "expected_decision": expected_decision,
        "decision_hit": decision_hit,
        "candidate_hit": candidate_hit,
        "cert_hit": cert_hit,
        "is_safe": is_safe,
        "passed": passed,
        "safety_violation": safety_violation,
        "cert_failures": cert_failures,
        "missing_candidates": missing,
        "extra_candidates": extra,
        "candidates": sorted(actual_candidates),
        "related_expanded": sorted(related_ids),
        "strong_applicability": [
            a.standard_id for a in r.applicability if a.result == "strong"
        ],
        "decision_reasons": r.decision_reasons,
        "elapsed_ms": round(elapsed_ms, 1),
        "notes": case.get("notes", ""),
    }


def aggregate(rows: list[dict], cases: list[dict]) -> dict:
    n = len(rows)

    # Overall rates
    candidate_hit_rate = sum(x["candidate_hit"] for x in rows) / max(n, 1)
    decision_rows = [x for x in rows if x["expected_decision"] is not None]
    decision_hit_rate = (
        sum(x["decision_hit"] for x in decision_rows) / max(len(decision_rows), 1)
        if decision_rows else 1.0
    )
    cert_cases_with_expected = [
        c for c in cases if c.get("expected_cert")
    ]
    cert_ids = {c["id"] for c in cert_cases_with_expected}
    cert_rows = [x for x in rows if x["id"] in cert_ids]
    cert_hit_rate = (
        sum(x["cert_hit"] for x in cert_rows) / max(len(cert_rows), 1)
        if cert_rows else 1.0
    )
    safety_rows = [x for x in rows if not x["is_safe"]]
    overall_pass_rate = sum(x["passed"] for x in rows) / max(n, 1)

    # Per-category
    categories: dict[str, dict] = {}
    for row in rows:
        cat = row["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0, "candidate_hit": 0, "decision_hit": 0}
        categories[cat]["total"] += 1
        categories[cat]["passed"] += int(row["passed"])
        categories[cat]["candidate_hit"] += int(row["candidate_hit"])
        if row["expected_decision"] is not None:
            categories[cat].setdefault("decision_cases", 0)
            categories[cat]["decision_cases"] = categories[cat].get("decision_cases", 0) + 1
            categories[cat]["decision_hit"] += int(row["decision_hit"])

    for cat, stats in categories.items():
        stats["pass_rate"] = round(stats["passed"] / max(stats["total"], 1), 3)
        stats["candidate_hit_rate"] = round(stats["candidate_hit"] / max(stats["total"], 1), 3)

    # Failures
    failures = [x for x in rows if not x["passed"]]

    return {
        "total_cases": n,
        "overall_pass_rate": round(overall_pass_rate, 3),
        "candidate_hit_rate": round(candidate_hit_rate, 3),
        "decision_hit_rate": round(decision_hit_rate, 3),
        "cert_hit_rate": round(cert_hit_rate, 3),
        "safety_violations": len(safety_rows),
        "safety_violation_ids": [x["id"] for x in safety_rows],
        "failures": len(failures),
        "failure_ids": [x["id"] for x in failures],
        "per_category": categories,
    }


def print_summary(agg: dict, rows: list[dict]) -> None:
    print("\n" + "=" * 68)
    print("  SpecWise Benchmark v2 — Results Summary")
    print("=" * 68)
    print(f"  Total cases       : {agg['total_cases']}")
    print(f"  Overall pass rate : {agg['overall_pass_rate']:.1%}")
    print(f"  Candidate hit rate: {agg['candidate_hit_rate']:.1%}")
    print(f"  Decision hit rate : {agg['decision_hit_rate']:.1%}")
    print(f"  Cert hit rate     : {agg['cert_hit_rate']:.1%}")
    print(f"  Safety violations : {agg['safety_violations']}")
    if agg["safety_violation_ids"]:
        print(f"    !! VIOLATIONS: {', '.join(agg['safety_violation_ids'])}")
    print()

    print("  Per-category breakdown:")
    print(f"    {'Category':<28} {'Pass':>5}  {'Cand%':>6}  N")
    print(f"    {'-'*28} {'-'*5}  {'-'*6}  {'-'*3}")
    for cat, s in sorted(agg["per_category"].items()):
        print(f"    {cat:<28} {s['pass_rate']:>5.1%}  {s['candidate_hit_rate']:>6.1%}  {s['total']}")

    if agg["failures"]:
        print(f"\n  Failures ({agg['failures']}):")
        for row in rows:
            if not row["passed"]:
                flags = []
                if not row["candidate_hit"]:
                    flags.append(f"cand_miss={row['missing_candidates']}")
                if not row["decision_hit"]:
                    flags.append(f"dec={row['decision']}!={row['expected_decision']}")
                if not row["cert_hit"]:
                    flags.append(f"cert={row['cert_failures']}")
                if not row["is_safe"]:
                    flags.append(f"SAFETY:{row['safety_violation']}")
                print(f"    [{row['id']}] {' | '.join(flags)}")
    else:
        print("\n  All cases passed.")

    print("=" * 68 + "\n")


def main(output_json: str = None):
    engine = RecommendationEngine()

    # Load cases
    if engine.repo.benchmark_cases:
        cases = [c.model_dump() for c in engine.repo.benchmark_cases]
    else:
        cases = json.loads(
            Path("data/evaluation_cases.json").read_text(encoding="utf-8")
        )["cases"]

    print(f"Running {len(cases)} benchmark cases ...")
    rows = []
    for i, c in enumerate(cases, 1):
        print(f"  [{i:02d}/{len(cases)}] {c['id']} ... ", end="", flush=True)
        result = run_case(engine, c)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status} {result['decision']} ({result['elapsed_ms']:.0f}ms)")
        rows.append(result)

    agg = aggregate(rows, cases)
    print_summary(agg, rows)

    payload = {"summary": agg, "cases": rows}

    if output_json:
        out = Path(output_json)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Full results written to: {out}")
    else:
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SpecWise Benchmark Runner v2")
    parser.add_argument("--output", "-o", default=None, help="Write JSON output to file")
    args = parser.parse_args()
    main(output_json=args.output)
