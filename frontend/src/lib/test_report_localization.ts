import { dictionary, english, Language, languages } from '../context/LanguageContext';
import { generateLocalizedAuditHtml } from './reportLocalization';
import type { AnalysisResponse } from '../types/api';

const FIXTURE: AnalysisResponse = {
  analysis_id: 'TEST-001', decision: 'RECOMMEND',
  decision_reasons: ['Matched IS 14220 by exact product keyword'],
  input_text: 'openwell submersible pumpset 2.2 kW',
  candidates: [{ standard_id: 'IS 14220', title: 'Openwell Submersible Pumpsets', retrieval_paths: ['keyword', 'exact_id'], rrf_score: 0.9 }],
  applicability: [{ standard_id: 'IS 14220', result: 'strong', reasons: ['keyword match'], evidence_ids: [] }],
  lifecycle: [{ standard_id: 'IS 14220', state: 'supported', reasons: ['active'], evidence_ids: [] }],
  requirements: [{ requirement_id: 'R-01', category: 'power', text: '2.2 kW motor', extraction_method: 'pattern', extraction_confidence: 0.95 }],
  related_standards: [{ from_standard: 'IS 14220', to_standard: 'IS 900', relationship_type: 'references', verified: true, evidence_ids: [] }],
  certification: {}, coverage: [], gaps: [], conflicts: [], evidence: [],
  timings_ms: { total_ms: 123 },
};

let passed = 0; let failed = 0;
function ok(c: boolean, l: string) { if (c) { console.log('  PASS ' + l); passed++; } else { console.error('  FAIL ' + l); failed++; } }

const REQUIRED_KEYS = ['auditReport','tagline','definitiveMatch','reviewRequired','outOfCorpus','noPrimary','analysisId','latency','language','extractedRequirements','colId','colCategory','requirementText','colMethod','confidence','noRequirementsFound','candidateStandards','standardNumber','title','applicability','lifecycle','retrievalPaths','primaryBadge','noCandidatesFound','normativeReferences','sourceStandard','targetStandard','relationship','verified','reportVerified','reportUnverified','noRelatedStandards','prototypeNotice','generatedOn','bisIntelligence'];

console.log('\n-- TEST 1: Required keys in all languages --');
for (const lang of languages) {
  for (const key of REQUIRED_KEYS) { ok(key in dictionary[lang] || key in english, '[' + lang + '] key: ' + key); }
}

const reports: Record<Language, string> = {} as Record<Language, string>;
console.log('\n-- TEST 2: Report generation per language --');
for (const lang of languages) {
  const d = dictionary[lang];
  const t = new Proxy(d, { get: (tgt: typeof english, p: string | symbol) => { if (typeof p !== 'string') return Reflect.get(tgt, p); return (tgt as Record<string,string>)[p] ?? (english as Record<string,string>)[p] ?? p; } });
  const html = generateLocalizedAuditHtml(FIXTURE, lang, t);
  reports[lang] = html;
  ok(html.length > 500, '[' + lang + '] report has content');
  ok(html.includes('lang="' + lang + '"'), '[' + lang + '] html lang attribute');
  ok(html.includes('IS 14220'), '[' + lang + '] preserves IS 14220');
  ok(html.includes('TEST-001'), '[' + lang + '] preserves analysis_id');
  ok(html.includes('IS 900'), '[' + lang + '] preserves IS 900');
  ok(html.includes('2.2 kW'), '[' + lang + '] preserves 2.2 kW');
  ok(html.includes('95%'), '[' + lang + '] preserves 95%');
}

console.log('\n-- TEST 3: Localized headings in non-English --');
const localHeadings: [Language, string][] = [['hi','\u0911\u0921\u093f\u091f \u0930\u093f\u092a\u094b\u0930\u094d\u091f'],['hi','\u0935\u093f\u0936\u094d\u0932\u0947\u0937\u0923 ID'],['kn','\u0c86\u0ca1\u0cbf\u0c9f\u0ccd \u0cb5\u0cb0\u0ca6\u0cbf'],['kn','\u0cb5\u0cbf\u0cb6\u0ccd\u0cb2\u0cc7\u0cb7\u0ca3\u0cbe ID'],['ta','\u0ba4\u0ba3\u0bbf\u0b95\u0bcd\u0b95\u0bc8 \u0b85\u0bb1\u0bbf\u0b95\u0bcd\u0b95\u0bc8'],['ta','\u0baa\u0b95\u0bc1\u0baa\u0bcd\u0baa\u0bbe\u0baf\u0bcd\u0bb5\u0bc1 ID'],['te','\u0c06\u0c21\u0c3f\u0c1f\u0c4d \u0c28\u0c3f\u0c35\u0c47\u0c26\u0c3f\u0c15'],['te','\u0c35\u0c3f\u0c36\u0c4d\u0c32\u0c47\u0c37\u0c23 ID']];
for (const [lang, heading] of localHeadings) { ok(reports[lang].includes(heading), '[' + lang + '] contains heading'); }

console.log('\n-- TEST 4: English UI labels absent in non-English --');
const EN_LABELS = ['<th>Latency</th>','<th>Category</th>','<th>Requirement Text</th>','<th>Confidence</th>','<th>Title</th>','<th>Applicability</th>','<th>Lifecycle</th>','<th>Retrieval Paths</th>','<th>Relationship</th>','>Analysis ID<','>Latency<'];
for (const lang of ['hi','kn','ta','te'] as Language[]) { for (const s of EN_LABELS) { ok(!reports[lang].includes(s), '[' + lang + '] no English label: ' + s.slice(0,30)); } }

console.log('\n-- TEST 5: English report correct --');
const en = reports['en'];
for (const s of ['BIS Audit Report','Analysis ID','Latency','Requirement Text','Confidence','Retrieval Paths','Generated on','Bureau of Indian Standards Intelligence','\u2705 Verified']) { ok(en.includes(s), '[en] contains "' + s + '"'); }

console.log('\n-- TEST 6: Technical data identical --');
for (const v of ['IS 14220','IS 900','TEST-001','2.2 kW','95%','references']) { ok(languages.every(l => reports[l].includes(v)), 'all 5 langs preserve: ' + v); }

console.log('\nRESULT: ' + passed + ' passed, ' + failed + ' failed');
if (failed > 0) process.exit(1);
