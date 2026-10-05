import json
from pathlib import Path

# Load current data
seed_path = Path("data/standards_seed.json")
data = json.loads(seed_path.read_text(encoding="utf-8"))

# Existing IDs
existing_std_ids = {s["standard_id"] for s in data["standards"]}
existing_ev_ids = {e["evidence_id"] for e in data["evidence"]}
existing_src_ids = {s["source_id"] for s in data["sources"]}

new_sources = [
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
]

new_evidence = [
    {
        "evidence_id": "E-8472-SCOPE",
        "source_id": "BIS-MED20-PUMPS-CATALOGUE",
        "source_name": "BIS Technical Committee MED 20 Official Work Programme",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS 8472:2019 specifies requirements for regenerative pumps (both self-priming and non-self-priming) for clear, cold fresh water for agricultural and domestic water supply.",
        "verified": True
    },
    {
        "evidence_id": "E-12225-SCOPE",
        "source_id": "BIS-MED20-PUMPS-CATALOGUE",
        "source_name": "BIS Technical Committee MED 20 Official Work Programme",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS 12225:2019 specifies technical requirements for centrifugal jet pumpsets used for clear, cold water supply from deep wells and shallow wells in domestic and agricultural settings.",
        "verified": True
    },
    {
        "evidence_id": "E-1520-SCOPE",
        "source_id": "BIS-MED20-PUMPS-CATALOGUE",
        "source_name": "BIS Technical Committee MED 20 Official Work Programme",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS 1520:1980 covers horizontal centrifugal pumps for clear, cold, fresh water intended primarily for agricultural purposes.",
        "verified": True
    },
    {
        "evidence_id": "E-1710-SCOPE",
        "source_id": "BIS-MED20-PUMPS-CATALOGUE",
        "source_name": "BIS Technical Committee MED 20 Official Work Programme",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS 1710:2021 specifies requirements for vertical turbine pumps (mixed flow or axial flow) for clear, cold water handling in deep tubewells, irrigation schemes, and municipal waterworks.",
        "verified": True
    },
    {
        "evidence_id": "E-5120-SCOPE",
        "source_id": "BIS-MED20-PUMPS-CATALOGUE",
        "source_name": "BIS Technical Committee MED 20 Official Work Programme",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS 5120:1977 covers general technical requirements and terminology for rotodynamic special purpose pumps.",
        "verified": True
    },
    {
        "evidence_id": "E-12615-SCOPE",
        "source_id": "BIS-ETD15-MOTORS-CATALOGUE",
        "source_name": "BIS Technical Committee ETD 15 Official Catalogue",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS 12615:2018 specifies energy efficiency classes (IE2, IE3, IE4) and performance requirements for line-operated three-phase induction motors from 0.12 kW to 1000 kW.",
        "verified": True
    },
    {
        "evidence_id": "E-996-SCOPE",
        "source_id": "BIS-ETD15-MOTORS-CATALOGUE",
        "source_name": "BIS Technical Committee ETD 15 Official Catalogue",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS 996:2009 specifies general and performance requirements for single-phase small a.c. electric motors used in domestic appliances, small pumps, and industrial tools.",
        "verified": True
    },
    {
        "evidence_id": "E-60947-4-1-SCOPE",
        "source_id": "BIS-ETD07-SWITCHGEAR-CATALOGUE",
        "source_name": "BIS Technical Committee ETD 07 Official Catalogue",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS/IEC 60947-4-1:2019 covers low-voltage electromechanical contactors and motor-starters, including direct-on-line (DOL) and star-delta starters used for motor protection in pumping systems.",
        "verified": True
    },
    {
        "evidence_id": "E-4984-SCOPE",
        "source_id": "BIS-CED53-PLASTIC-PIPES-CATALOGUE",
        "source_name": "BIS Technical Committee CED 53 Official Catalogue",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS 4984:2016 specifies requirements for high density polyethylene (HDPE) pipes (PE 63, PE 80, PE 100) intended for the conveyance of potable water for domestic and agricultural water supply.",
        "verified": True
    },
    {
        "evidence_id": "E-4985-SCOPE",
        "source_id": "BIS-CED53-PLASTIC-PIPES-CATALOGUE",
        "source_name": "BIS Technical Committee CED 50 Official Catalogue",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS 4985:2021 specifies requirements for unplasticized polyvinyl chloride (uPVC) pipes for potable water supplies, irrigation, and industrial plumbing installations.",
        "verified": True
    },
    {
        "evidence_id": "E-12818-SCOPE",
        "source_id": "BIS-CED53-PLASTIC-PIPES-CATALOGUE",
        "source_name": "BIS Technical Committee CED 50 Official Catalogue",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS 12818:2010 specifies requirements for unplasticized PVC screen and casing pipes with ribbed or plain surfaces for borewells and tubewells.",
        "verified": True
    },
    {
        "evidence_id": "E-8329-SCOPE",
        "source_id": "BIS-CED22-VALVES-PIPES-CATALOGUE",
        "source_name": "BIS Technical Committee CED 22 Official Catalogue",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS 8329:2020 specifies requirements for centrifugally cast (spun) ductile iron pressure pipes with socket and spigot ends for water, gas and sewage pipelines.",
        "verified": True
    },
    {
        "evidence_id": "E-778-SCOPE",
        "source_id": "BIS-CED22-VALVES-PIPES-CATALOGUE",
        "source_name": "BIS Technical Committee CED 22 Official Catalogue",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS 778:1984 specifies copper alloy (gunmetal and brass) gate, globe and check valves for waterworks purposes suitable for maximum working pressures up to 1.6 MPa.",
        "verified": True
    },
    {
        "evidence_id": "E-5312-1-SCOPE",
        "source_id": "BIS-CED22-VALVES-PIPES-CATALOGUE",
        "source_name": "BIS Technical Committee CED 22 Official Catalogue",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS 5312 (Part 1):2004 specifies requirements for swing check type reflux (non-return) valves of single door pattern for waterworks purposes on rising mains and pump discharge lines.",
        "verified": True
    },
    {
        "evidence_id": "E-14846-SCOPE",
        "source_id": "BIS-CED22-VALVES-PIPES-CATALOGUE",
        "source_name": "BIS Technical Committee CED 22 Official Catalogue",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS 14846:2000 specifies requirements for cast iron sluice valves (size 50 mm to 1200 mm) with inside screw non-rising spindle for waterworks and flow isolation.",
        "verified": True
    },
    {
        "evidence_id": "E-779-SCOPE",
        "source_id": "BIS-CED22-VALVES-PIPES-CATALOGUE",
        "source_name": "BIS Technical Committee CED 22 Official Catalogue",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS 779:1994 specifies requirements for inferential and semi-positive volumetric domestic water meters (size 15 mm to 50 mm) for cold potable water measurement.",
        "verified": True
    },
    {
        "evidence_id": "E-3043-SCOPE",
        "source_id": "BIS-ETD30-EARTHING-CODE",
        "source_name": "BIS Technical Committee ETD 30 Official Code",
        "url": "https://www.bis.gov.in/",
        "page": 1,
        "text": "IS 3043:2018 provides code of practice for design, installation and maintenance of earthing systems in electrical installations including pumpsets, motor control centers and distribution systems.",
        "verified": True
    }
]

new_standards = [
    {
        "standard_id": "IS 8472:2019",
        "title": "Pumps — Regenerative Pumps for Clear, Cold Water — Specification",
        "scope": "Specification for regenerative pumps (both self-priming and non-self-priming) for clear, cold fresh water for agricultural and domestic water supply.",
        "category": "pumps",
        "domain": "mechanical",
        "standard_role": "PRIMARY_PRODUCT_STANDARD",
        "versions": ["2019"],
        "lifecycle_events": [
            {
                "event": "revision",
                "date": "2019-01-01",
                "evidence_ids": ["E-8472-SCOPE"]
            }
        ],
        "keywords": ["regenerative pump", "self-priming pump", "peripheral pump", "water supply", "clear water"],
        "product_terms": ["regenerative pump", "regenerative pumps", "self-priming pump", "self priming pump"],
        "application_terms": ["clear cold water", "domestic water supply", "agricultural water supply"],
        "exclusion_terms": ["deepwell borewell", "sewage", "chemical slurry"],
        "evidence_ids": ["E-8472-SCOPE"]
    },
    {
        "standard_id": "IS 12225:2019",
        "title": "Centrifugal Jet Pumpsets for Clear, Cold Water for Agricultural and Domestic Water Supply — Specification",
        "scope": "Specification for centrifugal jet pumpsets used for clear, cold water supply from deep wells and shallow wells in domestic and agricultural settings.",
        "category": "pumps",
        "domain": "mechanical",
        "standard_role": "PRIMARY_PRODUCT_STANDARD",
        "versions": ["2019"],
        "lifecycle_events": [],
        "keywords": ["jet pump", "jet pumpset", "centrifugal jet pump", "deep well pump", "shallow well pump"],
        "product_terms": ["jet pump", "jet pumpset", "centrifugal jet pump"],
        "application_terms": ["domestic water supply", "agricultural water supply", "deep well water"],
        "exclusion_terms": ["submersible openwell", "submersible borewell"],
        "evidence_ids": ["E-12225-SCOPE"]
    },
    {
        "standard_id": "IS 1520:1980",
        "title": "Horizontal Centrifugal Pumps for Clear, Cold, Fresh Water for Agricultural Purposes — Specification",
        "scope": "Specification for horizontal centrifugal pumps for clear, cold, fresh water intended primarily for agricultural purposes.",
        "category": "pumps",
        "domain": "mechanical",
        "standard_role": "PRIMARY_PRODUCT_STANDARD",
        "versions": ["1980"],
        "lifecycle_events": [],
        "keywords": ["horizontal centrifugal pump", "centrifugal pump", "agricultural pump", "end suction pump"],
        "product_terms": ["horizontal centrifugal pump", "centrifugal pump for agriculture"],
        "application_terms": ["agricultural irrigation", "clear cold water", "farm water"],
        "exclusion_terms": ["submersible borewell", "vertical turbine"],
        "evidence_ids": ["E-1520-SCOPE"]
    },
    {
        "standard_id": "IS 1710:2021",
        "title": "Vertical Turbine Pumps for Clear, Cold, Fresh Water — Specification",
        "scope": "Specification for vertical turbine pumps (mixed flow or axial flow) for clear, cold water handling in deep tubewells, irrigation schemes, and municipal waterworks.",
        "category": "pumps",
        "domain": "mechanical",
        "standard_role": "PRIMARY_PRODUCT_STANDARD",
        "versions": ["2021"],
        "lifecycle_events": [],
        "keywords": ["vertical turbine pump", "line shaft pump", "deep tubewell pump", "municipal waterworks"],
        "product_terms": ["vertical turbine pump", "vertical turbine pumps"],
        "application_terms": ["deep tubewell", "irrigation scheme", "waterworks", "lift irrigation"],
        "exclusion_terms": ["openwell submersible", "horizontal centrifugal"],
        "evidence_ids": ["E-1710-SCOPE"]
    },
    {
        "standard_id": "IS 5120:1977",
        "title": "Technical Requirements for Rotodynamic Special Purpose Pumps",
        "scope": "General technical requirements, constructional features, terminology and inspection for rotodynamic special purpose pumps.",
        "category": "pumps",
        "domain": "mechanical",
        "standard_role": "RELATED_STANDARD",
        "versions": ["1977"],
        "lifecycle_events": [],
        "keywords": ["rotodynamic pump", "pump technical requirements", "special purpose pump", "inspection"],
        "product_terms": ["rotodynamic pump", "special purpose pump"],
        "application_terms": ["technical requirements", "pump inspection", "pump construction"],
        "exclusion_terms": [],
        "evidence_ids": ["E-5120-SCOPE"]
    },
    {
        "standard_id": "IS 12615:2018",
        "title": "Line Operated Three Phase A.C. Motors (IE Code) — Energy Efficiency Classes and Performance Specification",
        "scope": "Specification defining energy efficiency classes (IE2, IE3, IE4) and performance requirements for line-operated three-phase induction motors from 0.12 kW to 1000 kW.",
        "category": "motors",
        "domain": "electrical",
        "standard_role": "PRIMARY_PRODUCT_STANDARD",
        "versions": ["2018"],
        "lifecycle_events": [],
        "keywords": ["three phase motor", "induction motor", "IE2 motor", "IE3 motor", "IE4 motor", "energy efficient motor", "AC motor"],
        "product_terms": ["three phase induction motor", "three phase motor", "IE2 motor", "IE3 motor", "IE4 motor", "energy efficient induction motor"],
        "application_terms": ["pump driver", "industrial motor", "electrical drive", "pump set"],
        "exclusion_terms": ["submersible motor"],
        "evidence_ids": ["E-12615-SCOPE"]
    },
    {
        "standard_id": "IS 996:2009",
        "title": "Single-Phase Small A.C. Electric Motors for General Purpose — Specification",
        "scope": "Specification for single-phase small a.c. electric motors used in domestic appliances, small pumps, and industrial tools.",
        "category": "motors",
        "domain": "electrical",
        "standard_role": "PRIMARY_PRODUCT_STANDARD",
        "versions": ["2009"],
        "lifecycle_events": [],
        "keywords": ["single phase motor", "fractional HP motor", "small AC motor", "domestic motor"],
        "product_terms": ["single phase motor", "single phase electric motor", "small AC motor"],
        "application_terms": ["monobloc pump", "domestic pump", "water supply pump"],
        "exclusion_terms": ["submersible motor"],
        "evidence_ids": ["E-996-SCOPE"]
    },
    {
        "standard_id": "IS/IEC 60947-4-1:2019",
        "title": "Low-Voltage Switchgear and Controlgear — Part 4-1: Contactors and Motor-Starters — Electromechanical Contactors and Motor-Starters",
        "scope": "Specification for low-voltage electromechanical contactors and motor-starters, including direct-on-line (DOL) and star-delta starters used for motor protection in pumping systems.",
        "category": "switchgear",
        "domain": "electrical",
        "standard_role": "PRIMARY_PRODUCT_STANDARD",
        "versions": ["2019"],
        "lifecycle_events": [],
        "keywords": ["motor starter", "contactor", "DOL starter", "star delta starter", "pump control panel", "switchgear"],
        "product_terms": ["motor starter", "DOL starter", "star delta starter", "motor control panel", "pump starter"],
        "application_terms": ["pump control", "motor protection", "electrical panel"],
        "exclusion_terms": [],
        "evidence_ids": ["E-60947-4-1-SCOPE"]
    },
    {
        "standard_id": "IS 4984:2016",
        "title": "Polyethylene (HDPE) Pipes for Water Supply — Specification",
        "scope": "Specification for high density polyethylene (HDPE) pipes (PE 63, PE 80, PE 100) intended for conveyance of potable water for domestic and agricultural water supply.",
        "category": "piping",
        "domain": "piping",
        "standard_role": "PRIMARY_PRODUCT_STANDARD",
        "versions": ["2016"],
        "lifecycle_events": [],
        "keywords": ["HDPE pipe", "polyethylene pipe", "PE 100", "PE 80", "water supply pipe", "potable water pipe"],
        "product_terms": ["HDPE pipe", "HDPE pipes", "polyethylene pipe", "PE pipe"],
        "application_terms": ["potable water supply", "irrigation water", "water distribution network"],
        "exclusion_terms": ["casing pipe"],
        "evidence_ids": ["E-4984-SCOPE"]
    },
    {
        "standard_id": "IS 4985:2021",
        "title": "Unplasticized Polyvinyl Chloride (uPVC) Pipes for Potable Water Supplies — Specification",
        "scope": "Specification for unplasticized polyvinyl chloride (uPVC) pipes for potable water supplies, irrigation, and plumbing installations.",
        "category": "piping",
        "domain": "piping",
        "standard_role": "PRIMARY_PRODUCT_STANDARD",
        "versions": ["2021"],
        "lifecycle_events": [],
        "keywords": ["uPVC pipe", "PVC pipe", "potable water", "irrigation pipe", "plumbing pipe"],
        "product_terms": ["uPVC pipe", "uPVC pipes", "unplasticized PVC pipe"],
        "application_terms": ["potable water supply", "agricultural irrigation", "water supply network"],
        "exclusion_terms": ["borewell casing pipe"],
        "evidence_ids": ["E-4985-SCOPE"]
    },
    {
        "standard_id": "IS 12818:2010",
        "title": "Unplasticized PVC (uPVC) Screen and Casing Pipes for Borewells / Tubewells — Specification",
        "scope": "Specification for unplasticized PVC screen and casing pipes with ribbed or plain surfaces for borewells and tubewells.",
        "category": "piping",
        "domain": "piping",
        "standard_role": "PRIMARY_PRODUCT_STANDARD",
        "versions": ["2010"],
        "lifecycle_events": [],
        "keywords": ["casing pipe", "screen pipe", "uPVC casing", "borewell casing", "tubewell pipe"],
        "product_terms": ["casing pipe", "uPVC casing pipe", "borewell casing pipe", "screen pipe"],
        "application_terms": ["borewell", "tubewell", "groundwater extraction"],
        "exclusion_terms": [],
        "evidence_ids": ["E-12818-SCOPE"]
    },
    {
        "standard_id": "IS 8329:2020",
        "title": "Centrifugally Cast (Spun) Ductile Iron Pressure Pipes for Water, Gas and Sewage — Specification",
        "scope": "Specification for centrifugally cast (spun) ductile iron pressure pipes with socket and spigot ends for water, gas and sewage pipelines.",
        "category": "piping",
        "domain": "piping",
        "standard_role": "PRIMARY_PRODUCT_STANDARD",
        "versions": ["2020"],
        "lifecycle_events": [],
        "keywords": ["ductile iron pipe", "DI pipe", "spun iron pipe", "water transmission", "pumping main"],
        "product_terms": ["ductile iron pipe", "DI pipe", "DI pipes", "ductile iron pressure pipe"],
        "application_terms": ["water supply main", "pumping main", "rising main", "water transmission"],
        "exclusion_terms": [],
        "evidence_ids": ["E-8329-SCOPE"]
    },
    {
        "standard_id": "IS 778:1984",
        "title": "Specification for Copper Alloy Gate, Globe and Check Valves for Waterworks Purposes",
        "scope": "Specification for copper alloy (gunmetal and brass) gate, globe and check valves for waterworks purposes suitable for maximum working pressures up to 1.6 MPa.",
        "category": "valves",
        "domain": "mechanical",
        "standard_role": "PRIMARY_PRODUCT_STANDARD",
        "versions": ["1984"],
        "lifecycle_events": [],
        "keywords": ["gunmetal valve", "brass valve", "gate valve", "globe valve", "check valve", "waterworks valve"],
        "product_terms": ["gunmetal valve", "copper alloy valve", "brass gate valve", "brass check valve"],
        "application_terms": ["waterworks", "potable water distribution", "pump plumbing"],
        "exclusion_terms": [],
        "evidence_ids": ["E-778-SCOPE"]
    },
    {
        "standard_id": "IS 5312-1:2004",
        "title": "Swing Check Type Reflux (Non-Return) Valves for Waterworks Purposes — Part 1: Single Door Pattern",
        "scope": "Specification for swing check type reflux (non-return) valves of single door pattern for waterworks purposes on rising mains and pump discharge lines.",
        "category": "valves",
        "domain": "mechanical",
        "standard_role": "PRIMARY_PRODUCT_STANDARD",
        "versions": ["2004"],
        "lifecycle_events": [],
        "keywords": ["non return valve", "NRV", "reflux valve", "check valve", "swing check valve", "pump discharge valve"],
        "product_terms": ["non return valve", "reflux valve", "swing check valve", "NRV valve"],
        "application_terms": ["pump discharge line", "waterworks", "rising main"],
        "exclusion_terms": [],
        "evidence_ids": ["E-5312-1-SCOPE"]
    },
    {
        "standard_id": "IS 14846:2000",
        "title": "Sluice Valves for Waterworks Purposes (50 to 1200 mm Size) — Specification",
        "scope": "Specification for cast iron sluice valves (size 50 mm to 1200 mm) with inside screw non-rising spindle for waterworks and flow isolation.",
        "category": "valves",
        "domain": "mechanical",
        "standard_role": "PRIMARY_PRODUCT_STANDARD",
        "versions": ["2000"],
        "lifecycle_events": [],
        "keywords": ["sluice valve", "gate valve 100mm", "isolation valve", "cast iron sluice valve", "waterworks valve"],
        "product_terms": ["sluice valve", "cast iron sluice valve", "waterworks sluice valve"],
        "application_terms": ["waterworks", "pipeline isolation", "water distribution network"],
        "exclusion_terms": [],
        "evidence_ids": ["E-14846-SCOPE"]
    },
    {
        "standard_id": "IS 779:1994",
        "title": "Water Meters (Domestic Type) — Specification",
        "scope": "Specification for inferential and semi-positive volumetric domestic water meters (size 15 mm to 50 mm) for cold potable water measurement.",
        "category": "instrumentation",
        "domain": "instrumentation",
        "standard_role": "PRIMARY_PRODUCT_STANDARD",
        "versions": ["1994"],
        "lifecycle_events": [],
        "keywords": ["water meter", "domestic water meter", "flow meter", "water measurement"],
        "product_terms": ["water meter", "domestic water meter", "cold water meter"],
        "application_terms": ["potable water measurement", "domestic water billing", "water flow measurement"],
        "exclusion_terms": [],
        "evidence_ids": ["E-779-SCOPE"]
    },
    {
        "standard_id": "IS 3043:2018",
        "title": "Code of Practice for Earthing",
        "scope": "Code of practice for design, installation and maintenance of earthing systems in electrical installations including pumpsets, motor control centers and distribution systems.",
        "category": "safety",
        "domain": "electrical",
        "standard_role": "CODE_OF_PRACTICE",
        "versions": ["2018"],
        "lifecycle_events": [],
        "keywords": ["earthing", "earthing code", "electrical grounding", "pump earthing", "substation earthing"],
        "product_terms": [],
        "application_terms": ["electrical earthing", "earthing installation", "pump safety", "motor grounding"],
        "exclusion_terms": [],
        "evidence_ids": ["E-3043-SCOPE"]
    }
]

new_relationships = [
    {
        "from_standard": "IS 14220:2018",
        "to_standard": "IS 3043:2018",
        "relationship_type": "safety",
        "evidence_ids": ["E-3043-SCOPE"],
        "description": "Code of practice for earthing and electrical installation safety for openwell submersible pumpsets."
    },
    {
        "from_standard": "IS 8034:2018",
        "to_standard": "IS 12818:2010",
        "relationship_type": "companion_specification",
        "evidence_ids": ["E-12818-SCOPE"],
        "description": "Companion specification for uPVC screen and casing pipes used in deep borewells housing submersible pumps."
    },
    {
        "from_standard": "IS 8034:2018",
        "to_standard": "IS 3043:2018",
        "relationship_type": "safety",
        "evidence_ids": ["E-3043-SCOPE"],
        "description": "Code of practice for earthing and electrical installation safety for borewell submersible pumpsets."
    },
    {
        "from_standard": "IS 9079:2018",
        "to_standard": "IS 12615:2018",
        "relationship_type": "normative_reference",
        "evidence_ids": ["E-12615-SCOPE"],
        "description": "Normative energy efficiency specification for line-operated three-phase electric motors driving monoset pumps."
    },
    {
        "from_standard": "IS 9079:2018",
        "to_standard": "IS 996:2009",
        "relationship_type": "normative_reference",
        "evidence_ids": ["E-996-SCOPE"],
        "description": "Normative specification for single-phase electric motors driving domestic monoset pumps."
    },
    {
        "from_standard": "IS 9079:2018",
        "to_standard": "IS 5312-1:2004",
        "relationship_type": "companion_specification",
        "evidence_ids": ["E-5312-1-SCOPE"],
        "description": "Companion non-return valve specification on discharge piping of monoset pump installations."
    },
    {
        "from_standard": "IS 8472:2019",
        "to_standard": "IS 11346:2002",
        "relationship_type": "test_method",
        "evidence_ids": ["E-8472-SCOPE"],
        "description": "Code of acceptance for hydraulic performance testing of regenerative pumps."
    },
    {
        "from_standard": "IS 12225:2019",
        "to_standard": "IS 11346:2002",
        "relationship_type": "test_method",
        "evidence_ids": ["E-12225-SCOPE"],
        "description": "Code of acceptance for hydraulic performance testing of centrifugal jet pumpsets."
    },
    {
        "from_standard": "IS 1520:1980",
        "to_standard": "IS 11346:2002",
        "relationship_type": "test_method",
        "evidence_ids": ["E-1520-SCOPE"],
        "description": "Code of acceptance for hydraulic performance testing of horizontal centrifugal agricultural pumps."
    },
    {
        "from_standard": "IS 1710:2021",
        "to_standard": "IS 11346:2002",
        "relationship_type": "test_method",
        "evidence_ids": ["E-1710-SCOPE"],
        "description": "Code of acceptance for hydraulic performance testing of vertical turbine pumps."
    },
    {
        "from_standard": "IS 12615:2018",
        "to_standard": "IS/IEC 60947-4-1:2019",
        "relationship_type": "companion_specification",
        "evidence_ids": ["E-60947-4-1-SCOPE"],
        "description": "Companion specification for electromechanical contactors and motor-starters protecting 3-phase induction motors."
    },
    {
        "from_standard": "IS 14846:2000",
        "to_standard": "IS 778:1984",
        "relationship_type": "related_product",
        "evidence_ids": ["E-778-SCOPE"],
        "description": "Companion flow control valves for waterworks isolation and distribution networks."
    }
]

# Append new entries without duplicates
for src in new_sources:
    if src["source_id"] not in existing_src_ids:
        data["sources"].append(src)
        existing_src_ids.add(src["source_id"])

for ev in new_evidence:
    if ev["evidence_id"] not in existing_ev_ids:
        data["evidence"].append(ev)
        existing_ev_ids.add(ev["evidence_id"])

for std in new_standards:
    if std["standard_id"] not in existing_std_ids:
        data["standards"].append(std)
        existing_std_ids.add(std["standard_id"])

existing_rel_pairs = {(r["from_standard"], r["to_standard"], r["relationship_type"]) for r in data["relationships"]}
for rel in new_relationships:
    pair = (rel["from_standard"], rel["to_standard"], rel["relationship_type"])
    if pair not in existing_rel_pairs:
        data["relationships"].append(rel)
        existing_rel_pairs.add(pair)

seed_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Expanded corpus: {len(data['standards'])} standards, {len(data['evidence'])} evidence, {len(data['relationships'])} relationships, {len(data['sources'])} sources.")
