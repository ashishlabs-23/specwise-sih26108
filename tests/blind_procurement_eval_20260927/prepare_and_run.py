"""Create expectation files/PDFs first, then upload PDFs via production UI."""
import json
import re
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz

ROOT = Path(__file__).resolve().parent
EXPECTED = ROOT / "expected"
PDFS = ROOT / "pdfs"
CAPTURES = ROOT / "captures"
URL = "https://specwise-sih26108.web.app"
API_UPLOAD = "https://specwise-sih26108.onrender.com/api/v1/upload-pdf"

CASES = [
    dict(id="BLIND-01", domain="water systems", class_="meaningful_overlap", mode="short", text="Supply and commissioning of 7.5 HP submersible pump sets for 180 mm agricultural bore wells, rated 415 V three phase, 50 Hz, 72 m head and 6 L/s discharge for a village water scheme. Require performance acceptance testing and conformity to IS 8034:2018.", expected="A strong borewell pump match may be recommended; the reference and product intent should agree. No unrelated standard should become primary.", primary="IS 8034:2018"),
    dict(id="BLIND-02", domain="agricultural equipment", class_="meaningful_overlap", mode="short with historical reference", text="Procure 5.5 HP open-well submersible pump sets for lifting clear water from dug wells to field channels. Three phase 415 V supply, 24 m duty head, 12 L/s discharge, cast iron casing and site acceptance test. Tender cites IS 14220:1994.", expected="Openwell product intent should identify the current corpus family; the historical cited edition must remain an edition-mismatch review, not be treated as current.", primary="IS 14220:2018"),
    dict(id="BLIND-03", domain="industrial equipment", class_="meaningful_overlap", mode="short with current reference", text="Purchase 3 HP monoblock pump sets for clear, cold washdown water at a food-packaging unit, 415 V three phase, 50 Hz, 32 m head, 450 L/min, with factory performance test and IS 9079:2018 compliance documents.", expected="The monoset pump family is represented; a strong applicable primary may be recommended if all gates pass.", primary="IS 9079:2018"),
    dict(id="BLIND-04", domain="water systems", class_="meaningful_overlap", mode="long numbered tender with boilerplate", text="MUNICIPAL LIFT-IRRIGATION PROCUREMENT\n1. Scope: Supply two 6 HP openwell submersible pump sets for a lined irrigation reservoir and delivery main.\n2. Duty: 415 V, three phase, 50 Hz; 26 m total head; 10 L/s per pump; clear raw water.\n3. Construction: corrosion-resistant fasteners, guarded coupling, lifting arrangement and replaceable wear parts.\n4. Testing: submit performance curves and conduct witnessed acceptance testing.\n5. Delivery: deliver to three district depots, commission and train operators.\n6. Warranty: provide a two-year service plan and spare-parts schedule.\n7. Bid forms: submit sealed price schedules, tax registration, bank details, non-blacklisting declaration, delivery timetable and signed general conditions.\n8. Evaluation: purchaser may seek clarifications and reject incomplete bids. The specified equipment is the openwell pump set; references to site piping are interface requirements only.", expected="The pump is a meaningful openwell procurement. RECOMMEND is plausible if extracted technical requirements are covered; unresolved item requirements should yield REVIEW.", primary="IS 14220:2018"),
    dict(id="BLIND-05", domain="mechanical", class_="meaningful_overlap", mode="numbered mixed pump/cable with historical reference", text="1) Supply a 4 HP borewell submersible pump set for a 125 mm farm well, 415 V three phase, 60 m head and 3.5 L/s discharge.\n2) Include 30 m of flat, three-core PVC insulated submersible cable rated 1100 V; the schedule cites IS 694:1990.\n3) Include starter panel, protection relay and delivery column.\n4) Conduct pump performance testing and hand over the test record.\n5) Provide installation, warranty and operator instructions.", expected="The borewell pump is supported, while the historical cable edition and other components may remain unresolved. Do not silently cover those gaps; REVIEW is the safe result.", primary="IS 8034:2018"),
    dict(id="BLIND-06", domain="renewable energy", class_="partially_related", mode="mixed solar and water equipment, fake reference", text="Package for a remote solar water-lifting installation: 4 kW PV array, MPPT controller, battery bank, telemetry and a 5 HP submersible pump for a 90 m agricultural bore. The schedule cites IS 8034:2018 for the pump and IS 77777:2026 for the solar controller. Provide design, installation, commissioning and 12-month performance monitoring.", expected="The pump may match, but the renewable system and fake controller reference are not fully supported. Expect REVIEW with an explicit unverified-reference gap, not RECOMMEND.", primary="IS 8034:2018"),
    dict(id="BLIND-07", domain="electrical", class_="partially_related", mode="cable-only with historical reference", text="Supply 1.1 kV PVC insulated, armoured, four-core low-voltage feeder cables for a small pump-house distribution panel. Cable sizes 16 and 35 square millimetres; the drawing notes IS 1554 (Part 1):1988. Include drums, glands and continuity-test records.", expected="Cable terminology overlaps the corpus, but the cited standard is historical and the corpus role may be related rather than primary. Do not claim a definitive primary certification recommendation.", primary=None),
    dict(id="BLIND-08", domain="civil/building", class_="partially_related", mode="building system with accessory-only pump", text="Modernize a 12-storey passenger lift installation including traction machines, controller, landing doors, guide rails, emergency communication, fire recall and standby power. The basement package includes a small sump pump for incidental water removal. Submit structural calculations, inspection certificates and integrated commissioning records.", expected="The lift/building system is primary; an incidental sump pump mention must not promote a pump standard. If candidate retrieval remains, it must not become primary.", primary=None),
    dict(id="BLIND-09", domain="laboratory", class_="partially_related", mode="laboratory skid with accessory feed pump", text="Supply a laboratory ultrapure-water skid with reverse-osmosis membranes, UV oxidation, resistivity monitor, TOC analyzer and automatic sanitization. A small feed pump is included inside the skid as a replaceable accessory. Provide calibration certificates, validation protocol and one-year consumables.", expected="Water-treatment laboratory equipment is primary; feed-pump language is accessory context. No pump standard should be promoted as the procurement primary.", primary=None),
    dict(id="BLIND-10", domain="industrial equipment", class_="partially_related", mode="mechanical system with mixed requirements", text="Provide an induced-draft cooling-tower package for a process plant: fan assembly, gearbox, drift eliminators, fill media, basin, make-up controls and circulating-water pump set. The pump is one subsystem among multiple separately tested components. Include vibration limits, noise report and site acceptance plan.", expected="Some pump terminology is relevant, but the complete cooling-tower package is not covered. Review or abstention is defensible; RECOMMEND for the whole package is not.", primary=None),
    dict(id="BLIND-11", domain="electrical", class_="clearly_outside", mode="short, no IS reference", text="Supply a 630 kVA, 11/0.433 kV oil-immersed distribution transformer with off-circuit tap changer, silica-gel breather, Buchholz relay, marshalling box and routine electrical test certificates for a campus substation.", expected="Transformer procurement is outside the current corpus. Do not recommend a pump or cable standard based on incidental electrical language.", primary=None),
    dict(id="BLIND-12", domain="civil/building", class_="clearly_outside", mode="long numbered tender, boilerplate-heavy", text="1. Work: seismic retrofit and façade repair of the municipal records building.\n2. Install carbon-fibre reinforcement at nominated beams and columns.\n3. Replace expansion joints and repair concrete spalling.\n4. Provide scaffolding, debris removal, protection screens and a site safety plan.\n5. Submit structural calculations, material certificates and inspection reports.\n6. General conditions: sealed tender, tax registration, bank information, non-blacklisting declaration, delivery plan, insurance, warranty, signed forms and purchaser right to clarify or reject bids.\n7. No mechanical water equipment is included in the work scope.", expected="Building retrofit is outside the corpus. Long generic boilerplate must not create a product match or evidence.", primary=None),
    dict(id="BLIND-13", domain="laboratory", class_="clearly_outside", mode="laboratory analyzer with plausible reference", text="Purchase a benchtop gas chromatograph mass spectrometer with autosampler, capillary column oven, electron-ionization source, spectral library and nitrogen generator. Provide IQ/OQ documents, traceable calibration, training and two-year service. The laboratory schedule references IS 88888:2024 for instrument performance.", expected="Analytical laboratory instrumentation is outside the corpus. The plausible citation must remain unverified and must not produce verified corpus evidence or a pump primary.", primary=None),
    dict(id="BLIND-14", domain="renewable energy", class_="clearly_outside", mode="renewable system with accessory cable terms", text="Design, supply and commission a 180 kWp rooftop photovoltaic generation plant with mono-PERC modules, string inverters, rooftop mounting rails, DC isolators, AC combiner panels, monitoring gateway and earthing grid. Include DC and AC cable runs, generation forecast and grid-synchronization tests.", expected="Solar generation is the primary procurement. Incidental DC/AC cables must not make the document a cable-standard recommendation.", primary=None),
    dict(id="BLIND-15", domain="safety/fire", class_="clearly_outside", mode="fire safety system with pump component", text="Install an addressable fire alarm and clean-agent suppression system for a data hall: smoke detectors, aspirating detection, releasing panel, cylinders, distribution pipework, sounders and cause-effect programming. Include integrated cause-and-effect testing and authority inspection. A small jockey pump serves the adjacent fire-water header.", expected="Fire safety systems are outside the corpus. Jockey-pump mention is an accessory and must not trigger a pump-standard primary.", primary=None),
    dict(id="BLIND-16", domain="mechanical", class_="ambiguous_underspecified", mode="short, ambiguous product", text="Procure one pump package for process liquid transfer. Medium, installation arrangement, duty point, head, flow and pump construction will be finalized after award. Vendor may propose a suitable type.", expected="Pump terminology may be relevant, but product intent and parameters are insufficient to choose an openwell, borewell or monoset standard. ABSTAIN/REVIEW is expected; no definitive RECOMMEND.", primary=None),
    dict(id="BLIND-17", domain="water systems", class_="ambiguous_underspecified", mode="short, incomplete well equipment description", text="Provide a submersible assembly for deep community wells, complete with starter and rising main. Well diameter, motor rating, water application and duty point are not available at tender stage.", expected="Potential pump-family language is present, but insufficient detail should lead to ABSTAIN or REVIEW rather than an unjustified primary recommendation.", primary=None),
    dict(id="BLIND-18", domain="agricultural equipment", class_="ambiguous_underspecified", mode="underspecified farm equipment", text="Supply water-lifting equipment for a farm pond and seasonal irrigation channel. The department has not selected the equipment type, source depth, capacity or power arrangement; bidder may recommend a configuration after a site visit.", expected="Agricultural water context alone is insufficient to choose a corpus product family. Do not recommend a standard solely from application words.", primary=None),
    dict(id="BLIND-19", domain="industrial equipment", class_="ambiguous_underspecified", mode="generic pump with incidental numeric requirements", text="Supply two standard pump sets for a plant utility service, 5 HP, 415 V, 50 Hz. Fluid, suction arrangement, well type, duty head and discharge are to be confirmed during detailed engineering.", expected="Generic pump candidates may appear, but this does not distinguish product family or establish full coverage. ABSTAIN/REVIEW, not an unqualified recommendation.", primary=None),
    dict(id="BLIND-20", domain="medical/technical equipment", class_="ambiguous_underspecified", mode="technical assembly without procurement discriminator", text="Deliver a 5 HP, 415 V submersible drive assembly for a controlled wet test cell. The procurement schedule does not state whether the assembly includes a pump, motor only, cooling equipment or circulation unit. Final process interface is pending.", expected="The product itself is unclear despite a submersible technical phrase. ABSTAIN or REVIEW is defensible; do not infer a pump standard.", primary=None),
]


def write_fixtures():
    EXPECTED.mkdir(parents=True, exist_ok=True)
    PDFS.mkdir(parents=True, exist_ok=True)
    CAPTURES.mkdir(parents=True, exist_ok=True)
    for case in CASES:
        fixture = {
            "pdf_id": case["id"], "domain": case["domain"],
            "expected_behavioral_class": case["class_"], "format_variation": case["mode"],
            "expected_behavior": case["expected"], "expected_primary_if_appropriate": case["primary"],
            "source_text_for_pdf": case["text"],
            "fixture_created_before_production_upload": True,
        }
        (EXPECTED / f"{case['id']}.json").write_text(json.dumps(fixture, indent=2), encoding="utf-8")
    (ROOT / "expected-index.json").write_text(json.dumps([
        {k: v for k, v in case.items() if k not in {"text"}} for case in CASES
    ], indent=2), encoding="utf-8")


def create_pdfs():
    for case in CASES:
        path = PDFS / f"{case['id']}.pdf"
        doc = fitz.open()
        text = case["text"]
        if case["id"] == "BLIND-04":
            text += "\nGENERAL CONDITIONS: Bidders must submit signed schedules, tax details, insurance, warranties, delivery dates and declarations. The purchaser may clarify submissions. These are administrative requirements and do not change the equipment scope.\n" * 8
        if case["id"] == "BLIND-12":
            text += "\nAll quantities are subject to measurement; bidders shall attend the site conference and submit sealed envelopes with signed declarations.\n" * 12
        chunks = [text[i:i + 2600] for i in range(0, len(text), 2600)]
        for chunk in chunks:
            page = doc.new_page()
            page.insert_textbox(fitz.Rect(48, 48, 545, 790), chunk, fontsize=10, fontname="helv")
        doc.save(path)
        doc.close()


def classify_ui_decision(text):
    for decision, pattern in [
        ("RECOMMEND", r"\bRECOMMEND\b"),
        ("REVIEW", r"\bREVIEW NEEDED\b"),
        ("ABSTAIN", r"\bNO PRIMARY MATCH\b"),
        ("OUT_OF_CORPUS", r"\bOUT OF CORPUS\b"),
    ]:
        if re.search(pattern, text):
            return decision
    return None


def perform_upload(page, case):
    page.locator("button:has-text('Upload Document (PDF)')").click()
    page.locator("input[type=file]").set_input_files(str(PDFS / f"{case['id']}.pdf"))
    page.locator("button:has-text('Process Document')").click()
    page.wait_for_function(
        "() => { const d=document.querySelector('dialog'); if(!d || !d.open) return true; "
        "return /could not|OCR integration|upload failed|invalid, unprotected/i.test(d.innerText); }",
        timeout=90000,
    )
    page.wait_for_timeout(350)


def extract_ui(page, case_id):
    result_text = page.locator("#results-section").inner_text()
    decision = classify_ui_decision(result_text)
    primary_row = page.get_by_text("Standard No.", exact=True)
    primary = re.findall(r"IS\s+\d{3,6}:\d{4}", primary_row.locator("xpath=..").inner_text()) if primary_row.count() else []
    dialog = page.locator("dialog")
    error_node = dialog.locator(".text-red-600") if dialog.count() else None
    error = error_node.inner_text() if error_node and error_node.count() else ""
    cert = " ".join(line.strip() for line in result_text.splitlines() if "certification / qco status" in line.casefold() or "qco proposed" in line.casefold() or "not applicable" in line.casefold() or "not evaluated" in line.casefold() or "review required" in line.casefold())
    tabs = {}
    audit = page.locator("#advanced-accordion")
    if not error and audit.count():
        show = page.get_by_text("Show Details", exact=True)
        if show.count():
            show.click()
        for tab_name, button_pattern in [
            ("coverage", "Coverage & Gaps"),
            ("evidence", "Evidence Provenance"),
            ("applicability", "Applicability"),
            ("requirements", "Requirements"),
        ]:
            button = page.get_by_role("button", name=re.compile(button_pattern))
            if button.count():
                button.first.click()
                page.wait_for_timeout(80)
                tabs[tab_name] = audit.inner_text()
    page.screenshot(path=str(CAPTURES / f"{case_id}.png"), full_page=True)
    return {"decision": decision, "primary_standard": primary, "certification_state": cert, "error": error, "rendered_result": result_text, "rendered_tabs": tabs}


def main():
    # All expectation files are persisted before any PDF is uploaded.
    write_fixtures()
    create_pdfs()
    records = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1050})
        responses = []

        def on_response(response):
            if response.url.rstrip("/").endswith("/api/v1/upload-pdf") and response.request.method == "POST":
                try:
                    responses.append({"status": response.status, "json": response.json()})
                except Exception as exc:
                    responses.append({"status": response.status, "error": str(exc)})

        page.on("response", on_response)
        page.goto(URL, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_function("() => /RECOMMEND|REVIEW NEEDED|NO PRIMARY MATCH|OUT OF CORPUS/.test(document.querySelector('#results-section')?.innerText || '')", timeout=90000)

        for case in CASES:
            fixture_path = EXPECTED / f"{case['id']}.json"
            fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
            responses.clear()
            page.locator("textarea").fill(f"Blind procurement evaluation {case['id']}")
            perform_upload(page, case)
            if not page.locator("dialog .text-red-600").count():
                page.wait_for_function("() => /RECOMMEND|REVIEW NEEDED|NO PRIMARY MATCH|OUT OF CORPUS/.test(document.querySelector('#results-section')?.innerText || '')", timeout=90000)
            ui = extract_ui(page, case["id"])
            api = responses[-1] if responses else {"status": None, "error": "No upload response captured"}
            body = api.get("json", {})
            api_candidates = [c.get("standard_id") for c in body.get("candidates", [])]
            api_primary = []
            strong = [a.get("standard_id") for a in body.get("applicability", []) if a.get("result") == "strong"]
            if body.get("decision") in {"RECOMMEND", "REVIEW"}:
                api_primary = strong[:1]
            refs = [c for c in body.get("coverage", []) if c.get("state") in {"unverified_reference", "edition_mismatch"}]
            api_cert = body.get("certification", {})
            api_cert_states = sorted({v.get("state") for v in api_cert.values() if v.get("state")})
            ui_ids = sorted(set(re.findall(r"IS\s+\d{3,6}:\d{4}", " ".join(ui["rendered_tabs"].get("applicability", "").splitlines()))))
            ui_ev_count = len(set(re.findall(r"\bE-[A-Z0-9-]+\b", ui["rendered_tabs"].get("evidence", ""))))
            coverage_states_ui = re.findall(r"\b(COVERED|PARTIAL|NOT_COVERED|UNVERIFIED_REFERENCE|EDITION_MISMATCH|UNKNOWN|CONFLICTING)\b", ui["rendered_tabs"].get("coverage", ""), re.I)
            if api.get("status") == 200:
                parity = {
                    "decision": ui["decision"] == body.get("decision"),
                    "primary": sorted(ui["primary_standard"]) == sorted(api_primary),
                    "candidates_visible": set(api_candidates).issubset(set(ui_ids)),
                    "coverage_states_visible": all(str(x.get("state", "")).upper() in [v.upper() for v in coverage_states_ui] for x in body.get("coverage", [])),
                    "evidence_count_visible": ui_ev_count == len(body.get("evidence", [])),
                }
            else:
                parity = {"decision": ui["decision"] is None and bool(ui["error"]), "primary": True, "candidates_visible": True, "coverage_states_visible": True, "evidence_count_visible": True}
            expected_primary = fixture.get("expected_primary_if_appropriate")
            record = {
                "pdf_id": case["id"], "domain": case["domain"],
                "expected_behavioral_class": fixture["expected_behavioral_class"],
                "expected_behavior": fixture["expected_behavior"],
                "fixture_written_before_upload": fixture["fixture_created_before_production_upload"],
                "api_status": api.get("status"), "actual_decision": body.get("decision"),
                "actual_primary_standard": api_primary, "ui_primary_standard": ui["primary_standard"],
                "candidate_count": len(api_candidates), "candidates": api_candidates,
                "applicability": body.get("applicability", []),
                "coverage": body.get("coverage", []), "gaps": body.get("gaps", []),
                "unverified_references": refs,
                "evidence_count": len(body.get("evidence", [])),
                "evidence_ids": [e.get("evidence_id") for e in body.get("evidence", [])],
                "certification": api_cert, "certification_states": api_cert_states,
                "ui_certification_state": ui["certification_state"],
                "ui_agrees_with_backend": parity,
                "ui_parity": all(parity.values()),
                "error": ui["error"], "pdf_extracted_text": body.get("input_text"),
                "pdf_requirements": body.get("requirements", []),
                "ui": ui,
                "api_http_status": api.get("status"),
                "decision_classification": None,
                "expected_primary_if_appropriate": expected_primary,
            }
            records.append(record)
            (ROOT / "actual" / f"{case['id']}.json").parent.mkdir(parents=True, exist_ok=True)
            (ROOT / "actual" / f"{case['id']}.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
            print(json.dumps({"pdf_id": case["id"], "decision": record["actual_decision"], "primary": api_primary, "parity": parity, "error": ui["error"]}))
            if ui["error"]:
                page.locator("dialog button:has-text('Cancel')").click()

        browser.close()
    (ROOT / "actual-results.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Captured {len(records)} production PDF uploads at {ROOT}")


if __name__ == "__main__":
    main()
