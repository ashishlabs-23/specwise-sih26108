"""Post-hoc blind evaluation classifications; does not call or modify the app."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
rows = json.loads((ROOT / "actual-results.json").read_text(encoding="utf-8"))

judgments = {
    "BLIND-01": ("REVIEW", "Correct IS 8034 primary and decision. The PDF text retains 72 m head and 6 L/s, but neither becomes a structured head/flow requirement; coverage therefore does not explicitly account for those duty values.", "requirement extraction → coverage"),
    "BLIND-02": ("FAIL", "Open-well is extracted, and IS 14220:1994 correctly creates an edition-mismatch gap, but IS 8034:2018 is still rendered as primary. The hyphenated open-well wording did not trigger IS 8034's openwell exclusion; 24 m head and 12 L/s also remain unstructured.", "applicability → primary selection"),
    "BLIND-03": ("REVIEW", "IS 9079:2018 is retrieved and cited, but monoblock pump sets do not produce an applicable strong primary under the corpus's monoset product terms. With synonym equivalence unverified in the corpus, withholding RECOMMEND is conservative but misses the likely intended match.", "product terminology normalization → applicability"),
    "BLIND-04": ("REVIEW", "Correct IS 14220:2018 primary, and boilerplate does not displace the product. The long tender's 26 m head and 10 L/s discharge stay in prose rather than structured coverage, yet the UI shows RECOMMEND with no gaps.", "requirement extraction → coverage → decision"),
    "BLIND-05": ("PASS", "IS 8034:2018 is primary; IS 694:1990 is explicitly detected as an edition mismatch against IS 694:2010, so the mixed component package receives REVIEW rather than RECOMMEND.", "—"),
    "BLIND-06": ("REVIEW", "Mixed solar/pump package correctly does not receive RECOMMEND; IS 77777:2026 remains unverified. The 5 HP submersible pump for a 90 m agricultural bore is not strong enough for IS 8034:2018 primary, leaving a not-covered pump requirement.", "applicability"),
    "BLIND-07": ("FAIL", "The cited IS 1554 (Part 1):1988 is reduced to IS 1554; the year/part is lost, so the old edition is not reported as an edition mismatch. The cable standard is only weak and not primary.", "requirement extraction"),
    "BLIND-08": ("PASS", "Building lift scope stays non-primary. Incidental sump-pump language yields ABSTAIN, not a pump recommendation.", "—"),
    "BLIND-09": ("PASS", "Laboratory water-treatment skid stays OUT_OF_CORPUS despite a replaceable feed-pump accessory; candidate and evidence counts are zero.", "—"),
    "BLIND-10": ("REVIEW", "Cooling tower is the procurement head and no standard is promoted, but a named circulating-water pump set is discarded with the accessory context and the document becomes OUT_OF_CORPUS instead of retaining a partial/ambiguous pump component for review.", "document intent / relevance gate"),
    "BLIND-11": ("PASS", "Transformer procurement is OUT_OF_CORPUS with no candidates or evidence.", "—"),
    "BLIND-12": ("PASS", "Long building-retrofit tender is OUT_OF_CORPUS; boilerplate creates no candidate or evidence.", "—"),
    "BLIND-13": ("REVIEW", "The fake IS 88888:2024 is correctly unverified and no primary is shown. Eight unrelated corpus candidates and eight evidence records are nevertheless attached, creating evidence-relevance noise.", "retrieval / evidence assembly"),
    "BLIND-14": ("PASS", "Solar generation remains OUT_OF_CORPUS; incidental DC/AC cable language does not create a cable candidate or evidence.", "—"),
    "BLIND-15": ("REVIEW", "Fire alarm/clean-agent system does not get a primary pump standard. A jockey-pump mention leaves weak candidates and 13 evidence records on an ABSTAIN result; this is conservative but noisy.", "retrieval / evidence assembly"),
    "BLIND-16": ("PASS", "Unspecified process-liquid pump receives ABSTAIN and no primary.", "—"),
    "BLIND-17": ("REVIEW", "The system returns OUT_OF_CORPUS for a submersible assembly for deep community wells. No recommendation is fabricated, but ABSTAIN would better express possibly relevant terminology with insufficient product detail.", "relevance gate / decision semantics"),
    "BLIND-18": ("PASS", "Unspecified water-lifting equipment contains no corpus product discriminator and is OUT_OF_CORPUS with no evidence.", "—"),
    "BLIND-19": ("PASS", "Generic pump sets with duty details still lack product-family specificity; REVIEW with no primary is safe.", "—"),
    "BLIND-20": ("PASS", "Ambiguous submersible drive assembly receives REVIEW with no primary; it does not infer a pump standard from the unclear assembly scope.", "—"),
}

for row in rows:
    classification, finding, stage = judgments[row["pdf_id"]]
    row["decision_classification"] = classification
    row["evaluation_finding"] = finding
    row["failure_stages"] = [] if stage == "—" else [x.strip() for x in stage.split("→")]
    (ROOT / "actual" / f"{row['pdf_id']}.json").write_text(json.dumps(row, indent=2), encoding="utf-8")

counts = {key: sum(r["decision_classification"] == key for r in rows) for key in ("PASS", "REVIEW", "FAIL")}
(ROOT / "assessment.json").write_text(json.dumps({"counts": counts, "results": rows}, indent=2), encoding="utf-8")

lines = [
    "# Blind unseen procurement evaluation — 2026-09-27",
    "",
    "Evaluation-only. No application code, thresholds, standards or corpus records were changed.",
    "All 20 expected-behavior JSON fixtures were written before the production upload run. PDFs were uploaded through the deployed UI using Playwright file input. API responses were captured from the same upload requests and compared with rendered UI states.",
    "",
    f"Classification counts: PASS {counts['PASS']}, REVIEW {counts['REVIEW']}, FAIL {counts['FAIL']}. UI/backend parity: {sum(bool(r['ui_parity']) for r in rows)}/20.",
    "",
    "| PDF | Domain | Expected class | Actual | Primary | Candidates | Evidence | UI/API | Class | Finding |",
    "|---|---|---|---|---|---:|---:|---|---|---|",
]
for r in rows:
    primary = ", ".join(r["actual_primary_standard"]) or "—"
    finding = r["evaluation_finding"].replace("|", "/")
    lines.append(f"| {r['pdf_id']} | {r['domain']} | {r['expected_behavioral_class']} | {r['actual_decision']} | {primary} | {r['candidate_count']} | {r['evidence_count']} | {'agree' if r['ui_parity'] else 'MISMATCH'} | {r['decision_classification']} | {finding} |")
lines += [
    "",
    "## Priority failures",
    "",
    "- BLIND-02: wrong IS 8034 primary for an open-well requirement despite a correctly detected historical IS 14220 edition mismatch.",
    "- BLIND-07: IS 1554 (Part 1):1988 is extracted without its part/year, losing the historical edition signal.",
    "",
    "## Relevance and evidence notes",
    "",
    "- No clearly unrelated PDF was RECOMMENDed; no weak-only candidate was displayed as primary.",
    "- Accessory-only lift, laboratory-skid, fire and solar wording did not generate a primary recommendation.",
    "- Fake explicit references remained unverified. BLIND-13 still displayed unrelated corpus candidates/evidence, and BLIND-15 displayed weak accessory-related candidates/evidence.",
    "- Backend evidence records were existing corpus records, not invented records; the concern is relevance/presentation, not fabricated source text.",
    "- PDF extracted text preserved tender wording across page wraps. However, common duty formats such as `L/s`, `L/min`, and metre head were not emitted as structured flow/head attributes in these cases.",
    "- Certification states were captured for all cases. Where a primary existed, it was shown as QCO Proposed / Unconfirmed, not verified certification. BLIND-02's wrong primary also makes that otherwise cautious status attach to the wrong standard.",
    "",
    "See `expected/` for the pre-upload behavioral fixtures, `actual/` and `assessment.json` for field-level results, `pdfs/` for the 20 new PDFs, and `captures/` for production screenshots.",
]
(ROOT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps({"counts": counts, "ui_backend_parity": f"{sum(bool(r['ui_parity']) for r in rows)}/20", "report": str(ROOT / 'report.md')}))
