import json
from pathlib import Path
from app.engine import RecommendationEngine
from app.models import AnalysisRequest


def main():
    engine = RecommendationEngine()
    if engine.repo.benchmark_cases:
        cases = [c.model_dump() for c in engine.repo.benchmark_cases]
    else:
        cases = json.loads(Path("data/evaluation_cases.json").read_text(encoding="utf-8"))["cases"]
    rows = []

    for c in cases:
        r = engine.analyze(AnalysisRequest(text=c["query"]))
        actual_candidates = {x.standard_id for x in r.candidates}
        # For relationship-discovery cases, check graph expansion too
        related_ids = {x.to_standard for x in r.related_standards}
        all_retrieved = actual_candidates | related_ids

        expected_candidates = set(c.get("expected_contains", []))
        expected_decision = c.get("expected_decision")

        candidate_hit = (
            bool(expected_candidates & all_retrieved)
            if expected_candidates
            else r.decision in {"OUT_OF_CORPUS", "ABSTAIN"}
        )
        decision_hit = (expected_decision is None) or (r.decision == expected_decision)

        expected_cert = c.get("expected_cert")
        cert_hit = True
        if expected_cert:
            for sid, exp_state in expected_cert.items():
                actual_state = r.certification.get(sid).state if sid in r.certification else None
                if actual_state != exp_state:
                    cert_hit = False

        rows.append({
            "id": c["id"],
            "decision": r.decision,
            "expected_decision": expected_decision,
            "decision_hit": decision_hit,
            "candidate_hit": candidate_hit,
            "cert_hit": cert_hit,
            "candidates": sorted(actual_candidates),
            "related_expanded": sorted(related_ids),
            "strong_applicability": [
                a.standard_id for a in r.applicability if a.result == "strong"
            ],
        })

    candidate_hit_rate = sum(x["candidate_hit"] for x in rows) / max(len(rows), 1)
    decision_hit_rate = sum(
        x["decision_hit"] for x in rows if x["expected_decision"] is not None
    ) / max(sum(1 for x in rows if x["expected_decision"] is not None), 1)
    cert_cases = [x for x in rows if "expected_cert" in next(item for item in cases if item["id"] == x["id"])]
    cert_hit_rate = sum(x["cert_hit"] for x in cert_cases) / max(len(cert_cases), 1) if cert_cases else 1.0

    print(json.dumps({
        "candidate_hit_rate": round(candidate_hit_rate, 3),
        "decision_hit_rate": round(decision_hit_rate, 3),
        "cert_hit_rate": round(cert_hit_rate, 3),
        "cases": rows,
    }, indent=2))


if __name__ == "__main__":
    main()
