export interface SourceRecord {
  source_id: string;
  name: string;
  publisher: string;
  url: string;
  source_type: "official_bis" | "secondary_search_result";
  retrieved_at: string;
  notes: string;
}

export interface CorpusEvidence {
  evidence_id: string;
  source_id: string;
  source_name: string;
  url: string;
  page?: number | null;
  text: string;
  verified: boolean;
  purpose: string;
  linked_standards: string[];
}

export interface CorpusRelationship {
  from_standard: string;
  to_standard: string;
  relationship_type: string;
  evidence_ids: string[];
  verified: boolean;
  notes: string;
}

export interface CorpusStandard {
  standard_id: string;
  title: string;
  scope: string;
  category: string;
  standard_role: string;
  role_label: string;
  versions: string[];
  provenance: string;
  evidence_ids: string[];
  related_standards: string[];
  keywords: string[];
  product_terms: string[];
  application_terms: string[];
}

export interface EvaluationCase {
  id: string;
  query: string;
  expected_contains: string[];
  expected_decision: string | null;
  notes: string;
}

export const SOURCES: SourceRecord[] = [
  {
    source_id: "BIS-14220-SUMMARY-2024",
    name: "BIS Summary of IS 14220:2018",
    publisher: "Bureau of Indian Standards",
    url: "https://www.services.bis.gov.in/tmp/tbl5_2024-11-11_1182.pdf",
    source_type: "official_bis",
    retrieved_at: "2026-09-22",
    notes: "BIS summary describing Openwell Submersible Pumpsets and agriculture/irrigation use."
  },
  {
    source_id: "BIS-PUMP-BOOKLET",
    name: "BIS Government Procurement pump standards booklet",
    publisher: "Bureau of Indian Standards",
    url: "https://www.services.bis.gov.in/php/BIS_2.0/gpportal2/assets/img/Full-BookletGP.pdf",
    source_type: "official_bis",
    retrieved_at: "2026-09-22",
    notes: "BIS material describing IS 8034:2018, IS 9079:2018, and IS 14536:2018."
  },
  {
    source_id: "BIS-8034-GUIDELINE-2018",
    name: "Implementation guideline for revised IS 8034:2018",
    publisher: "Bureau of Indian Standards",
    url: "https://www.services.bis.gov.in/tmp/CMD3_IS8034_guidelines_17112018.pdf",
    source_type: "official_bis",
    retrieved_at: "2026-09-22",
    notes: "Documents revision from IS 8034:2002 to IS 8034:2018. Records IS 9283, IS 14536, IS 11346 as normative references. Old edition withdrawal documented after 2019-04-04."
  },
  {
    source_id: "BIS-MED20-2026",
    name: "BIS MED 20 committee material (2026)",
    publisher: "Bureau of Indian Standards",
    url: "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    source_type: "official_bis",
    retrieved_at: "2026-09-22",
    notes: "2026 BIS MED 20 committee programme of work lists IS 8034:2018, IS 14220:2018, IS 9079:2018, IS 14536:2018, IS 9283, IS 11346, IS 10572 all under Committee MED 20."
  },
  {
    source_id: "BIS-QCO-PUMPS-2023-SEARCH",
    name: "Pumps QCO 2023 — search-result summary",
    publisher: "Department for Promotion of Industry and Internal Trade (DPIIT)",
    url: "https://www.bis.gov.in/",
    source_type: "secondary_search_result",
    retrieved_at: "2026-09-22",
    notes: "Search results confirm a Pumps (Quality Control) Order 2023 was proposed by DPIIT covering IS 8034:2018 and IS 14220:2018, mandating ISI Mark. Enforcement date cited as 'to be announced'. No official gazette number or effective date confirmed in prototype corpus."
  }
];

export const EVIDENCE_RECORDS: CorpusEvidence[] = [
  {
    evidence_id: "E-14220-SCOPE",
    source_id: "BIS-14220-SUMMARY-2024",
    source_name: "BIS Summary of IS 14220:2018",
    url: "https://www.services.bis.gov.in/tmp/tbl5_2024-11-11_1182.pdf",
    page: 1,
    text: "BIS describes IS 14220:2018 as Openwell Submersible Pumpsets and discusses agriculture and irrigation applications.",
    verified: true,
    purpose: "Scope & Application Definition",
    linked_standards: ["IS 14220:2018"]
  },
  {
    evidence_id: "E-8034-SCOPE",
    source_id: "BIS-PUMP-BOOKLET",
    source_name: "BIS Government Procurement pump standards booklet",
    url: "https://www.services.bis.gov.in/php/BIS_2.0/gpportal2/assets/img/Full-BookletGP.pdf",
    page: 1,
    text: "BIS describes IS 8034:2018 as Submersible Pumpsets used for clear, cold water in agriculture and water supply, commonly in boreholes/borewells/tubewells.",
    verified: true,
    purpose: "Scope & Borewell Application Definition",
    linked_standards: ["IS 8034:2018"]
  },
  {
    evidence_id: "E-9079-SCOPE",
    source_id: "BIS-PUMP-BOOKLET",
    source_name: "BIS Government Procurement pump standards booklet",
    url: "https://www.services.bis.gov.in/php/BIS_2.0/gpportal2/assets/img/Full-BookletGP.pdf",
    page: 1,
    text: "BIS booklet identifies IS 9079:2018 as Monoset Pumps for Clear, Cold Water for Agricultural and Water Supply.",
    verified: true,
    purpose: "Scope & Monoset Pump Definition",
    linked_standards: ["IS 9079:2018"]
  },
  {
    evidence_id: "E-8034-LIFECYCLE",
    source_id: "BIS-8034-GUIDELINE-2018",
    source_name: "Implementation guideline for revised IS 8034:2018",
    url: "https://www.services.bis.gov.in/tmp/CMD3_IS8034_guidelines_17112018.pdf",
    page: 1,
    text: "IS 8034:2002 was revised as IS 8034:2018 and the old standard would stand withdrawn after 04-04-2019.",
    verified: true,
    purpose: "Lifecycle & Revision Transition Tracking",
    linked_standards: ["IS 8034:2018"]
  },
  {
    evidence_id: "E-8034-NORMREF-9283",
    source_id: "BIS-8034-GUIDELINE-2018",
    source_name: "Implementation guideline for revised IS 8034:2018",
    url: "https://www.services.bis.gov.in/tmp/CMD3_IS8034_guidelines_17112018.pdf",
    page: 1,
    text: "IS 8034:2018 guideline records IS 9283 (line-operated a.c. motors for submersible pumpsets) as a normative reference for the motor component of submersible pumpsets.",
    verified: true,
    purpose: "Normative Reference Linkage (Motor Component)",
    linked_standards: ["IS 8034:2018", "IS 9283:2024"]
  },
  {
    evidence_id: "E-8034-NORMREF-14536",
    source_id: "BIS-8034-GUIDELINE-2018",
    source_name: "Implementation guideline for revised IS 8034:2018",
    url: "https://www.services.bis.gov.in/tmp/CMD3_IS8034_guidelines_17112018.pdf",
    page: 1,
    text: "IS 8034:2018 guideline records IS 14536 (Code of practice for selection, installation, operation and maintenance of submersible pumpset) as a normative reference.",
    verified: true,
    purpose: "Normative Reference Linkage (Code of Practice)",
    linked_standards: ["IS 8034:2018", "IS 14536:2018"]
  },
  {
    evidence_id: "E-8034-NORMREF-11346",
    source_id: "BIS-8034-GUIDELINE-2018",
    source_name: "Implementation guideline for revised IS 8034:2018",
    url: "https://www.services.bis.gov.in/tmp/CMD3_IS8034_guidelines_17112018.pdf",
    page: 1,
    text: "IS 8034:2018 guideline records IS 11346 (Tests for agricultural and water supply pumps — Code of acceptance) as the hydraulic performance test method reference.",
    verified: true,
    purpose: "Test Method Reference Linkage (Acceptance Test)",
    linked_standards: ["IS 8034:2018", "IS 11346:2002"]
  },
  {
    evidence_id: "E-14220-REVISION-2026",
    source_id: "BIS-MED20-2026",
    source_name: "BIS MED 20 committee material (2026)",
    url: "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    page: 1,
    text: "2026 BIS committee material lists revision work for IS 14220:2018.",
    verified: true,
    purpose: "Committee Programme of Work & Revision Tracking",
    linked_standards: ["IS 14220:2018"]
  },
  {
    evidence_id: "E-8034-REVISION-2026",
    source_id: "BIS-MED20-2026",
    source_name: "BIS MED 20 committee material (2026)",
    url: "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    page: 1,
    text: "2026 BIS committee material lists revision work for IS 8034:2018.",
    verified: true,
    purpose: "Committee Programme of Work & Revision Tracking",
    linked_standards: ["IS 8034:2018"]
  },
  {
    evidence_id: "E-9079-REVISION-2026",
    source_id: "BIS-MED20-2026",
    source_name: "BIS MED 20 committee material (2026)",
    url: "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    page: 1,
    text: "2026 BIS committee material lists revision work for IS 9079:2018.",
    verified: true,
    purpose: "Committee Programme of Work & Revision Tracking",
    linked_standards: ["IS 9079:2018"]
  },
  {
    evidence_id: "E-14536-LISTING-2026",
    source_id: "BIS-MED20-2026",
    source_name: "BIS MED 20 committee material (2026)",
    url: "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    page: 1,
    text: "BIS committee material lists IS 14536:2018 as Selection, installation, operation and maintenance of submersible pumpset - Code of practice (First Revision).",
    verified: true,
    purpose: "Standard Designation & Committee Verification",
    linked_standards: ["IS 14536:2018", "IS 14220:2018"]
  },
  {
    evidence_id: "E-9283-LISTING-2026",
    source_id: "BIS-MED20-2026",
    source_name: "BIS MED 20 committee material (2026)",
    url: "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    page: 1,
    text: "BIS MED 20 committee material lists IS 9283 (Line operated a.c. motors for submersible pumpsets — Specification) as a standard under the submersible pumpset committee. Current revision noted as IS 9283:2024 on BIS portal.",
    verified: true,
    purpose: "Standard Designation & Motor Specification Provenance",
    linked_standards: ["IS 9283:2024"]
  },
  {
    evidence_id: "E-11346-LISTING-MED20",
    source_id: "BIS-MED20-2026",
    source_name: "BIS MED 20 committee material (2026)",
    url: "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    page: 1,
    text: "BIS MED 20 committee material lists IS 11346:2002 (Tests for agricultural and water supply pumps — Code of acceptance) as the hydraulic performance testing standard under Committee MED 20.",
    verified: true,
    purpose: "Test Method Designation & Verification",
    linked_standards: ["IS 11346:2002", "IS 9079:2018"]
  },
  {
    evidence_id: "E-10572-LISTING-MED20",
    source_id: "BIS-MED20-2026",
    source_name: "BIS MED 20 committee material (2026)",
    url: "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    page: 1,
    text: "BIS MED 20 committee material lists IS 10572:1983 (Methods of sampling for pumps) as a sampling standard under Committee MED 20.",
    verified: true,
    purpose: "Sampling & Inspection Procedure Provenance",
    linked_standards: ["IS 10572:1983"]
  },
  {
    evidence_id: "E-QCO-PUMPS-2023",
    source_id: "BIS-QCO-PUMPS-2023-SEARCH",
    source_name: "Pumps QCO 2023 — search-result summary",
    url: "https://www.bis.gov.in/",
    page: null,
    text: "Secondary search results confirm Pumps (Quality Control) Order 2023 proposed by DPIIT covers IS 8034:2018 (Submersible Pumpsets) and IS 14220:2018 (Openwell Submersible Pumpsets), requiring ISI Mark under BIS Scheme-I. Enforcement date cited as 'to be announced'. No official gazette number or effective date confirmed.",
    verified: false,
    purpose: "Proposed Regulatory & QCO Tracking (Unverified / Advisory)",
    linked_standards: ["IS 8034:2018", "IS 14220:2018"]
  }
];

export const RELATIONSHIPS: CorpusRelationship[] = [
  {
    from_standard: "IS 8034:2018",
    to_standard: "IS 9283:2024",
    relationship_type: "normative_reference",
    evidence_ids: ["E-8034-NORMREF-9283"],
    verified: true,
    notes: "IS 9283 defines line-operated A.C. motor requirements for submersible pumpsets."
  },
  {
    from_standard: "IS 8034:2018",
    to_standard: "IS 14536:2018",
    relationship_type: "normative_reference",
    evidence_ids: ["E-8034-NORMREF-14536"],
    verified: true,
    notes: "Code of practice for selection, installation, operation and maintenance of submersible pumpsets."
  },
  {
    from_standard: "IS 8034:2018",
    to_standard: "IS 11346:2002",
    relationship_type: "test_method",
    evidence_ids: ["E-8034-NORMREF-11346"],
    verified: true,
    notes: "Code of acceptance for hydraulic performance tests on agricultural and water supply pumps."
  },
  {
    from_standard: "IS 14220:2018",
    to_standard: "IS 14536:2018",
    relationship_type: "related_practice",
    evidence_ids: ["E-14536-LISTING-2026"],
    verified: true,
    notes: "Code of practice for installation and operation applied to openwell submersible units."
  },
  {
    from_standard: "IS 9079:2018",
    to_standard: "IS 11346:2002",
    relationship_type: "test_method",
    evidence_ids: ["E-11346-LISTING-MED20"],
    verified: true,
    notes: "Code of acceptance and test procedures for monoset agricultural pumps."
  }
];

export const STANDARDS: CorpusStandard[] = [
  {
    standard_id: "IS 14220:2018",
    title: "Openwell Submersible Pumpsets — Specification",
    scope: "Openwell submersible pumpsets for clear, cold water, including agriculture and irrigation applications described in BIS summary material.",
    category: "pumps",
    standard_role: "PRIMARY_PRODUCT_STANDARD",
    role_label: "Primary Product Standard",
    versions: ["2018"],
    provenance: "BIS Summary (2024) / MED 20 Committee Material",
    evidence_ids: ["E-14220-SCOPE", "E-14220-REVISION-2026"],
    related_standards: ["IS 14536:2018"],
    keywords: ["openwell", "submersible", "pumpset", "agriculture", "irrigation", "water supply"],
    product_terms: ["openwell"],
    application_terms: ["agriculture", "irrigation", "water supply"]
  },
  {
    standard_id: "IS 8034:2018",
    title: "Submersible Pumpsets — Specification",
    scope: "Submersible pumpsets for clear, cold water, commonly used in boreholes/borewells/tubewells for agriculture and water supply.",
    category: "pumps",
    standard_role: "PRIMARY_PRODUCT_STANDARD",
    role_label: "Primary Product Standard",
    versions: ["2018"],
    provenance: "BIS Government Procurement Booklet / Implementation Guidelines (2018)",
    evidence_ids: ["E-8034-SCOPE", "E-8034-LIFECYCLE", "E-8034-NORMREF-9283", "E-8034-NORMREF-14536", "E-8034-NORMREF-11346", "E-8034-REVISION-2026"],
    related_standards: ["IS 9283:2024", "IS 14536:2018", "IS 11346:2002"],
    keywords: ["submersible", "pumpset", "borewell", "borehole", "tubewell", "agriculture", "water supply"],
    product_terms: ["submersible pumpset", "submersible pumpsets"],
    application_terms: ["borewell", "borehole", "tubewell", "agriculture", "water supply"]
  },
  {
    standard_id: "IS 9079:2018",
    title: "Monoset Pumps for Clear, Cold Water for Agricultural and Water Supply Purposes",
    scope: "Monoset pumps for clear, cold water for agricultural and water supply purposes.",
    category: "pumps",
    standard_role: "PRIMARY_PRODUCT_STANDARD",
    role_label: "Primary Product Standard",
    versions: ["2018"],
    provenance: "BIS Government Procurement Booklet / MED 20 Committee Material",
    evidence_ids: ["E-9079-SCOPE", "E-9079-REVISION-2026"],
    related_standards: ["IS 11346:2002"],
    keywords: ["monoset", "pump", "clear water", "cold water", "agriculture", "water supply"],
    product_terms: ["monoset", "monoset pump"],
    application_terms: ["agriculture", "water supply", "clear water", "cold water"]
  },
  {
    standard_id: "IS 14536:2018",
    title: "Selection, Installation, Operation and Maintenance of Submersible Pumpset — Code of Practice",
    scope: "Code of practice for selection, installation, operation and maintenance of submersible pumpset, as listed in BIS committee material.",
    category: "pumps",
    standard_role: "CODE_OF_PRACTICE",
    role_label: "Code of Practice",
    versions: ["2018"],
    provenance: "BIS MED 20 Committee Material (2026)",
    evidence_ids: ["E-14536-LISTING-2026"],
    related_standards: ["IS 8034:2018", "IS 14220:2018"],
    keywords: ["submersible", "pumpset", "selection", "installation", "operation", "maintenance"],
    product_terms: [],
    application_terms: ["selection", "installation", "operation", "maintenance"]
  },
  {
    standard_id: "IS 9283:2024",
    title: "Line Operated A.C. Motors for Submersible Pumpsets — Specification",
    scope: "Specification for line-operated a.c. motors designed for use in submersible pumpsets. Normative reference of IS 8034:2018.",
    category: "pumps",
    standard_role: "RELATED_STANDARD",
    role_label: "Related Specification (Motors)",
    versions: ["2024"],
    provenance: "BIS MED 20 Committee Material & IS 8034:2018 Normative Reference",
    evidence_ids: ["E-9283-LISTING-2026", "E-8034-NORMREF-9283"],
    related_standards: ["IS 8034:2018"],
    keywords: ["motor", "submersible", "pumpset", "a.c. motor", "line operated"],
    product_terms: ["submersible pumpset motor", "motor for submersible"],
    application_terms: ["submersible", "borewell", "borehole", "tubewell"]
  },
  {
    standard_id: "IS 11346:2002",
    title: "Tests for Agricultural and Water Supply Pumps — Code of Acceptance",
    scope: "Code of acceptance for hydraulic performance testing of pumps used in agricultural and water supply applications. Referenced by IS 8034:2018 and IS 9079:2018.",
    category: "pumps",
    standard_role: "TEST_METHOD",
    role_label: "Test Method (Acceptance Code)",
    versions: ["2002"],
    provenance: "BIS MED 20 Committee Programme of Work (2026)",
    evidence_ids: ["E-11346-LISTING-MED20", "E-8034-NORMREF-11346"],
    related_standards: ["IS 8034:2018", "IS 9079:2018"],
    keywords: ["test", "agricultural pump", "water supply pump", "hydraulic", "performance", "acceptance"],
    product_terms: [],
    application_terms: ["agricultural pump", "water supply pump", "hydraulic performance"]
  },
  {
    standard_id: "IS 10572:1983",
    title: "Methods of Sampling for Pumps",
    scope: "Methods of sampling and criteria for conformity for pumps, used in BIS certification under Committee MED 20.",
    category: "pumps",
    standard_role: "TEST_METHOD",
    role_label: "Test Method (Sampling & Inspection)",
    versions: ["1983"],
    provenance: "BIS MED 20 Committee Material (2026)",
    evidence_ids: ["E-10572-LISTING-MED20"],
    related_standards: [],
    keywords: ["sampling", "pump", "conformity", "inspection"],
    product_terms: [],
    application_terms: ["sampling", "conformity", "inspection"]
  }
];

export const EVALUATION_CASES: EvaluationCase[] = [
  {
    id: "openwell-primary-recommend",
    query: "openwell submersible pumpset for agricultural irrigation",
    expected_contains: ["IS 14220:2018"],
    expected_decision: "RECOMMEND",
    notes: "openwell product term discriminates IS 14220:2018 as the sole strong primary standard."
  },
  {
    id: "borewell-submersible-recommend",
    query: "submersible pumpsets for a borewell supplying agricultural water",
    expected_contains: ["IS 8034:2018"],
    expected_decision: "RECOMMEND",
    notes: "borewell application term + 'submersible pumpsets' product term discriminate IS 8034:2018."
  },
  {
    id: "monoset-primary-recommend",
    query: "monoset pump for clear cold water for agriculture",
    expected_contains: ["IS 9079:2018"],
    expected_decision: "RECOMMEND",
    notes: "monoset product term uniquely identifies IS 9079:2018."
  },
  {
    id: "is-number-lookup",
    query: "procurement as per IS 14220 openwell submersible pumpset",
    expected_contains: ["IS 14220:2018"],
    expected_decision: "RECOMMEND",
    notes: "Explicit IS 14220 reference in query must be retrieved via exact_id path."
  },
  {
    id: "related-standard-discovery",
    query: "submersible pumpsets for a borewell supplying agricultural water",
    expected_contains: ["IS 9283:2024", "IS 11346:2002", "IS 14536:2018"],
    expected_decision: null,
    notes: "IS 8034:2018 is the primary candidate. Graph expansion surfaces its normative references: IS 9283 (motor), IS 11346 (test method), IS 14536 (CoP) at hop=1."
  },
  {
    id: "unsupported-out-of-corpus",
    query: "advanced underwater robotic mining vehicle",
    expected_contains: [],
    expected_decision: "OUT_OF_CORPUS",
    notes: "Completely outside the pump corpus; no candidates above relevance floor."
  },
  {
    id: "ambiguous-submersible-generic",
    query: "submersible pump for water supply",
    expected_contains: ["IS 8034:2018"],
    expected_decision: null,
    notes: "Generic submersible query without well type distinction triggers ABSTAIN or REVIEW."
  },
  {
    id: "lifecycle-revision-under-print",
    query: "openwell submersible pumpset for agricultural irrigation",
    expected_contains: ["IS 14220:2018"],
    expected_decision: "RECOMMEND",
    notes: "revision_under_print lifecycle event does not block RECOMMEND while current standard is in force."
  },
  {
    id: "is-number-lookup-8034",
    query: "specification compliance for IS 8034 submersible pumpsets",
    expected_contains: ["IS 8034:2018"],
    expected_decision: "RECOMMEND",
    notes: "Explicit IS 8034 reference in query is retrieved via exact_id path."
  },
  {
    id: "certification-qco-unverified-handling",
    query: "submersible pumpsets for a borewell supplying agricultural water with mandatory QCO ISI mark compliance",
    expected_contains: ["IS 8034:2018"],
    expected_decision: "RECOMMEND",
    notes: "QCO is proposed but unverified; marked not_verified_in_prototype_corpus without blocking valid standard recommendation."
  }
];
