import json
from pathlib import Path
from app.engine import RecommendationEngine
from app.models import AnalysisRequest, StandardRecord
from app.policy.lifecycle import assess as assess_lifecycle
from datetime import date

def main():
    engine = RecommendationEngine()
    cases = json.loads(Path('data/evaluation_cases.json').read_text(encoding='utf-8'))['cases']

    print('Testing 2x Determinism across all evaluation cases...')
    determinism_passed = True
    for c in cases:
        r1 = engine.analyze(AnalysisRequest(text=c['query']))
        r2 = engine.analyze(AnalysisRequest(text=c['query']))
        d1, d2 = r1.decision, r2.decision
        c1 = [x.standard_id for x in r1.candidates]
        c2 = [x.standard_id for x in r2.candidates]
        rel1 = [x.to_standard for x in r1.related_standards]
        rel2 = [x.to_standard for x in r2.related_standards]
        strong1 = [a.standard_id for a in r1.applicability if a.result == 'strong']
        strong2 = [a.standard_id for a in r2.applicability if a.result == 'strong']
        
        match = (d1 == d2 and c1 == c2 and rel1 == rel2 and strong1 == strong2)
        case_id = c['id']
        if not match:
            determinism_passed = False
            print(f'FAIL: Non-deterministic behavior on case {case_id}: {d1} vs {d2}')
        else:
            print(f'PASS: {case_id} -> decision={d1}, strong={strong1}')

    print(f'Determinism result: {"100% IDENTICAL" if determinism_passed else "FAILED"}')

    # Check evidence on all recommendations
    for c in cases:
        r = engine.analyze(AnalysisRequest(text=c['query']))
        if r.decision == 'RECOMMEND':
            for s in r.applicability:
                if s.result == 'strong':
                    std = engine.repo.get_standard(s.standard_id)
                    assert std.evidence_ids, f'Standard {s.standard_id} has no evidence_ids!'
                    for eid in std.evidence_ids:
                        assert any(e.evidence_id == eid for e in engine.repo.evidence), f'Evidence {eid} not found!'

    # Check report sections
    sample_r = engine.analyze(AnalysisRequest(text='openwell submersible pumpset for agricultural irrigation'))
    rep = sample_r.report_html
    for sec in ['id="decision"', 'id="requirements"', 'id="primary"', 'id="related-cands"', 'id="coverage"', 'id="gaps"', 'id="conflicts"', 'id="graph"', 'id="evidence"']:
        assert sec in rep, f'Missing section {sec} in report!'

    # Test lifecycle warning case
    withdrawn_std = StandardRecord(
        standard_id="IS 8034:2002",
        title="Submersible Pumpsets (Old)",
        scope="Old submersible pumpsets",
        category="pumps",
        lifecycle_events=[{"event": "withdrawn_after_revision", "date": "2019-04-04", "evidence_ids": ["E-8034-LIFECYCLE"]}],
        evidence_ids=["E-8034-LIFECYCLE"]
    )
    lc_res = assess_lifecycle(withdrawn_std, date(2026, 9, 22))
    assert lc_res.state == "warning", f"Expected lifecycle warning for withdrawn standard, got {lc_res.state}"

    print('All acceptance invariants verified successfully!')

if __name__ == '__main__':
    main()
