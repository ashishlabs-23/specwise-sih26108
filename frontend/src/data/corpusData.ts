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
    "source_id": "BIS-1239-SEARCH-2026",
    "name": "BIS IS 1239 Standard \u2014 web search summary 2026",
    "publisher": "Bureau of Indian Standards",
    "url": "https://www.bis.gov.in/",
    "source_type": "secondary_search_result",
    "retrieved_at": "2026-09-24",
    "notes": "Web search results from bis.gov.in confirm IS 1239 (Part 1) covers mild steel tubes (welded and seamless) for conveyance of water, gas, air and steam, classified as Light (Class A), Medium (Class B) and Heavy (Class C). Steel Tubes (Quality Control) Order 2020 mandates ISI mark. Tender explicitly cites 'IS 1239 / 90' for 50mm GI pipes Class B. This is a secondary search-result summary; no official gazette number confirmed."
  },
  {
    "source_id": "BIS-694-SEARCH-2026",
    "name": "BIS IS 694:2010 Standard \u2014 web search summary 2026",
    "publisher": "Bureau of Indian Standards",
    "url": "https://www.bis.gov.in/",
    "source_type": "secondary_search_result",
    "retrieved_at": "2026-09-24",
    "notes": "Web search results from bis.gov.in confirm IS 694:2010 specifies PVC insulated unsheathed and sheathed cables/cords with rigid and flexible conductors for rated voltages up to 1100 V. BIS product manual referenced for IS 694:2010. Tender cites 'IS 694-1990' for flat 3-core PVC insulated cables. IS 694 has been revised to 2010 edition. This is a secondary search-result summary; no gazette number confirmed."
  },
  {
    "source_id": "BIS-1554-SEARCH-2026",
    "name": "BIS IS 1554 (Part 1):1988 Standard \u2014 web search summary 2026",
    "publisher": "Bureau of Indian Standards",
    "url": "https://www.bis.gov.in/",
    "source_type": "secondary_search_result",
    "retrieved_at": "2026-09-24",
    "notes": "Web search results from bis.gov.in confirm IS 1554 (Part 1):1988 covers PVC insulated heavy-duty electric cables for working voltages up to 1100 V (armoured and unarmoured). BIS certification is mandatory. Tender explicitly cites 'IS 1554/ 1988' for PVC insulated sheathed steel wire armoured LT UG cable. This is a secondary search-result summary."
  },
  {
    "source_id": "BIS-14220-SUMMARY-2024",
    "name": "BIS Summary of IS 14220:2018",
    "publisher": "Bureau of Indian Standards",
    "url": "https://www.services.bis.gov.in/tmp/tbl5_2024-11-11_1182.pdf",
    "source_type": "official_bis",
    "retrieved_at": "2026-09-22",
    "notes": "BIS summary describing Openwell Submersible Pumpsets and agriculture/irrigation use."
  },
  {
    "source_id": "BIS-PUMP-BOOKLET",
    "name": "BIS Government Procurement pump standards booklet",
    "publisher": "Bureau of Indian Standards",
    "url": "https://www.services.bis.gov.in/php/BIS_2.0/gpportal2/assets/img/Full-BookletGP.pdf",
    "source_type": "official_bis",
    "retrieved_at": "2026-09-22",
    "notes": "BIS material describing IS 8034:2018, IS 9079:2018, and IS 14536:2018."
  },
  {
    "source_id": "BIS-8034-GUIDELINE-2018",
    "name": "Implementation guideline for revised IS 8034:2018",
    "publisher": "Bureau of Indian Standards",
    "url": "https://www.services.bis.gov.in/tmp/CMD3_IS8034_guidelines_17112018.pdf",
    "source_type": "official_bis",
    "retrieved_at": "2026-09-22",
    "notes": "Documents revision from IS 8034:2002 to IS 8034:2018. Records IS 9283, IS 14536, IS 11346 as normative references. Old edition withdrawal documented after 2019-04-04."
  },
  {
    "source_id": "BIS-MED20-2026",
    "name": "BIS MED 20 committee material (2026)",
    "publisher": "Bureau of Indian Standards",
    "url": "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    "source_type": "official_bis",
    "retrieved_at": "2026-09-22",
    "notes": "2026 BIS MED 20 committee programme of work lists IS 8034:2018, IS 14220:2018, IS 9079:2018, IS 14536:2018, IS 9283, IS 11346, IS 10572 all under Committee MED 20."
  },
  {
    "source_id": "BIS-QCO-PUMPS-2023-SEARCH",
    "name": "Pumps QCO 2023 \u2014 search-result summary",
    "publisher": "Department for Promotion of Industry and Internal Trade (DPIIT)",
    "url": "https://www.bis.gov.in/",
    "source_type": "secondary_search_result",
    "retrieved_at": "2026-09-22",
    "notes": "Search results confirm a Pumps (Quality Control) Order 2023 was proposed by DPIIT covering IS 8034:2018 and IS 14220:2018, mandating ISI Mark. Enforcement date was cited as 'to be announced'. No official gazette number or effective date was confirmed in accessible sources. This record is a secondary summary only \u2014 not a primary gazette citation."
  },
  {
    "source_id": "BIS-MED20-PUMPS-CATALOGUE",
    "name": "BIS Technical Committee MED 20 Official Work Programme & Published Standards",
    "publisher": "Bureau of Indian Standards",
    "url": "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    "source_type": "official_bis",
    "retrieved_at": "2026-09-25",
    "notes": "Official BIS MED 20 Committee record listing IS 8472, IS 12225, IS 1520, IS 1710, and IS 5120."
  },
  {
    "source_id": "BIS-ETD15-MOTORS-CATALOGUE",
    "name": "BIS Technical Committee ETD 15 Rotating Machinery Official Catalogue",
    "publisher": "Bureau of Indian Standards",
    "url": "https://www.bis.gov.in/",
    "source_type": "official_bis",
    "retrieved_at": "2026-09-25",
    "notes": "Official BIS ETD 15 records covering IS 12615:2018 (IE Code) and IS 996:2009 (Single phase small AC motors)."
  },
  {
    "source_id": "BIS-ETD07-SWITCHGEAR-CATALOGUE",
    "name": "BIS Technical Committee ETD 07 Low Voltage Switchgear Official Standards",
    "publisher": "Bureau of Indian Standards",
    "url": "https://www.bis.gov.in/",
    "source_type": "official_bis",
    "retrieved_at": "2026-09-25",
    "notes": "Official BIS ETD 07 records covering IS/IEC 60947-4-1:2019 for electromechanical contactors and motor-starters."
  },
  {
    "source_id": "BIS-CED53-PLASTIC-PIPES-CATALOGUE",
    "name": "BIS Technical Committee CED 53 / CED 50 Plastic Piping Systems",
    "publisher": "Bureau of Indian Standards",
    "url": "https://www.bis.gov.in/",
    "source_type": "official_bis",
    "retrieved_at": "2026-09-25",
    "notes": "Official BIS CED 53 & CED 50 records covering IS 4984:2016 (HDPE pipes), IS 4985:2021 (uPVC pipes), and IS 12818:2010 (uPVC casing pipes)."
  },
  {
    "source_id": "BIS-CED22-VALVES-PIPES-CATALOGUE",
    "name": "BIS Technical Committee CED 22 Public Health Engineering & Waterworks Standards",
    "publisher": "Bureau of Indian Standards",
    "url": "https://www.bis.gov.in/",
    "source_type": "official_bis",
    "retrieved_at": "2026-09-25",
    "notes": "Official BIS CED 22 records covering IS 8329:2020 (Ductile iron pipes), IS 778:1984 (Copper alloy valves), IS 5312-1:2004 (Swing check NRV), IS 14846:2000 (Sluice valves), and IS 779:1994 (Water meters)."
  },
  {
    "source_id": "BIS-ETD30-EARTHING-CODE",
    "name": "BIS Technical Committee ETD 30 Electrical Installation Safety Code",
    "publisher": "Bureau of Indian Standards",
    "url": "https://www.bis.gov.in/",
    "source_type": "official_bis",
    "retrieved_at": "2026-09-25",
    "notes": "Official BIS ETD 30 record for IS 3043:2018 Code of Practice for Earthing."
  }
];

export const EVIDENCE: CorpusEvidence[] = [
  {
    "evidence_id": "E-1239-SCOPE",
    "source_id": "BIS-1239-SEARCH-2026",
    "source_name": "BIS IS 1239 Standard \u2014 web search summary 2026",
    "url": "https://www.bis.gov.in/",
    "page": null,
    "text": "IS 1239 (Part 1) covers mild steel tubes (welded and seamless, plain end, screwed end or screwed and socketed) for conveyance of water, gas, air and steam, in Class A (Light), Class B (Medium) and Class C (Heavy). Tubes may be supplied as uncoated or hot-dip galvanized (GI). Nominal bore 6 mm to 150 mm. Tender explicitly cites 'IS 1239 / 90' for 50mm GI pipes Class B for column pipe installation.",
    "verified": false,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 1239:1990"
    ]
  },
  {
    "evidence_id": "E-694-SCOPE",
    "source_id": "BIS-694-SEARCH-2026",
    "source_name": "BIS IS 694:2010 Standard \u2014 web search summary 2026",
    "url": "https://www.bis.gov.in/",
    "page": null,
    "text": "IS 694:2010 specifies PVC insulated unsheathed and sheathed cables and cords (circular and flat) with rigid and flexible conductors for rated voltages up to and including 1100 V. Tender cites 'IS 694-1990' for flat 3-core sheathed PVC insulated submersible pump cable of sizes 2.5, 4 and 6 sq mm. IS 694 has been revised; current edition is IS 694:2010.",
    "verified": false,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 694:2010"
    ]
  },
  {
    "evidence_id": "E-1554-SCOPE",
    "source_id": "BIS-1554-SEARCH-2026",
    "source_name": "BIS IS 1554 (Part 1):1988 Standard \u2014 web search summary 2026",
    "url": "https://www.bis.gov.in/",
    "page": null,
    "text": "IS 1554 (Part 1):1988 covers PVC insulated heavy-duty electric cables (armoured and unarmoured) for working voltages up to 1100 V, used for electric supply and control including underground installation. Tender cites 'IS 1554/ 1988' for armoured LT UG cable (3.5x10 and 3.5x25 sq mm) for main connection.",
    "verified": false,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 1554:1988"
    ]
  },
  {
    "evidence_id": "E-14220-SCOPE",
    "source_id": "BIS-14220-SUMMARY-2024",
    "source_name": "BIS Summary of IS 14220:2018",
    "url": "https://www.services.bis.gov.in/tmp/tbl5_2024-11-11_1182.pdf",
    "page": 1,
    "text": "BIS describes IS 14220:2018 as Openwell Submersible Pumpsets and discusses agriculture and irrigation applications.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 14220:2018"
    ]
  },
  {
    "evidence_id": "E-8034-SCOPE",
    "source_id": "BIS-PUMP-BOOKLET",
    "source_name": "BIS Government Procurement pump standards booklet",
    "url": "https://www.services.bis.gov.in/php/BIS_2.0/gpportal2/assets/img/Full-BookletGP.pdf",
    "page": 1,
    "text": "BIS describes IS 8034:2018 as Submersible Pumpsets used for clear, cold water in agriculture and water supply, commonly in boreholes/borewells/tubewells.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 8034:2018"
    ]
  },
  {
    "evidence_id": "E-9079-SCOPE",
    "source_id": "BIS-PUMP-BOOKLET",
    "source_name": "BIS Government Procurement pump standards booklet",
    "url": "https://www.services.bis.gov.in/php/BIS_2.0/gpportal2/assets/img/Full-BookletGP.pdf",
    "page": 1,
    "text": "BIS booklet identifies IS 9079:2018 as Monoset Pumps for Clear, Cold Water for Agricultural and Water Supply.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 9079:2018"
    ]
  },
  {
    "evidence_id": "E-8034-LIFECYCLE",
    "source_id": "BIS-8034-GUIDELINE-2018",
    "source_name": "Implementation guideline for revised IS 8034:2018",
    "url": "https://www.services.bis.gov.in/tmp/CMD3_IS8034_guidelines_17112018.pdf",
    "page": 1,
    "text": "IS 8034:2002 was revised as IS 8034:2018 and the old standard would stand withdrawn after 04-04-2019.",
    "verified": true,
    "purpose": "Lifecycle & Revision Tracking",
    "linked_standards": [
      "IS 8034:2018"
    ]
  },
  {
    "evidence_id": "E-8034-NORMREF-9283",
    "source_id": "BIS-8034-GUIDELINE-2018",
    "source_name": "Implementation guideline for revised IS 8034:2018",
    "url": "https://www.services.bis.gov.in/tmp/CMD3_IS8034_guidelines_17112018.pdf",
    "page": 1,
    "text": "IS 8034:2018 guideline records IS 9283 (line-operated a.c. motors for submersible pumpsets) as a normative reference for the motor component of submersible pumpsets.",
    "verified": true,
    "purpose": "Normative Reference Linkage",
    "linked_standards": [
      "IS 8034:2018",
      "IS 9283:2024"
    ]
  },
  {
    "evidence_id": "E-8034-NORMREF-14536",
    "source_id": "BIS-8034-GUIDELINE-2018",
    "source_name": "Implementation guideline for revised IS 8034:2018",
    "url": "https://www.services.bis.gov.in/tmp/CMD3_IS8034_guidelines_17112018.pdf",
    "page": 1,
    "text": "IS 8034:2018 guideline records IS 14536 (Code of practice for selection, installation, operation and maintenance of submersible pumpset) as a normative reference.",
    "verified": true,
    "purpose": "Normative Reference Linkage",
    "linked_standards": [
      "IS 14536:2018",
      "IS 8034:2018"
    ]
  },
  {
    "evidence_id": "E-8034-NORMREF-11346",
    "source_id": "BIS-8034-GUIDELINE-2018",
    "source_name": "Implementation guideline for revised IS 8034:2018",
    "url": "https://www.services.bis.gov.in/tmp/CMD3_IS8034_guidelines_17112018.pdf",
    "page": 1,
    "text": "IS 8034:2018 guideline records IS 11346 (Tests for agricultural and water supply pumps \u2014 Code of acceptance) as the hydraulic performance test method reference.",
    "verified": true,
    "purpose": "Test Method & Acceptance Criteria",
    "linked_standards": [
      "IS 11346:2002",
      "IS 8034:2018"
    ]
  },
  {
    "evidence_id": "E-14220-REVISION-2026",
    "source_id": "BIS-MED20-2026",
    "source_name": "BIS MED 20 committee material (2026)",
    "url": "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    "page": 1,
    "text": "2026 BIS committee material lists revision work for IS 14220:2018.",
    "verified": true,
    "purpose": "Lifecycle & Revision Tracking",
    "linked_standards": []
  },
  {
    "evidence_id": "E-8034-REVISION-2026",
    "source_id": "BIS-MED20-2026",
    "source_name": "BIS MED 20 committee material (2026)",
    "url": "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    "page": 1,
    "text": "2026 BIS committee material lists revision work for IS 8034:2018.",
    "verified": true,
    "purpose": "Lifecycle & Revision Tracking",
    "linked_standards": []
  },
  {
    "evidence_id": "E-9079-REVISION-2026",
    "source_id": "BIS-MED20-2026",
    "source_name": "BIS MED 20 committee material (2026)",
    "url": "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    "page": 1,
    "text": "2026 BIS committee material lists revision work for IS 9079:2018.",
    "verified": true,
    "purpose": "Lifecycle & Revision Tracking",
    "linked_standards": []
  },
  {
    "evidence_id": "E-14536-LISTING-2026",
    "source_id": "BIS-MED20-2026",
    "source_name": "BIS MED 20 committee material (2026)",
    "url": "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    "page": 1,
    "text": "BIS committee material lists IS 14536:2018 as Selection, installation, operation and maintenance of submersible pumpset - Code of practice (First Revision).",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 14220:2018",
      "IS 14536:2018"
    ]
  },
  {
    "evidence_id": "E-9283-LISTING-2026",
    "source_id": "BIS-MED20-2026",
    "source_name": "BIS MED 20 committee material (2026)",
    "url": "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    "page": 1,
    "text": "BIS MED 20 committee material lists IS 9283 (Line operated a.c. motors for submersible pumpsets \u2014 Specification) as a standard under the submersible pumpset committee. Current revision noted as IS 9283:2024 on BIS portal.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 9283:2024"
    ]
  },
  {
    "evidence_id": "E-11346-LISTING-MED20",
    "source_id": "BIS-MED20-2026",
    "source_name": "BIS MED 20 committee material (2026)",
    "url": "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    "page": 1,
    "text": "BIS MED 20 committee material lists IS 11346:2002 (Tests for agricultural and water supply pumps \u2014 Code of acceptance) as the hydraulic performance testing standard under Committee MED 20.",
    "verified": true,
    "purpose": "Test Method & Acceptance Criteria",
    "linked_standards": [
      "IS 11346:2002",
      "IS 9079:2018"
    ]
  },
  {
    "evidence_id": "E-10572-LISTING-MED20",
    "source_id": "BIS-MED20-2026",
    "source_name": "BIS MED 20 committee material (2026)",
    "url": "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/68/300/",
    "page": 1,
    "text": "BIS MED 20 committee material lists IS 10572:1983 (Methods of sampling for pumps) as a sampling standard under Committee MED 20.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 10572:1983"
    ]
  },
  {
    "evidence_id": "E-QCO-PUMPS-2023",
    "source_id": "BIS-QCO-PUMPS-2023-SEARCH",
    "source_name": "Pumps QCO 2023 \u2014 search-result summary",
    "url": "https://www.bis.gov.in/",
    "page": null,
    "text": "Secondary search results confirm Pumps (Quality Control) Order 2023 proposed by DPIIT covers IS 8034:2018 (Submersible Pumpsets) and IS 14220:2018 (Openwell Submersible Pumpsets), requiring ISI Mark under BIS Scheme-I. Enforcement date cited as 'to be announced'. No official gazette number or effective date confirmed.",
    "verified": false,
    "purpose": "Regulatory & Certification Grounding",
    "linked_standards": []
  },
  {
    "evidence_id": "E-8472-SCOPE",
    "source_id": "BIS-MED20-PUMPS-CATALOGUE",
    "source_name": "BIS Technical Committee MED 20 Official Work Programme",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS 8472:2019 specifies requirements for regenerative pumps (both self-priming and non-self-priming) for clear, cold fresh water for agricultural and domestic water supply.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 11346:2002",
      "IS 8472:2019"
    ]
  },
  {
    "evidence_id": "E-12225-SCOPE",
    "source_id": "BIS-MED20-PUMPS-CATALOGUE",
    "source_name": "BIS Technical Committee MED 20 Official Work Programme",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS 12225:2025 (Second Revision) specifies technical requirements for centrifugal jet pumpsets used for clear, cold water supply from deep wells and shallow wells in domestic and agricultural settings.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 11346:2002",
      "IS 12225:2025"
    ]
  },
  {
    "evidence_id": "E-1520-SCOPE",
    "source_id": "BIS-MED20-PUMPS-CATALOGUE",
    "source_name": "BIS Technical Committee MED 20 Official Work Programme",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS 1520:1980 covers horizontal centrifugal pumps for clear, cold, fresh water intended primarily for agricultural purposes.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 11346:2002",
      "IS 1520:1980"
    ]
  },
  {
    "evidence_id": "E-1710-SCOPE",
    "source_id": "BIS-MED20-PUMPS-CATALOGUE",
    "source_name": "BIS Technical Committee MED 20 Official Work Programme",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS 1710:2021 specifies requirements for vertical turbine pumps (mixed flow or axial flow) for clear, cold water handling in deep tubewells, irrigation schemes, and municipal waterworks.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 11346:2002",
      "IS 1710:2021"
    ]
  },
  {
    "evidence_id": "E-5120-SCOPE",
    "source_id": "BIS-MED20-PUMPS-CATALOGUE",
    "source_name": "BIS Technical Committee MED 20 Official Work Programme",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS 5120:1977 covers general technical requirements and terminology for rotodynamic special purpose pumps.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 5120:1977"
    ]
  },
  {
    "evidence_id": "E-12615-SCOPE",
    "source_id": "BIS-ETD15-MOTORS-CATALOGUE",
    "source_name": "BIS Technical Committee ETD 15 Official Catalogue",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS 12615:2018 specifies energy efficiency classes (IE2, IE3, IE4) and performance requirements for line-operated three-phase induction motors from 0.12 kW to 1000 kW.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 12615:2018",
      "IS 9079:2018"
    ]
  },
  {
    "evidence_id": "E-996-SCOPE",
    "source_id": "BIS-ETD15-MOTORS-CATALOGUE",
    "source_name": "BIS Technical Committee ETD 15 Official Catalogue",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS 996:2009 specifies general and performance requirements for single-phase small a.c. electric motors used in domestic appliances, small pumps, and industrial tools.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 9079:2018",
      "IS 996:2009"
    ]
  },
  {
    "evidence_id": "E-60947-4-1-SCOPE",
    "source_id": "BIS-ETD07-SWITCHGEAR-CATALOGUE",
    "source_name": "BIS Technical Committee ETD 07 Official Catalogue",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS/IEC 60947-4-1:2019 covers low-voltage electromechanical contactors and motor-starters, including direct-on-line (DOL) and star-delta starters used for motor protection in pumping systems.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 12615:2018",
      "IS/IEC 60947-4-1:2019"
    ]
  },
  {
    "evidence_id": "E-4984-SCOPE",
    "source_id": "BIS-CED53-PLASTIC-PIPES-CATALOGUE",
    "source_name": "BIS Technical Committee CED 53 Official Catalogue",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS 4984:2016 specifies requirements for high density polyethylene (HDPE) pipes (PE 63, PE 80, PE 100) intended for the conveyance of potable water for domestic and agricultural water supply.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 4984:2016"
    ]
  },
  {
    "evidence_id": "E-4985-SCOPE",
    "source_id": "BIS-CED53-PLASTIC-PIPES-CATALOGUE",
    "source_name": "BIS Technical Committee CED 50 Official Catalogue",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS 4985:2021 specifies requirements for unplasticized polyvinyl chloride (uPVC) pipes for potable water supplies, irrigation, and industrial plumbing installations.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 4985:2021"
    ]
  },
  {
    "evidence_id": "E-12818-SCOPE",
    "source_id": "BIS-CED53-PLASTIC-PIPES-CATALOGUE",
    "source_name": "BIS Technical Committee CED 50 Official Catalogue",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS 12818:2010 specifies requirements for unplasticized PVC screen and casing pipes with ribbed or plain surfaces for borewells and tubewells.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 12818:2010",
      "IS 8034:2018"
    ]
  },
  {
    "evidence_id": "E-8329-SCOPE",
    "source_id": "BIS-CED22-VALVES-PIPES-CATALOGUE",
    "source_name": "BIS Technical Committee CED 22 Official Catalogue",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS 8329:2020 specifies requirements for centrifugally cast (spun) ductile iron pressure pipes with socket and spigot ends for water, gas and sewage pipelines.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 8329:2020"
    ]
  },
  {
    "evidence_id": "E-778-SCOPE",
    "source_id": "BIS-CED22-VALVES-PIPES-CATALOGUE",
    "source_name": "BIS Technical Committee CED 22 Official Catalogue",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS 778:1984 specifies copper alloy (gunmetal and brass) gate, globe and check valves for waterworks purposes suitable for maximum working pressures up to 1.6 MPa.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 14846:2000",
      "IS 778:1984"
    ]
  },
  {
    "evidence_id": "E-5312-1-SCOPE",
    "source_id": "BIS-CED22-VALVES-PIPES-CATALOGUE",
    "source_name": "BIS Technical Committee CED 22 Official Catalogue",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS 5312 (Part 1):2004 specifies requirements for swing check type reflux (non-return) valves of single door pattern for waterworks purposes on rising mains and pump discharge lines.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 5312-1:2004",
      "IS 9079:2018"
    ]
  },
  {
    "evidence_id": "E-14846-SCOPE",
    "source_id": "BIS-CED22-VALVES-PIPES-CATALOGUE",
    "source_name": "BIS Technical Committee CED 22 Official Catalogue",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS 14846:2000 specifies requirements for cast iron sluice valves (size 50 mm to 1200 mm) with inside screw non-rising spindle for waterworks and flow isolation.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 14846:2000"
    ]
  },
  {
    "evidence_id": "E-779-SCOPE",
    "source_id": "BIS-CED22-VALVES-PIPES-CATALOGUE",
    "source_name": "BIS Technical Committee CED 22 Official Catalogue",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS 779:1994 specifies requirements for inferential and semi-positive volumetric domestic water meters (size 15 mm to 50 mm) for cold potable water measurement.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 779:1994"
    ]
  },
  {
    "evidence_id": "E-3043-SCOPE",
    "source_id": "BIS-ETD30-EARTHING-CODE",
    "source_name": "BIS Technical Committee ETD 30 Official Code",
    "url": "https://www.bis.gov.in/",
    "page": 1,
    "text": "IS 3043:2018 provides code of practice for design, installation and maintenance of earthing systems in electrical installations including pumpsets, motor control centers and distribution systems.",
    "verified": true,
    "purpose": "Standard Specification & Scope Grounding",
    "linked_standards": [
      "IS 14220:2018",
      "IS 3043:2018",
      "IS 8034:2018"
    ]
  }
];

export const RELATIONSHIPS: CorpusRelationship[] = [
  {
    "from_standard": "IS 8034:2018",
    "to_standard": "IS 9283:2024",
    "relationship_type": "normative_reference",
    "evidence_ids": [
      "E-8034-NORMREF-9283"
    ],
    "verified": true,
    "notes": "Normative Reference between IS 8034:2018 and IS 9283:2024."
  },
  {
    "from_standard": "IS 8034:2018",
    "to_standard": "IS 14536:2018",
    "relationship_type": "normative_reference",
    "evidence_ids": [
      "E-8034-NORMREF-14536"
    ],
    "verified": true,
    "notes": "Normative Reference between IS 8034:2018 and IS 14536:2018."
  },
  {
    "from_standard": "IS 8034:2018",
    "to_standard": "IS 11346:2002",
    "relationship_type": "test_method",
    "evidence_ids": [
      "E-8034-NORMREF-11346"
    ],
    "verified": true,
    "notes": "Test Method between IS 8034:2018 and IS 11346:2002."
  },
  {
    "from_standard": "IS 14220:2018",
    "to_standard": "IS 14536:2018",
    "relationship_type": "related_practice",
    "evidence_ids": [
      "E-14536-LISTING-2026"
    ],
    "verified": true,
    "notes": "Related Practice between IS 14220:2018 and IS 14536:2018."
  },
  {
    "from_standard": "IS 9079:2018",
    "to_standard": "IS 11346:2002",
    "relationship_type": "test_method",
    "evidence_ids": [
      "E-11346-LISTING-MED20"
    ],
    "verified": true,
    "notes": "Test Method between IS 9079:2018 and IS 11346:2002."
  },
  {
    "from_standard": "IS 14220:2018",
    "to_standard": "IS 3043:2018",
    "relationship_type": "safety",
    "evidence_ids": [
      "E-3043-SCOPE"
    ],
    "verified": true,
    "notes": "Code of practice for earthing and electrical installation safety for openwell submersible pumpsets."
  },
  {
    "from_standard": "IS 8034:2018",
    "to_standard": "IS 12818:2010",
    "relationship_type": "companion_specification",
    "evidence_ids": [
      "E-12818-SCOPE"
    ],
    "verified": true,
    "notes": "Companion specification for uPVC screen and casing pipes used in deep borewells housing submersible pumps."
  },
  {
    "from_standard": "IS 8034:2018",
    "to_standard": "IS 3043:2018",
    "relationship_type": "safety",
    "evidence_ids": [
      "E-3043-SCOPE"
    ],
    "verified": true,
    "notes": "Code of practice for earthing and electrical installation safety for borewell submersible pumpsets."
  },
  {
    "from_standard": "IS 9079:2018",
    "to_standard": "IS 12615:2018",
    "relationship_type": "normative_reference",
    "evidence_ids": [
      "E-12615-SCOPE"
    ],
    "verified": true,
    "notes": "Normative energy efficiency specification for line-operated three-phase electric motors driving monoset pumps."
  },
  {
    "from_standard": "IS 9079:2018",
    "to_standard": "IS 996:2009",
    "relationship_type": "normative_reference",
    "evidence_ids": [
      "E-996-SCOPE"
    ],
    "verified": true,
    "notes": "Normative specification for single-phase electric motors driving domestic monoset pumps."
  },
  {
    "from_standard": "IS 9079:2018",
    "to_standard": "IS 5312-1:2004",
    "relationship_type": "companion_specification",
    "evidence_ids": [
      "E-5312-1-SCOPE"
    ],
    "verified": true,
    "notes": "Companion non-return valve specification on discharge piping of monoset pump installations."
  },
  {
    "from_standard": "IS 8472:2019",
    "to_standard": "IS 11346:2002",
    "relationship_type": "test_method",
    "evidence_ids": [
      "E-8472-SCOPE"
    ],
    "verified": true,
    "notes": "Code of acceptance for hydraulic performance testing of regenerative pumps."
  },
  {
    "from_standard": "IS 12225:2025",
    "to_standard": "IS 11346:2002",
    "relationship_type": "test_method",
    "evidence_ids": [
      "E-12225-SCOPE"
    ],
    "verified": true,
    "notes": "Code of acceptance for hydraulic performance testing of centrifugal jet pumpsets."
  },
  {
    "from_standard": "IS 1520:1980",
    "to_standard": "IS 11346:2002",
    "relationship_type": "test_method",
    "evidence_ids": [
      "E-1520-SCOPE"
    ],
    "verified": true,
    "notes": "Code of acceptance for hydraulic performance testing of horizontal centrifugal agricultural pumps."
  },
  {
    "from_standard": "IS 1710:2021",
    "to_standard": "IS 11346:2002",
    "relationship_type": "test_method",
    "evidence_ids": [
      "E-1710-SCOPE"
    ],
    "verified": true,
    "notes": "Code of acceptance for hydraulic performance testing of vertical turbine pumps."
  },
  {
    "from_standard": "IS 12615:2018",
    "to_standard": "IS/IEC 60947-4-1:2019",
    "relationship_type": "companion_specification",
    "evidence_ids": [
      "E-60947-4-1-SCOPE"
    ],
    "verified": true,
    "notes": "Companion specification for electromechanical contactors and motor-starters protecting 3-phase induction motors."
  },
  {
    "from_standard": "IS 14846:2000",
    "to_standard": "IS 778:1984",
    "relationship_type": "related_product",
    "evidence_ids": [
      "E-778-SCOPE"
    ],
    "verified": true,
    "notes": "Companion flow control valves for waterworks isolation and distribution networks."
  }
];

export const STANDARDS: CorpusStandard[] = [
  {
    "standard_id": "IS 14220:2018",
    "title": "Openwell Submersible Pumpsets",
    "scope": "Openwell submersible pumpsets for clear, cold water, including agriculture and irrigation applications described in BIS summary material.",
    "category": "pumps",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "2018"
    ],
    "provenance": "BIS Technical Committee Evidence (E-14220-SCOPE)",
    "evidence_ids": [
      "E-14220-SCOPE"
    ],
    "related_standards": [
      "IS 14536:2018",
      "IS 3043:2018"
    ],
    "keywords": [
      "openwell",
      "submersible",
      "pumpset",
      "agriculture",
      "irrigation",
      "water supply"
    ],
    "product_terms": [
      "openwell"
    ],
    "application_terms": [
      "agriculture",
      "irrigation",
      "water supply"
    ]
  },
  {
    "standard_id": "IS 8034:2018",
    "title": "Submersible Pumpsets",
    "scope": "Submersible pumpsets for clear, cold water, commonly used in boreholes/borewells/tubewells for agriculture and water supply.",
    "category": "pumps",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "2018"
    ],
    "provenance": "BIS Technical Committee Evidence (E-8034-SCOPE, E-8034-LIFECYCLE)",
    "evidence_ids": [
      "E-8034-SCOPE",
      "E-8034-LIFECYCLE"
    ],
    "related_standards": [
      "IS 11346:2002",
      "IS 12818:2010",
      "IS 14536:2018",
      "IS 3043:2018",
      "IS 9283:2024"
    ],
    "keywords": [
      "submersible",
      "pumpset",
      "borewell",
      "borehole",
      "tubewell",
      "agriculture",
      "water supply"
    ],
    "product_terms": [
      "submersible pumpset",
      "submersible pumpsets"
    ],
    "application_terms": [
      "borewell",
      "borehole",
      "tubewell",
      "agriculture",
      "water supply"
    ]
  },
  {
    "standard_id": "IS 9079:2018",
    "title": "Monoset Pumps for Clear, Cold Water for Agricultural and Water Supply",
    "scope": "Monoset pumps for clear, cold water for agricultural and water supply purposes.",
    "category": "pumps",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "2018"
    ],
    "provenance": "BIS Technical Committee Evidence (E-9079-SCOPE)",
    "evidence_ids": [
      "E-9079-SCOPE"
    ],
    "related_standards": [
      "IS 11346:2002",
      "IS 12615:2018",
      "IS 5312-1:2004",
      "IS 996:2009"
    ],
    "keywords": [
      "monoset",
      "pump",
      "clear water",
      "cold water",
      "agriculture",
      "water supply"
    ],
    "product_terms": [
      "monoset",
      "monoset pump"
    ],
    "application_terms": [
      "agriculture",
      "water supply",
      "clear water",
      "cold water"
    ]
  },
  {
    "standard_id": "IS 14536:2018",
    "title": "Selection, Installation, Operation and Maintenance of Submersible Pumpset \u2014 Code of Practice",
    "scope": "Code of practice for selection, installation, operation and maintenance of submersible pumpset, as listed in BIS committee material.",
    "category": "pumps",
    "standard_role": "CODE_OF_PRACTICE",
    "role_label": "Code of Practice",
    "versions": [
      "2018"
    ],
    "provenance": "BIS Technical Committee Evidence (E-14536-LISTING-2026)",
    "evidence_ids": [
      "E-14536-LISTING-2026"
    ],
    "related_standards": [
      "IS 14220:2018",
      "IS 8034:2018"
    ],
    "keywords": [
      "submersible",
      "pumpset",
      "selection",
      "installation",
      "operation",
      "maintenance"
    ],
    "product_terms": [],
    "application_terms": [
      "selection",
      "installation",
      "operation",
      "maintenance"
    ]
  },
  {
    "standard_id": "IS 9283:2024",
    "title": "Line Operated A.C. Motors for Submersible Pumpsets \u2014 Specification",
    "scope": "Specification for line-operated a.c. motors designed for use in submersible pumpsets. Normative reference of IS 8034:2018.",
    "category": "pumps",
    "standard_role": "RELATED_STANDARD",
    "role_label": "Related / Component Standard",
    "versions": [
      "2024"
    ],
    "provenance": "BIS Technical Committee Evidence (E-9283-LISTING-2026)",
    "evidence_ids": [
      "E-9283-LISTING-2026"
    ],
    "related_standards": [
      "IS 8034:2018"
    ],
    "keywords": [
      "motor",
      "submersible",
      "pumpset",
      "a.c. motor",
      "line operated"
    ],
    "product_terms": [
      "submersible pumpset motor",
      "motor for submersible"
    ],
    "application_terms": [
      "submersible",
      "borewell",
      "borehole",
      "tubewell"
    ]
  },
  {
    "standard_id": "IS 11346:2002",
    "title": "Tests for Agricultural and Water Supply Pumps \u2014 Code of Acceptance",
    "scope": "Code of acceptance for hydraulic performance testing of pumps used in agricultural and water supply applications. Referenced by IS 8034:2018 and IS 9079:2018.",
    "category": "pumps",
    "standard_role": "TEST_METHOD",
    "role_label": "Test Method Standard",
    "versions": [
      "2002"
    ],
    "provenance": "BIS Technical Committee Evidence (E-11346-LISTING-MED20)",
    "evidence_ids": [
      "E-11346-LISTING-MED20"
    ],
    "related_standards": [
      "IS 12225:2025",
      "IS 1520:1980",
      "IS 1710:2021",
      "IS 8034:2018",
      "IS 8472:2019",
      "IS 9079:2018"
    ],
    "keywords": [
      "test",
      "agricultural pump",
      "water supply pump",
      "hydraulic",
      "performance",
      "acceptance"
    ],
    "product_terms": [],
    "application_terms": [
      "agricultural pump",
      "water supply pump",
      "hydraulic performance"
    ]
  },
  {
    "standard_id": "IS 10572:1983",
    "title": "Methods of Sampling for Pumps",
    "scope": "Methods of sampling and criteria for conformity for pumps, used in BIS certification under Committee MED 20.",
    "category": "pumps",
    "standard_role": "TEST_METHOD",
    "role_label": "Test Method Standard",
    "versions": [
      "1983"
    ],
    "provenance": "BIS Technical Committee Evidence (E-10572-LISTING-MED20)",
    "evidence_ids": [
      "E-10572-LISTING-MED20"
    ],
    "related_standards": [],
    "keywords": [
      "sampling",
      "pump",
      "conformity",
      "inspection"
    ],
    "product_terms": [],
    "application_terms": [
      "sampling",
      "conformity",
      "inspection"
    ]
  },
  {
    "standard_id": "IS 1239:1990",
    "title": "Mild Steel Tubes, Tubulars and Other Wrought Steel Fittings \u2014 Specification (Part 1: Mild Steel Tubes)",
    "scope": "Specification for mild steel tubes (welded and seamless) for conveyance of water, gas, air and steam, classified as Class A (Light), Class B (Medium) and Class C (Heavy). Tubes may be uncoated or hot-dip galvanized (GI). Nominal bore 6 mm to 150 mm. Directly cited in the Ganga Kalyana Scheme tender for 50mm GI column pipes Class B.",
    "category": "piping",
    "standard_role": "RELATED_STANDARD",
    "role_label": "Related / Component Standard",
    "versions": [
      "1990"
    ],
    "provenance": "BIS Technical Committee Evidence (E-1239-SCOPE)",
    "evidence_ids": [
      "E-1239-SCOPE"
    ],
    "related_standards": [],
    "keywords": [
      "steel tube",
      "GI pipe",
      "galvanized",
      "mild steel",
      "column pipe",
      "water pipe",
      "Class B",
      "ISI 1239"
    ],
    "product_terms": [
      "GI pipe",
      "GI pipes",
      "galvanized pipe",
      "mild steel tube",
      "steel tube"
    ],
    "application_terms": [
      "column pipe",
      "water conveyance",
      "borewell",
      "submersible pump"
    ]
  },
  {
    "standard_id": "IS 694:2010",
    "title": "PVC Insulated Cables for Working Voltages up to and Including 1100 V",
    "scope": "Specification for PVC insulated unsheathed and sheathed cables and cords (circular and flat) with rigid and flexible conductors for rated voltages up to 1100 V. Tender cites IS 694-1990 for flat 3-core sheathed PVC submersible pump cable. IS 694 has been revised to 2010 edition.",
    "category": "electrical_cables",
    "standard_role": "RELATED_STANDARD",
    "role_label": "Related / Component Standard",
    "versions": [
      "2010"
    ],
    "provenance": "BIS Technical Committee Evidence (E-694-SCOPE)",
    "evidence_ids": [
      "E-694-SCOPE"
    ],
    "related_standards": [],
    "keywords": [
      "PVC cable",
      "PVC insulated",
      "submersible cable",
      "flat cable",
      "3 core cable",
      "pump cable",
      "IS 694"
    ],
    "product_terms": [
      "PVC insulated cable",
      "flat 3 core cable",
      "submersible pump cable"
    ],
    "application_terms": [
      "submersible pump",
      "borewell pump",
      "cable installation"
    ]
  },
  {
    "standard_id": "IS 1554:1988",
    "title": "PVC Insulated (Heavy Duty) Electric Cables (Part 1: For Working Voltages up to and Including 1100 V)",
    "scope": "Specification for PVC insulated heavy-duty electric cables (armoured and unarmoured) for working voltages up to and including 1100 V, used for electric supply and control including underground installation. Tender cites 'IS 1554/1988' for armoured LT UG cable (3.5x10 and 3.5x25 sq mm).",
    "category": "electrical_cables",
    "standard_role": "RELATED_STANDARD",
    "role_label": "Related / Component Standard",
    "versions": [
      "1988"
    ],
    "provenance": "BIS Technical Committee Evidence (E-1554-SCOPE)",
    "evidence_ids": [
      "E-1554-SCOPE"
    ],
    "related_standards": [],
    "keywords": [
      "UG cable",
      "underground cable",
      "armoured cable",
      "LT cable",
      "PVC heavy duty",
      "IS 1554"
    ],
    "product_terms": [
      "armoured cable",
      "LT UG cable",
      "underground cable"
    ],
    "application_terms": [
      "underground installation",
      "submersible pump",
      "borewell electrification"
    ]
  },
  {
    "standard_id": "IS 8472:2019",
    "title": "Pumps \u2014 Regenerative Pumps for Clear, Cold Water \u2014 Specification",
    "scope": "Specification for regenerative pumps (both self-priming and non-self-priming) for clear, cold fresh water for agricultural and domestic water supply.",
    "category": "pumps",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "2019"
    ],
    "provenance": "BIS Technical Committee Evidence (E-8472-SCOPE)",
    "evidence_ids": [
      "E-8472-SCOPE"
    ],
    "related_standards": [
      "IS 11346:2002"
    ],
    "keywords": [
      "regenerative pump",
      "self-priming pump",
      "peripheral pump",
      "water supply",
      "clear water"
    ],
    "product_terms": [
      "regenerative pump",
      "regenerative pumps",
      "self-priming pump",
      "self priming pump"
    ],
    "application_terms": [
      "clear cold water",
      "domestic water supply",
      "agricultural water supply"
    ]
  },
  {
    "standard_id": "IS 12225:2025",
    "title": "Centrifugal Jet Pumpsets for Clear, Cold Water for Agricultural and Domestic Water Supply \u2014 Specification",
    "scope": "Specification for centrifugal jet pumpsets used for clear, cold water supply from deep wells and shallow wells in domestic and agricultural settings.",
    "category": "pumps",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "1987",
      "1997",
      "2025"
    ],
    "provenance": "BIS Technical Committee Evidence (E-12225-SCOPE)",
    "evidence_ids": [
      "E-12225-SCOPE"
    ],
    "related_standards": [
      "IS 11346:2002"
    ],
    "keywords": [
      "jet pump",
      "jet pumpset",
      "centrifugal jet pump",
      "deep well pump",
      "shallow well pump"
    ],
    "product_terms": [
      "jet pump",
      "jet pumpset",
      "centrifugal jet pump"
    ],
    "application_terms": [
      "domestic water supply",
      "agricultural water supply",
      "deep well water"
    ]
  },
  {
    "standard_id": "IS 1520:1980",
    "title": "Horizontal Centrifugal Pumps for Clear, Cold, Fresh Water for Agricultural Purposes \u2014 Specification",
    "scope": "Specification for horizontal centrifugal pumps for clear, cold, fresh water intended primarily for agricultural purposes.",
    "category": "pumps",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "1980"
    ],
    "provenance": "BIS Technical Committee Evidence (E-1520-SCOPE)",
    "evidence_ids": [
      "E-1520-SCOPE"
    ],
    "related_standards": [
      "IS 11346:2002"
    ],
    "keywords": [
      "horizontal centrifugal pump",
      "centrifugal pump",
      "agricultural pump",
      "end suction pump"
    ],
    "product_terms": [
      "horizontal centrifugal pump",
      "centrifugal pump for agriculture"
    ],
    "application_terms": [
      "agricultural irrigation",
      "clear cold water",
      "farm water"
    ]
  },
  {
    "standard_id": "IS 1710:2021",
    "title": "Vertical Turbine Pumps for Clear, Cold, Fresh Water \u2014 Specification",
    "scope": "Specification for vertical turbine pumps (mixed flow or axial flow) for clear, cold water handling in deep tubewells, irrigation schemes, and municipal waterworks.",
    "category": "pumps",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "2021"
    ],
    "provenance": "BIS Technical Committee Evidence (E-1710-SCOPE)",
    "evidence_ids": [
      "E-1710-SCOPE"
    ],
    "related_standards": [
      "IS 11346:2002"
    ],
    "keywords": [
      "vertical turbine pump",
      "line shaft pump",
      "deep tubewell pump",
      "municipal waterworks"
    ],
    "product_terms": [
      "vertical turbine pump",
      "vertical turbine pumps"
    ],
    "application_terms": [
      "deep tubewell",
      "irrigation scheme",
      "waterworks",
      "lift irrigation"
    ]
  },
  {
    "standard_id": "IS 5120:1977",
    "title": "Technical Requirements for Rotodynamic Special Purpose Pumps",
    "scope": "General technical requirements, constructional features, terminology and inspection for rotodynamic special purpose pumps.",
    "category": "pumps",
    "standard_role": "RELATED_STANDARD",
    "role_label": "Related / Component Standard",
    "versions": [
      "1977"
    ],
    "provenance": "BIS Technical Committee Evidence (E-5120-SCOPE)",
    "evidence_ids": [
      "E-5120-SCOPE"
    ],
    "related_standards": [],
    "keywords": [
      "rotodynamic pump",
      "pump technical requirements",
      "special purpose pump",
      "inspection"
    ],
    "product_terms": [
      "rotodynamic pump",
      "special purpose pump"
    ],
    "application_terms": [
      "technical requirements",
      "pump inspection",
      "pump construction"
    ]
  },
  {
    "standard_id": "IS 12615:2018",
    "title": "Line Operated Three Phase A.C. Motors (IE Code) \u2014 Energy Efficiency Classes and Performance Specification",
    "scope": "Specification defining energy efficiency classes (IE2, IE3, IE4) and performance requirements for line-operated three-phase induction motors from 0.12 kW to 1000 kW.",
    "category": "motors",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "2018"
    ],
    "provenance": "BIS Technical Committee Evidence (E-12615-SCOPE)",
    "evidence_ids": [
      "E-12615-SCOPE"
    ],
    "related_standards": [
      "IS 9079:2018",
      "IS/IEC 60947-4-1:2019"
    ],
    "keywords": [
      "three phase motor",
      "induction motor",
      "IE2",
      "IE3",
      "IE4",
      "energy efficient",
      "energy efficient motor",
      "AC motor",
      "line operated"
    ],
    "product_terms": [
      "three phase induction motor",
      "three phase motor",
      "line operated three phase induction motor",
      "IE2 motor",
      "IE3 motor",
      "IE4 motor",
      "energy efficient motor",
      "energy efficient induction motor"
    ],
    "application_terms": [
      "pump drive",
      "industrial pump drive",
      "pump driver",
      "industrial motor",
      "electrical drive",
      "pump set"
    ]
  },
  {
    "standard_id": "IS 996:2009",
    "title": "Single-Phase Small A.C. Electric Motors for General Purpose \u2014 Specification",
    "scope": "Specification for single-phase small a.c. electric motors used in domestic appliances, small pumps, and industrial tools.",
    "category": "motors",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "2009"
    ],
    "provenance": "BIS Technical Committee Evidence (E-996-SCOPE)",
    "evidence_ids": [
      "E-996-SCOPE"
    ],
    "related_standards": [
      "IS 9079:2018"
    ],
    "keywords": [
      "single phase motor",
      "fractional HP motor",
      "small AC motor",
      "domestic motor"
    ],
    "product_terms": [
      "single phase motor",
      "single phase electric motor",
      "small AC motor"
    ],
    "application_terms": [
      "monobloc pump",
      "domestic pump",
      "water supply pump"
    ]
  },
  {
    "standard_id": "IS/IEC 60947-4-1:2019",
    "title": "Low-Voltage Switchgear and Controlgear \u2014 Part 4-1: Contactors and Motor-Starters \u2014 Electromechanical Contactors and Motor-Starters",
    "scope": "Specification for low-voltage electromechanical contactors and motor-starters, including direct-on-line (DOL) and star-delta starters used for motor protection in pumping systems.",
    "category": "switchgear",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "2019"
    ],
    "provenance": "BIS Technical Committee Evidence (E-60947-4-1-SCOPE)",
    "evidence_ids": [
      "E-60947-4-1-SCOPE"
    ],
    "related_standards": [
      "IS 12615:2018"
    ],
    "keywords": [
      "motor starter",
      "contactor",
      "DOL starter",
      "star delta starter",
      "pump control panel",
      "switchgear"
    ],
    "product_terms": [
      "motor starter",
      "DOL starter",
      "star delta starter",
      "motor control panel",
      "pump starter"
    ],
    "application_terms": [
      "pump control",
      "motor protection",
      "electrical panel"
    ]
  },
  {
    "standard_id": "IS 4984:2016",
    "title": "Polyethylene (HDPE) Pipes for Water Supply \u2014 Specification",
    "scope": "Specification for high density polyethylene (HDPE) pipes (PE 63, PE 80, PE 100) intended for conveyance of potable water for domestic and agricultural water supply.",
    "category": "piping",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "2016"
    ],
    "provenance": "BIS Technical Committee Evidence (E-4984-SCOPE)",
    "evidence_ids": [
      "E-4984-SCOPE"
    ],
    "related_standards": [],
    "keywords": [
      "HDPE pipe",
      "polyethylene pipe",
      "PE 100",
      "PE 80",
      "water supply pipe",
      "potable water pipe"
    ],
    "product_terms": [
      "HDPE pipe",
      "HDPE pipes",
      "polyethylene pipe",
      "PE pipe"
    ],
    "application_terms": [
      "potable water supply",
      "irrigation water",
      "water distribution network"
    ]
  },
  {
    "standard_id": "IS 4985:2021",
    "title": "Unplasticized Polyvinyl Chloride (uPVC) Pipes for Potable Water Supplies \u2014 Specification",
    "scope": "Specification for unplasticized polyvinyl chloride (uPVC) pipes for potable water supplies, irrigation, and plumbing installations.",
    "category": "piping",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "2021"
    ],
    "provenance": "BIS Technical Committee Evidence (E-4985-SCOPE)",
    "evidence_ids": [
      "E-4985-SCOPE"
    ],
    "related_standards": [],
    "keywords": [
      "uPVC pipe",
      "PVC pipe",
      "potable water",
      "irrigation pipe",
      "plumbing pipe"
    ],
    "product_terms": [
      "uPVC pipe",
      "uPVC pipes",
      "unplasticized PVC pipe"
    ],
    "application_terms": [
      "potable water supply",
      "agricultural irrigation",
      "water supply network"
    ]
  },
  {
    "standard_id": "IS 12818:2010",
    "title": "Unplasticized PVC (uPVC) Screen and Casing Pipes for Borewells / Tubewells \u2014 Specification",
    "scope": "Specification for unplasticized PVC screen and casing pipes with ribbed or plain surfaces for borewells and tubewells.",
    "category": "piping",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "2010"
    ],
    "provenance": "BIS Technical Committee Evidence (E-12818-SCOPE)",
    "evidence_ids": [
      "E-12818-SCOPE"
    ],
    "related_standards": [
      "IS 8034:2018"
    ],
    "keywords": [
      "casing pipe",
      "screen pipe",
      "uPVC casing",
      "borewell casing",
      "tubewell pipe"
    ],
    "product_terms": [
      "casing pipe",
      "uPVC casing pipe",
      "borewell casing pipe",
      "screen pipe"
    ],
    "application_terms": [
      "borewell",
      "tubewell",
      "groundwater extraction"
    ]
  },
  {
    "standard_id": "IS 8329:2020",
    "title": "Centrifugally Cast (Spun) Ductile Iron Pressure Pipes for Water, Gas and Sewage \u2014 Specification",
    "scope": "Specification for centrifugally cast (spun) ductile iron pressure pipes with socket and spigot ends for water, gas and sewage pipelines.",
    "category": "piping",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "2020"
    ],
    "provenance": "BIS Technical Committee Evidence (E-8329-SCOPE)",
    "evidence_ids": [
      "E-8329-SCOPE"
    ],
    "related_standards": [],
    "keywords": [
      "ductile iron pipe",
      "DI pipe",
      "spun iron pipe",
      "water transmission",
      "pumping main"
    ],
    "product_terms": [
      "ductile iron pipe",
      "DI pipe",
      "DI pipes",
      "ductile iron pressure pipe"
    ],
    "application_terms": [
      "water supply main",
      "pumping main",
      "rising main",
      "water transmission"
    ]
  },
  {
    "standard_id": "IS 778:1984",
    "title": "Specification for Copper Alloy Gate, Globe and Check Valves for Waterworks Purposes",
    "scope": "Specification for copper alloy (gunmetal and brass) gate, globe and check valves for waterworks purposes suitable for maximum working pressures up to 1.6 MPa.",
    "category": "valves",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "1984"
    ],
    "provenance": "BIS Technical Committee Evidence (E-778-SCOPE)",
    "evidence_ids": [
      "E-778-SCOPE"
    ],
    "related_standards": [
      "IS 14846:2000"
    ],
    "keywords": [
      "gunmetal valve",
      "brass valve",
      "gate valve",
      "globe valve",
      "check valve",
      "waterworks valve"
    ],
    "product_terms": [
      "gunmetal valve",
      "copper alloy valve",
      "brass gate valve",
      "brass check valve"
    ],
    "application_terms": [
      "waterworks",
      "potable water distribution",
      "pump plumbing"
    ]
  },
  {
    "standard_id": "IS 5312-1:2004",
    "title": "Swing Check Type Reflux (Non-Return) Valves for Waterworks Purposes \u2014 Part 1: Single Door Pattern",
    "scope": "Specification for swing check type reflux (non-return) valves of single door pattern for waterworks purposes on rising mains and pump discharge lines.",
    "category": "valves",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "2004"
    ],
    "provenance": "BIS Technical Committee Evidence (E-5312-1-SCOPE)",
    "evidence_ids": [
      "E-5312-1-SCOPE"
    ],
    "related_standards": [
      "IS 9079:2018"
    ],
    "keywords": [
      "non return valve",
      "NRV",
      "reflux valve",
      "check valve",
      "swing check valve",
      "pump discharge valve"
    ],
    "product_terms": [
      "non return valve",
      "reflux valve",
      "swing check valve",
      "NRV valve"
    ],
    "application_terms": [
      "pump discharge line",
      "waterworks",
      "rising main"
    ]
  },
  {
    "standard_id": "IS 14846:2000",
    "title": "Sluice Valves for Waterworks Purposes (50 to 1200 mm Size) \u2014 Specification",
    "scope": "Specification for cast iron sluice valves (size 50 mm to 1200 mm) with inside screw non-rising spindle for waterworks and flow isolation.",
    "category": "valves",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "2000"
    ],
    "provenance": "BIS Technical Committee Evidence (E-14846-SCOPE)",
    "evidence_ids": [
      "E-14846-SCOPE"
    ],
    "related_standards": [
      "IS 778:1984"
    ],
    "keywords": [
      "sluice valve",
      "gate valve 100mm",
      "isolation valve",
      "cast iron sluice valve",
      "waterworks valve"
    ],
    "product_terms": [
      "sluice valve",
      "cast iron sluice valve",
      "waterworks sluice valve"
    ],
    "application_terms": [
      "waterworks",
      "pipeline isolation",
      "water distribution network"
    ]
  },
  {
    "standard_id": "IS 779:1994",
    "title": "Water Meters (Domestic Type) \u2014 Specification",
    "scope": "Specification for inferential and semi-positive volumetric domestic water meters (size 15 mm to 50 mm) for cold potable water measurement.",
    "category": "instrumentation",
    "standard_role": "PRIMARY_PRODUCT_STANDARD",
    "role_label": "Primary Product Standard",
    "versions": [
      "1994"
    ],
    "provenance": "BIS Technical Committee Evidence (E-779-SCOPE)",
    "evidence_ids": [
      "E-779-SCOPE"
    ],
    "related_standards": [],
    "keywords": [
      "water meter",
      "domestic water meter",
      "flow meter",
      "water measurement"
    ],
    "product_terms": [
      "water meter",
      "domestic water meter",
      "cold water meter"
    ],
    "application_terms": [
      "potable water measurement",
      "domestic water billing",
      "water flow measurement"
    ]
  },
  {
    "standard_id": "IS 3043:2018",
    "title": "Code of Practice for Earthing",
    "scope": "Code of practice for design, installation and maintenance of earthing systems in electrical installations including pumpsets, motor control centers and distribution systems.",
    "category": "safety",
    "standard_role": "CODE_OF_PRACTICE",
    "role_label": "Code of Practice",
    "versions": [
      "2018"
    ],
    "provenance": "BIS Technical Committee Evidence (E-3043-SCOPE)",
    "evidence_ids": [
      "E-3043-SCOPE"
    ],
    "related_standards": [
      "IS 14220:2018",
      "IS 8034:2018"
    ],
    "keywords": [
      "earthing",
      "earthing code",
      "electrical grounding",
      "pump earthing",
      "substation earthing"
    ],
    "product_terms": [],
    "application_terms": [
      "electrical earthing",
      "earthing installation",
      "pump safety",
      "motor grounding"
    ]
  }
];

export const EVALUATION_CASES: EvaluationCase[] = [
  {
    "id": "C01-openwell-primary",
    "query": "openwell submersible pumpset for agricultural irrigation",
    "expected_contains": [
      "IS 14220:2018"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "Canonical pump benchmark. Product term 'openwell' discriminates IS 14220:2018 as sole strong primary."
  },
  {
    "id": "C02-borewell-submersible",
    "query": "submersible pumpsets for a borewell supplying agricultural water",
    "expected_contains": [
      "IS 8034:2018"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "borewell + submersible pumpsets discriminates IS 8034:2018."
  },
  {
    "id": "C03-monoset-primary",
    "query": "monoset pump for clear cold water for agriculture",
    "expected_contains": [
      "IS 9079:2018"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "monoset product term uniquely identifies IS 9079:2018."
  },
  {
    "id": "C04-hdpe-pipe",
    "query": "HDPE pipe PE 100 for potable water supply distribution network",
    "expected_contains": [
      "IS 4984:2016"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "HDPE pipe product term uniquely identifies IS 4984:2016."
  },
  {
    "id": "C05-regenerative-pump",
    "query": "self-priming regenerative pump for domestic water supply",
    "expected_contains": [
      "IS 8472:2019"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "self-priming regenerative pump uniquely matches IS 8472:2019."
  },
  {
    "id": "C06-three-phase-motor",
    "query": "line operated three phase induction motor IE3 energy efficient for industrial pump drive",
    "expected_contains": [
      "IS 12615:2018"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "three phase induction motor IE3 uniquely identifies IS 12615:2018."
  },
  {
    "id": "C07-water-meter",
    "query": "domestic water meter 15mm cold potable water measurement",
    "expected_contains": [
      "IS 779:1994"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "domestic water meter identifies IS 779:1994."
  },
  {
    "id": "C08-sluice-valve",
    "query": "cast iron sluice valve 100mm for waterworks pipeline isolation",
    "expected_contains": [
      "IS 14846:2000"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "cast iron sluice valve identifies IS 14846:2000."
  },
  {
    "id": "C09-is-lookup-14220",
    "query": "procurement as per IS 14220 openwell submersible pumpset",
    "expected_contains": [
      "IS 14220:2018"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "Explicit IS number reference must be retrieved via exact_id retrieval path."
  },
  {
    "id": "C10-is-lookup-8034",
    "query": "specification compliance for IS 8034 submersible pumpsets",
    "expected_contains": [
      "IS 8034:2018"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "Explicit IS 8034 reference via exact_id path."
  },
  {
    "id": "C11-jet-pump-product-variation",
    "query": "centrifugal jet pump for domestic deep well water supply",
    "expected_contains": [
      "IS 12225:2025"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "jet pump product term maps to IS 12225:2025 centrifugal jet pumpsets."
  },
  {
    "id": "C12-horizontal-centrifugal-variation",
    "query": "horizontal centrifugal pump for agricultural irrigation clear water",
    "expected_contains": [
      "IS 1520:1980"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "horizontal centrifugal pump for agriculture uniquely maps to IS 1520:1980."
  },
  {
    "id": "C13-vertical-turbine-variation",
    "query": "vertical turbine pump for deep tubewell lift irrigation scheme",
    "expected_contains": [
      "IS 1710:2021"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "vertical turbine pump term maps to IS 1710:2021."
  },
  {
    "id": "C14-upvc-pipe-variation",
    "query": "uPVC pipe for potable water supply agricultural irrigation",
    "expected_contains": [
      "IS 4985:2021"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "uPVC pipe term maps to IS 4985:2021."
  },
  {
    "id": "C15-casing-pipe-variation",
    "query": "uPVC casing pipe and screen pipe for borewell tubewell groundwater extraction",
    "expected_contains": [
      "IS 12818:2010"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "casing pipe / screen pipe product term discriminates IS 12818:2010."
  },
  {
    "id": "C16-ductile-iron-pipe-variation",
    "query": "ductile iron DI pipe for water supply main pumping main",
    "expected_contains": [
      "IS 8329:2020"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "ductile iron / DI pipe maps to IS 8329:2020."
  },
  {
    "id": "C17-openwell-vs-borewell-discriminate",
    "query": "openwell submersible pumpset for agricultural irrigation borewell NOT borewell",
    "expected_contains": [
      "IS 14220:2018"
    ],
    "expected_decision": null,
    "notes": "openwell term should dominate over incidental borewell mention. IS 8034 must NOT be the sole result."
  },
  {
    "id": "C18-monoset-vs-submersible-discriminate",
    "query": "monoset pump centrifugal clear cold water",
    "expected_contains": [
      "IS 9079:2018"
    ],
    "expected_decision": null,
    "notes": "monoset product term must discriminate IS 9079:2018; IS 8034 should not dominate."
  },
  {
    "id": "C19-regen-not-submersible",
    "query": "regenerative pump for domestic water supply not for borewell not submersible",
    "expected_contains": [
      "IS 8472:2019"
    ],
    "expected_decision": null,
    "notes": "Self-priming regenerative pump excludes borewell submersible standards."
  },
  {
    "id": "C20-motor-not-submersible",
    "query": "three phase induction motor for pump drive not submersible motor",
    "expected_contains": [
      "IS 12615:2018"
    ],
    "expected_decision": null,
    "notes": "IS 12615 covers line-operated motors; IS 9283 (submersible motor) should be excluded as primary."
  },
  {
    "id": "C21-multi-req-borewell-full-package",
    "query": "submersible pumpset for borewell IS 8034 with GI column pipe IS 1239 and submersible cable IS 694",
    "expected_contains": [
      "IS 8034:2018",
      "IS 1239:1990",
      "IS 694:2010"
    ],
    "expected_decision": null,
    "notes": "Multi-standard tender. REVIEW expected if multiple strong candidates; all three must be retrieved. Decision is don't-care (REVIEW acceptable)."
  },
  {
    "id": "C22-multi-req-pump-and-valve",
    "query": "submersible borewell pumpset with non-return valve on discharge and sluice valve for isolation",
    "expected_contains": [
      "IS 8034:2018",
      "IS 5312-1:2004",
      "IS 14846:2000"
    ],
    "expected_decision": null,
    "notes": "Multi-standard query. Pump, NRV and sluice valve must all appear in candidates or graph expansion."
  },
  {
    "id": "C23-multi-req-motor-starter",
    "query": "three phase induction motor IE2 with DOL motor starter for pump control panel",
    "expected_contains": [
      "IS 12615:2018",
      "IS/IEC 60947-4-1:2019"
    ],
    "expected_decision": null,
    "notes": "Motor + starter multi-requirement. Both must be retrievable."
  },
  {
    "id": "C24-lifecycle-revision-under-print",
    "query": "openwell submersible pumpset for agricultural irrigation",
    "expected_contains": [
      "IS 14220:2018"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "revision_under_print lifecycle event must not prevent RECOMMEND; standard remains supported."
  },
  {
    "id": "C25-related-standard-discovery",
    "query": "submersible pumpsets for a borewell supplying agricultural water",
    "expected_contains": [
      "IS 9283:2024",
      "IS 11346:2002",
      "IS 14536:2018"
    ],
    "expected_decision": null,
    "notes": "Graph expansion from IS 8034:2018 at hop=1 must surface normative references: IS 9283 (motor), IS 11346 (test), IS 14536 (CoP)."
  },
  {
    "id": "C26-out-of-corpus-robotic-mining",
    "query": "advanced underwater robotic mining vehicle with hydraulic manipulators",
    "expected_contains": [],
    "expected_decision": "OUT_OF_CORPUS",
    "notes": "SAFETY: completely outside pump corpus. Must return OUT_OF_CORPUS, not a false RECOMMEND."
  },
  {
    "id": "C27-out-of-corpus-pharmaceutical",
    "query": "sterile pharmaceutical tablet coating machine GMP compliance",
    "expected_contains": [],
    "expected_decision": "OUT_OF_CORPUS",
    "notes": "SAFETY: pharmaceutical domain entirely outside corpus."
  },
  {
    "id": "C28-out-of-corpus-hvac",
    "query": "HVAC chiller unit refrigerant compressor for commercial building cooling",
    "expected_contains": [],
    "expected_decision": "OUT_OF_CORPUS",
    "notes": "SAFETY: HVAC/refrigeration domain not in corpus. OUT_OF_CORPUS required."
  },
  {
    "id": "C29-abstain-generic-pump",
    "query": "submersible pump for water supply",
    "expected_contains": [
      "IS 8034:2018"
    ],
    "expected_decision": null,
    "notes": "Generic submersible without borewell/openwell qualifier. Honest outcomes: ABSTAIN or REVIEW. OUT_OF_CORPUS is a safety failure."
  },
  {
    "id": "C30-cert-qco-8034",
    "query": "submersible pumpsets for a borewell supplying agricultural water with mandatory QCO ISI mark compliance",
    "expected_contains": [
      "IS 8034:2018"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "QCO proposed but unverified; cert must be not_verified_in_prototype_corpus without blocking RECOMMEND."
  },
  {
    "id": "C31-cert-qco-14220",
    "query": "openwell submersible pumpset with ISI mark BIS certification mandatory",
    "expected_contains": [
      "IS 14220:2018"
    ],
    "expected_decision": "RECOMMEND",
    "notes": "QCO proposed for IS 14220 but unverified; must not block RECOMMEND."
  },
  {
    "id": "C32-adversarial-empty-query",
    "query": "pump",
    "expected_contains": [],
    "expected_decision": null,
    "notes": "SAFETY: single-word query. Must not produce RECOMMEND. ABSTAIN or OUT_OF_CORPUS acceptable."
  },
  {
    "id": "C33-adversarial-unrelated-gibberish",
    "query": "xyzzy frobnicator quantum entanglement flux capacitor",
    "expected_contains": [],
    "expected_decision": "OUT_OF_CORPUS",
    "notes": "SAFETY: gibberish input. Must return OUT_OF_CORPUS, not hallucinate a standard."
  },
  {
    "id": "C34-adversarial-old-edition-citation",
    "query": "procurement of submersible pumpsets as per IS 8034:2002 for borewell",
    "expected_contains": [
      "IS 8034:2018"
    ],
    "expected_decision": null,
    "notes": "Tender cites withdrawn 2002 edition. Engine should retrieve IS 8034:2018; decision may be REVIEW due to edition_mismatch gap. RECOMMEND on the old edition is a failure."
  },
  {
    "id": "C35-adversarial-sewage-pump-exclusion",
    "query": "sewage pump for wastewater treatment plant effluent handling",
    "expected_contains": [],
    "expected_decision": null,
    "notes": "SAFETY: sewage/effluent pumps are excluded from all corpus product_terms. Engine correctly produces ABSTAIN (candidates found but none defensible) \u2014 both ABSTAIN and OUT_OF_CORPUS are safe. RECOMMEND is the only forbidden outcome."
  }
];
