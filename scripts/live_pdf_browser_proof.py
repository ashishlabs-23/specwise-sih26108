"""Upload the local red-team PDFs through the deployed SpecWise UI and capture rendered state."""
import json
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "tests" / "live_pdf_redteam_20260926"
OUT = ROOT / "tests" / "production_pdf_proof"
URL = "https://specwise-sih26108.web.app"


def wait_for_result(page):
    page.wait_for_function(
        "() => { const e=document.querySelector('#results-section'); if(!e) return false; "
        "return /RECOMMEND|REVIEW NEEDED|NO PRIMARY MATCH|OUT OF CORPUS/.test(e.innerText); }",
        timeout=90000,
    )
    page.wait_for_timeout(700)


def upload(page, name):
    dialog = page.locator("dialog")
    if not (dialog.count() and dialog.first.is_visible()):
        button = page.locator("button:has-text('Upload Document (PDF)')")
        if button.count() == 0:
            button = page.locator("button").filter(has_text=re.compile("Upload.*PDF", re.I)).first
        button.click()
    modal_title = page.locator("text=Upload Tender Document (PDF)")
    if modal_title.count() == 0:
        page.locator("button").filter(has_text=re.compile("Upload.*PDF", re.I)).first.click()
    page.locator("input[type=file]").set_input_files(str(PDF_DIR / name))
    page.locator("button:has-text('Process Document')").click()
    page.wait_for_function(
        "() => { const d=document.querySelector('dialog'); if(!d || !d.open) return true; "
        "return /could not|OCR integration|upload failed|invalid, unprotected/i.test(d.innerText); }",
        timeout=90000,
    )
    page.wait_for_timeout(500)


def rendered_state(page, label, screenshot=True):
    page.wait_for_timeout(500)
    result = {"label": label, "url": page.url}
    results = page.locator("#results-section")
    result["rendered_result"] = results.inner_text() if results.count() else ""
    result["error"] = ""
    dialog = page.locator("dialog")
    if dialog.count() and dialog.first.is_visible():
        error_node = dialog.locator(".text-red-600")
        result["error"] = error_node.inner_text() if error_node.count() else dialog.first.inner_text()
    result["decision"] = next((label for label, pattern in (
        ("RECOMMEND", r"\bRECOMMEND\b"), ("REVIEW", r"\bREVIEW NEEDED\b"),
        ("ABSTAIN", r"\bNO PRIMARY MATCH\b"), ("OUT_OF_CORPUS", r"\bOUT OF CORPUS\b"),
    ) if re.search(pattern, result["rendered_result"])), None)
    primary_row = page.get_by_text("Standard No.", exact=True)
    result["primary"] = re.findall(r"IS\s+\d{3,6}:\d{4}", primary_row.locator("xpath=..").inner_text()) if primary_row.count() else []
    result["certification"] = " ".join(
        x.strip() for x in result["rendered_result"].splitlines()
        if any(term in x.casefold() for term in ("certification / qco status", "qco proposed", "not evaluated", "not applicable"))
    )
    if results.count() and not result["error"]:
        audit = page.locator("#advanced-accordion")
        if audit.count():
            if page.get_by_text("Show Details", exact=True).count():
                page.get_by_text("Show Details", exact=True).click()
            for tab in ("Coverage & Gaps", "Evidence Provenance", "Applicability", "Requirements"):
                button = page.get_by_role("button", name=re.compile(tab))
                if button.count():
                    button.first.click()
                    page.wait_for_timeout(100)
                    result[tab.lower().replace(" & ", "_").replace(" ", "_")] = audit.inner_text()
            result["candidates"] = result.get("applicability", "")
    if screenshot:
        OUT.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(OUT / f"{label}.png"), full_page=True)
    return result


def analyze_text(page, text):
    page.locator("textarea").fill(text)
    page.locator("button:has-text('Find Applicable Standards')").click()
    wait_for_result(page)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cases = [
        ("LIVE-PDF-01", "pdf-01-openwell.pdf"),
        ("LIVE-PDF-02", "pdf-02-borewell.pdf"),
        ("LIVE-PDF-03", "pdf-03-fire.pdf"),
        ("LIVE-PDF-04", "pdf-04-solar.pdf"),
        ("LIVE-PDF-05", "pdf-05-mixed.pdf"),
        ("LIVE-PDF-06", "pdf-06-fake-reference.pdf"),
        ("LIVE-PDF-07", "pdf-07-corrupt.pdf"),
        ("LIVE-PDF-08", "pdf-08-scanned.pdf"),
        ("LIVE-PDF-09", "pdf-09-injection.pdf"),
    ]
    output = {"site": URL, "pdf_cases": [], "transitions": []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        for label, filename in cases:
            page.goto(URL, wait_until="networkidle", timeout=90000)
            page.locator("#results-section").wait_for(timeout=90000)
            upload(page, filename)
            if not (page.locator("dialog .text-red-600").count()):
                wait_for_result(page)
            output["pdf_cases"].append(rendered_state(page, label))

        # One browser page exercises all requested state transitions.
        page.goto(URL, wait_until="networkidle", timeout=90000)
        page.locator("#results-section").wait_for(timeout=90000)
        sequence = [
            ("supported_pdf", "pdf-01-openwell.pdf"),
            ("unrelated_pdf", "pdf-03-fire.pdf"),
            ("unrelated_pdf_to_supported_pdf", "pdf-01-openwell.pdf"),
            ("supported_pdf_to_corrupt_pdf", "pdf-07-corrupt.pdf"),
            ("supported_pdf_to_scanned_pdf", "pdf-08-scanned.pdf"),
        ]
        for label, filename in sequence:
            upload(page, filename)
            if filename not in {"pdf-07-corrupt.pdf", "pdf-08-scanned.pdf"}:
                wait_for_result(page)
            output["transitions"].append(rendered_state(page, f"TRANSITION-{label}"))
        if page.locator("dialog").count() and page.locator("dialog").first.is_visible():
            page.locator("dialog button:has-text('Cancel')").click()
        analyze_text(page, "openwell submersible pumpset for agricultural irrigation")
        output["transitions"].append(rendered_state(page, "TRANSITION-pdf_to_text"))
        upload(page, "pdf-01-openwell.pdf")
        wait_for_result(page)
        output["transitions"].append(rendered_state(page, "TRANSITION-text_to_pdf"))
        upload(page, "pdf-06-fake-reference.pdf")
        wait_for_result(page)
        output["transitions"].append(rendered_state(page, "TRANSITION-fake_reference_pdf"))
        upload(page, "pdf-01-openwell.pdf")
        wait_for_result(page)
        output["transitions"].append(rendered_state(page, "TRANSITION-fake_to_supported_pdf"))
        browser.close()
    (OUT / "rendered-results.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(OUT), "pdf_cases": len(output["pdf_cases"]), "transitions": len(output["transitions"])}))


if __name__ == "__main__":
    main()
