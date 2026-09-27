# Blind unseen procurement evaluation — 2026-09-27

Evaluation-only. No application code, thresholds, standards or corpus records were changed.
All 20 expected-behavior JSON fixtures were written before the production upload run. PDFs were uploaded through the deployed UI using Playwright file input. API responses were captured from the same upload requests and compared with rendered UI states.

Classification counts: PASS 10, REVIEW 8, FAIL 2. UI/backend parity: 20/20.

| PDF | Domain | Expected class | Actual | Primary | Candidates | Evidence | UI/API | Class | Finding |
|---|---|---|---|---|---:|---:|---|---|---|
| BLIND-01 | water systems | meaningful_overlap | RECOMMEND | IS 8034:2018 | 8 | 13 | agree | REVIEW | Correct IS 8034 primary and decision. The PDF text retains 72 m head and 6 L/s, but neither becomes a structured head/flow requirement; coverage therefore does not explicitly account for those duty values. |
| BLIND-02 | agricultural equipment | meaningful_overlap | REVIEW | IS 8034:2018 | 8 | 13 | agree | FAIL | Open-well is extracted, and IS 14220:1994 correctly creates an edition-mismatch gap, but IS 8034:2018 is still rendered as primary. The hyphenated open-well wording did not trigger IS 8034's openwell exclusion; 24 m head and 12 L/s also remain unstructured. |
| BLIND-03 | industrial equipment | meaningful_overlap | REVIEW | — | 8 | 14 | agree | REVIEW | IS 9079:2018 is retrieved and cited, but monoblock pump sets do not produce an applicable strong primary under the corpus's monoset product terms. With synonym equivalence unverified in the corpus, withholding RECOMMEND is conservative but misses the likely intended match. |
| BLIND-04 | water systems | meaningful_overlap | RECOMMEND | IS 14220:2018 | 8 | 14 | agree | REVIEW | Correct IS 14220:2018 primary, and boilerplate does not displace the product. The long tender's 26 m head and 10 L/s discharge stay in prose rather than structured coverage, yet the UI shows RECOMMEND with no gaps. |
| BLIND-05 | mechanical | meaningful_overlap | REVIEW | IS 8034:2018 | 8 | 13 | agree | PASS | IS 8034:2018 is primary; IS 694:1990 is explicitly detected as an edition mismatch against IS 694:2010, so the mixed component package receives REVIEW rather than RECOMMEND. |
| BLIND-06 | renewable energy | partially_related | REVIEW | — | 8 | 13 | agree | REVIEW | Mixed solar/pump package correctly does not receive RECOMMEND; IS 77777:2026 remains unverified. The 5 HP submersible pump for a 90 m agricultural bore is not strong enough for IS 8034:2018 primary, leaving a not-covered pump requirement. |
| BLIND-07 | electrical | partially_related | REVIEW | — | 8 | 13 | agree | FAIL | The cited IS 1554 (Part 1):1988 is reduced to IS 1554; the year/part is lost, so the old edition is not reported as an edition mismatch. The cable standard is only weak and not primary. |
| BLIND-08 | civil/building | partially_related | ABSTAIN | — | 8 | 9 | agree | PASS | Building lift scope stays non-primary. Incidental sump-pump language yields ABSTAIN, not a pump recommendation. |
| BLIND-09 | laboratory | partially_related | OUT_OF_CORPUS | — | 0 | 0 | agree | PASS | Laboratory water-treatment skid stays OUT_OF_CORPUS despite a replaceable feed-pump accessory; candidate and evidence counts are zero. |
| BLIND-10 | industrial equipment | partially_related | OUT_OF_CORPUS | — | 0 | 0 | agree | REVIEW | Cooling tower is the procurement head and no standard is promoted, but a named circulating-water pump set is discarded with the accessory context and the document becomes OUT_OF_CORPUS instead of retaining a partial/ambiguous pump component for review. |
| BLIND-11 | electrical | clearly_outside | OUT_OF_CORPUS | — | 0 | 0 | agree | PASS | Transformer procurement is OUT_OF_CORPUS with no candidates or evidence. |
| BLIND-12 | civil/building | clearly_outside | OUT_OF_CORPUS | — | 0 | 0 | agree | PASS | Long building-retrofit tender is OUT_OF_CORPUS; boilerplate creates no candidate or evidence. |
| BLIND-13 | laboratory | clearly_outside | REVIEW | — | 8 | 8 | agree | REVIEW | The fake IS 88888:2024 is correctly unverified and no primary is shown. Eight unrelated corpus candidates and eight evidence records are nevertheless attached, creating evidence-relevance noise. |
| BLIND-14 | renewable energy | clearly_outside | OUT_OF_CORPUS | — | 0 | 0 | agree | PASS | Solar generation remains OUT_OF_CORPUS; incidental DC/AC cable language does not create a cable candidate or evidence. |
| BLIND-15 | safety/fire | clearly_outside | ABSTAIN | — | 8 | 13 | agree | REVIEW | Fire alarm/clean-agent system does not get a primary pump standard. A jockey-pump mention leaves weak candidates and 13 evidence records on an ABSTAIN result; this is conservative but noisy. |
| BLIND-16 | mechanical | ambiguous_underspecified | ABSTAIN | — | 8 | 8 | agree | PASS | Unspecified process-liquid pump receives ABSTAIN and no primary. |
| BLIND-17 | water systems | ambiguous_underspecified | OUT_OF_CORPUS | — | 0 | 0 | agree | REVIEW | The system returns OUT_OF_CORPUS for a submersible assembly for deep community wells. No recommendation is fabricated, but ABSTAIN would better express possibly relevant terminology with insufficient product detail. |
| BLIND-18 | agricultural equipment | ambiguous_underspecified | OUT_OF_CORPUS | — | 0 | 0 | agree | PASS | Unspecified water-lifting equipment contains no corpus product discriminator and is OUT_OF_CORPUS with no evidence. |
| BLIND-19 | industrial equipment | ambiguous_underspecified | REVIEW | — | 8 | 13 | agree | PASS | Generic pump sets with duty details still lack product-family specificity; REVIEW with no primary is safe. |
| BLIND-20 | medical/technical equipment | ambiguous_underspecified | REVIEW | — | 8 | 13 | agree | PASS | Ambiguous submersible drive assembly receives REVIEW with no primary; it does not infer a pump standard from the unclear assembly scope. |

## Priority failures

- BLIND-02: wrong IS 8034 primary for an open-well requirement despite a correctly detected historical IS 14220 edition mismatch.
- BLIND-07: IS 1554 (Part 1):1988 is extracted without its part/year, losing the historical edition signal.

## Relevance and evidence notes

- No clearly unrelated PDF was RECOMMENDed; no weak-only candidate was displayed as primary.
- Accessory-only lift, laboratory-skid, fire and solar wording did not generate a primary recommendation.
- Fake explicit references remained unverified. BLIND-13 still displayed unrelated corpus candidates/evidence, and BLIND-15 displayed weak accessory-related candidates/evidence.
- Backend evidence records were existing corpus records, not invented records; the concern is relevance/presentation, not fabricated source text.
- PDF extracted text preserved tender wording across page wraps. However, common duty formats such as `L/s`, `L/min`, and metre head were not emitted as structured flow/head attributes in these cases.
- Certification states were captured for all cases. Where a primary existed, it was shown as QCO Proposed / Unconfirmed, not verified certification. BLIND-02's wrong primary also makes that otherwise cautious status attach to the wrong standard.

See `expected/` for the pre-upload behavioral fixtures, `actual/` and `assessment.json` for field-level results, `pdfs/` for the 20 new PDFs, and `captures/` for production screenshots.
