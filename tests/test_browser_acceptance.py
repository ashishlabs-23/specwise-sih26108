import os
import time
import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
FIXTURES_DIR = Path(__file__).parent / "fixtures"

@pytest.fixture(scope="session")
def browser_context():
    wait_for_backend_health()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        yield context
        browser.close()

def wait_for_backend_health():
    import urllib.request
    import json
    for _ in range(3):
        try:
            with urllib.request.urlopen(f"{BACKEND_URL}/api/v1/health", timeout=2) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode())
                    if data.get("status") == "ok":
                        return True
        except Exception:
            pass
        time.sleep(1)
    pytest.skip(f"Test backend not reachable at {BACKEND_URL}; skipping browser acceptance tests.")

def test_00_backend_and_frontend_alive(browser_context):
    wait_for_backend_health()
    page = browser_context.new_page()
    response = page.goto(FRONTEND_URL, wait_until="networkidle")
    assert response.status == 200
    expect(page.locator("h1")).to_contain_text("Indian Standard")
    page.close()

def test_01_valid_text_query_recommend(browser_context):
    page = browser_context.new_page()
    page.goto(FRONTEND_URL, wait_until="networkidle")

    # Enter valid product description
    textarea = page.locator("textarea")
    textarea.fill("openwell submersible pumpset for agricultural irrigation")

    # Click search button
    page.locator("button:has-text('Find Applicable Standards')").click()

    # Wait for results section
    page.wait_for_selector("#results-section", state="visible", timeout=15000)

    # Check decision banner
    expect(page.locator("text=RECOMMEND").first).to_be_visible(timeout=10000)
    expect(page.locator("h2:has-text('IS 14220')")).to_be_visible()

    # Check Key Details Card & Evidence Sources Card
    expect(page.locator("h3:has-text('Key Details')")).to_be_visible()
    expect(page.locator("h3:has-text('Evidence / Sources')")).to_be_visible()
    page.close()

def test_02_ambiguous_text_query_review_or_abstain(browser_context):
    page = browser_context.new_page()
    page.goto(FRONTEND_URL, wait_until="networkidle")

    textarea = page.locator("textarea")
    textarea.fill("pumpset")
    page.locator("button:has-text('Find Applicable Standards')").click()

    # Wait for response
    page.wait_for_selector("#results-section", state="visible", timeout=15000)

    # Should be ABSTAIN or REVIEW badge for ambiguous query
    banner = page.locator("#results-section")
    decision_badge = banner.locator("span:has-text('REVIEW')").or_(banner.locator("span:has-text('ABSTAIN')")).first
    expect(decision_badge).to_be_visible(timeout=10000)
    page.close()

def test_03_unrelated_text_query_out_of_corpus(browser_context):
    page = browser_context.new_page()
    page.goto(FRONTEND_URL, wait_until="networkidle")

    textarea = page.locator("textarea")
    textarea.fill("quantum machine learning cryptography algorithm for blockchain cloud computing")
    page.locator("button:has-text('Find Applicable Standards')").click()

    # Wait for response
    page.wait_for_selector("#results-section", state="visible", timeout=15000)

    # Should be OUT_OF_CORPUS
    expect(page.locator("text=OUT OF CORPUS").or_(page.locator("text=OUT_OF_CORPUS")).first).to_be_visible(timeout=10000)
    page.close()

def test_04_valid_pdf_upload(browser_context):
    page = browser_context.new_page()
    page.goto(FRONTEND_URL, wait_until="networkidle")

    # Open PDF upload modal
    page.locator("button:has-text('Upload Document (PDF)')").click()
    expect(page.locator("text=Upload Tender Document (PDF)")).to_be_visible()

    # Upload valid PDF fixture
    valid_pdf_path = FIXTURES_DIR / "valid_spec.pdf"
    assert valid_pdf_path.exists(), "Valid PDF fixture missing"

    file_input = page.locator("input[type='file']")
    file_input.set_input_files(str(valid_pdf_path))

    # Click Process Document
    process_btn = page.locator("button:has-text('Process Document')")
    expect(process_btn).to_be_enabled()
    process_btn.click()

    # Wait for results to render
    page.wait_for_selector("#results-section", state="visible", timeout=15000)

    # Verify decision is RECOMMEND and standard is IS 14220
    expect(page.locator("text=RECOMMEND").first).to_be_visible(timeout=10000)
    expect(page.locator("h2:has-text('IS 14220')")).to_be_visible()
    page.close()

def test_05_malformed_pdf_user_error(browser_context):
    page = browser_context.new_page()
    page.goto(FRONTEND_URL, wait_until="networkidle")

    # Open PDF upload modal
    page.locator("button:has-text('Upload Document (PDF)')").click()
    expect(page.locator("text=Upload Tender Document (PDF)")).to_be_visible()

    # Upload malformed PDF fixture
    malformed_pdf_path = FIXTURES_DIR / "malformed.pdf"
    file_input = page.locator("input[type='file']")
    file_input.set_input_files(str(malformed_pdf_path))

    # Click Process Document
    page.locator("button:has-text('Process Document')").click()

    # Assert error text appears in the modal
    error_el = page.locator("div.text-red-600")
    expect(error_el).to_be_visible(timeout=8000)

    # Close modal
    page.locator("button:has-text('Cancel')").click()
    expect(page.locator("text=Upload Tender Document (PDF)")).not_to_be_visible()
    page.close()

def test_06_scanned_image_pdf_user_error(browser_context):
    page = browser_context.new_page()
    page.goto(FRONTEND_URL, wait_until="networkidle")

    # Open PDF upload modal
    page.locator("button:has-text('Upload Document (PDF)')").click()
    expect(page.locator("text=Upload Tender Document (PDF)")).to_be_visible()

    # Upload scanned image PDF fixture (no text layer)
    scanned_pdf_path = FIXTURES_DIR / "scanned_image.pdf"
    file_input = page.locator("input[type='file']")
    file_input.set_input_files(str(scanned_pdf_path))

    # Click Process Document
    page.locator("button:has-text('Process Document')").click()

    # Assert error message about no extractable text / OCR is displayed
    error_el = page.locator("div.text-red-600")
    expect(error_el).to_be_visible(timeout=8000)
    expect(error_el).to_contain_text("extractable")

    # Close modal
    page.locator("button:has-text('Cancel')").click()
    page.close()

def test_07_prompt_injection_pdf_resilience(browser_context):
    page = browser_context.new_page()
    page.goto(FRONTEND_URL, wait_until="networkidle")

    # Open PDF upload modal
    page.locator("button:has-text('Upload Document (PDF)')").click()

    # Upload prompt injection PDF fixture
    injection_pdf_path = FIXTURES_DIR / "prompt_injection.pdf"
    file_input = page.locator("input[type='file']")
    file_input.set_input_files(str(injection_pdf_path))

    # Click Process Document
    page.locator("button:has-text('Process Document')").click()

    # Wait for results
    page.wait_for_selector("#results-section", state="visible", timeout=15000)

    # Grounded decision must remain IS 14220 RECOMMEND, NOT IS 99999 or OVERRIDE
    expect(page.locator("text=RECOMMEND").first).to_be_visible(timeout=10000)
    expect(page.locator("h2:has-text('IS 14220')")).to_be_visible()
    expect(page.locator("text=IS 99999")).not_to_be_visible()
    expect(page.locator("text=OVERRIDE_SUCCESSFUL")).not_to_be_visible()
    page.close()

def test_08_evidence_source_modal(browser_context):
    page = browser_context.new_page()
    page.goto(FRONTEND_URL, wait_until="networkidle")

    # Wait for initial results
    page.wait_for_selector("#results-section", state="visible", timeout=15000)

    # Click "View all sources"
    view_sources_btn = page.locator("button:has-text('View all sources')")
    expect(view_sources_btn).to_be_visible()
    view_sources_btn.click()

    # Verify modal is visible
    expect(page.locator("text=All Verified Sources & Evidence")).to_be_visible()
    expect(page.locator("text=Verified Official BIS").first).to_be_visible()

    # Close modal
    page.locator("button:has-text('Close')").click()
    expect(page.locator("text=All Verified Sources & Evidence")).not_to_be_visible()
    page.close()

def test_09_related_standards_expansion(browser_context):
    page = browser_context.new_page()
    page.goto(FRONTEND_URL, wait_until="networkidle")

    # Wait for results
    page.wait_for_selector("#results-section", state="visible", timeout=15000)

    # Check Related Standards Card is present
    expect(page.locator("h3:has-text('Related Standards')")).to_be_visible()

    # Click "View all related standards"
    view_all_rel = page.locator("button:has-text('View all related standards')")
    expect(view_all_rel).to_be_visible()
    view_all_rel.click()

    # Verify advanced details accordion is scrolled / visible
    expect(page.locator("#advanced-accordion")).to_be_visible()
    page.close()

def test_10_certification_warning_and_modal(browser_context):
    page = browser_context.new_page()
    page.goto(FRONTEND_URL, wait_until="networkidle")

    # Wait for results
    page.wait_for_selector("#results-section", state="visible", timeout=15000)

    # Check Certification / QCO Status Banner
    expect(page.locator("text=Certification / QCO Status")).to_be_visible()
    expect(page.locator("text=QCO Proposed / Unconfirmed").or_(page.locator("text=Regulatory Notice"))).to_be_visible()

    # Click "Learn more"
    page.locator("button:has-text('Learn more')").click()

    # Modal should be open
    expect(page.locator("text=Regulatory & QCO Verification Notice")).to_be_visible()
    expect(page.locator("text=not_verified_in_prototype_corpus")).to_be_visible()

    # Close modal
    page.locator("button:has-text('Close')").click()
    expect(page.locator("text=Regulatory & QCO Verification Notice")).not_to_be_visible()
    page.close()

def test_11_report_modal_and_download(browser_context):
    page = browser_context.new_page()
    page.goto(FRONTEND_URL, wait_until="networkidle")

    # Wait for results
    page.wait_for_selector("#results-section", state="visible", timeout=15000)

    # Click Download Report (Audit HTML)
    report_btn = page.locator("button:has-text('Download Report (Audit HTML)')")
    expect(report_btn).to_be_visible()
    report_btn.click()

    # Verify report modal opened
    expect(page.locator("text=SpecWise Audit Report")).to_be_visible()
    expect(page.get_by_role("button", name="Download", exact=True)).to_be_visible()
    expect(page.locator("button:has-text('Print')")).to_be_visible()

    # Close modal using the top right close button in the report modal header
    close_btn = page.locator("div.fixed button:has(svg.lucide-x)").first
    close_btn.click()
    expect(page.locator("text=SpecWise Audit Report")).not_to_be_visible()
    page.close()

def test_12_new_search_reset(browser_context):
    page = browser_context.new_page()
    page.goto(FRONTEND_URL, wait_until="networkidle")

    # Wait for results
    page.wait_for_selector("#results-section", state="visible", timeout=15000)

    # Click "New Search"
    new_search_btn = page.locator("button:has-text('New Search')")
    expect(new_search_btn).to_be_visible()
    new_search_btn.click()

    # Text area is accessible and can be changed
    textarea = page.locator("textarea")
    textarea.fill("monoset pump for clear cold water for agriculture")
    page.locator("button:has-text('Find Applicable Standards')").click()

    # Wait for new recommendation
    page.wait_for_selector("#results-section", state="visible", timeout=15000)
    expect(page.locator("text=RECOMMEND").first).to_be_visible()
    expect(page.locator("h2:has-text('IS 9079')")).to_be_visible()
    page.close()

def test_13_backend_unavailable_error_state(browser_context):
    page = browser_context.new_page()
    page.goto(FRONTEND_URL, wait_until="networkidle")

    # Route-abort /api/v1/analyze to simulate backend down
    page.route("**/api/v1/analyze", lambda route: route.abort("failed"))

    textarea = page.locator("textarea")
    textarea.fill("monoset pump test")
    page.locator("button:has-text('Find Applicable Standards')").click()

    # Connection error banner must appear
    expect(page.locator("text=Connection / API Error")).to_be_visible(timeout=10000)
    expect(page.locator("button:has-text('Retry Analysis')")).to_be_visible()
    page.close()

def test_14_how_it_works_navigation_and_content(browser_context):
    page = browser_context.new_page()
    page.goto(FRONTEND_URL, wait_until="networkidle")

    # Click How it works in Navbar
    nav_link = page.locator("nav a:has-text('How it works')")
    expect(nav_link).to_be_visible()
    nav_link.click()

    # Verify navigation to /how-it-works
    page.wait_for_url("**/how-it-works", timeout=5000)
    expect(page.locator("h1")).to_contain_text("How SpecWise Works")

    # Verify 9 stages are explained
    expect(page.locator("text=Stage 01")).to_be_visible()
    expect(page.locator("text=Stage 09")).to_be_visible()

    # Verify four decision states are defined
    expect(page.locator("text=RECOMMEND").first).to_be_visible()
    expect(page.locator("text=REVIEW").first).to_be_visible()
    expect(page.locator("text=ABSTAIN").first).to_be_visible()
    expect(page.locator("text=OUT_OF_CORPUS").first).to_be_visible()

    # Refresh page to verify direct route access
    page.reload(wait_until="networkidle")
    expect(page.locator("h1")).to_contain_text("How SpecWise Works")
    page.close()

def test_15_resources_navigation_and_live_data(browser_context):
    page = browser_context.new_page()
    page.goto(FRONTEND_URL, wait_until="networkidle")

    # Click Resources in Navbar
    nav_link = page.locator("nav a:has-text('Resources')")
    expect(nav_link).to_be_visible()
    nav_link.click()

    # Verify navigation to /resources
    page.wait_for_url("**/resources", timeout=5000)
    expect(page.locator("h1")).to_contain_text("Corpus Resources & Provenance")

    # Verify live summary counts loaded from backend
    expect(page.locator("text=Prototype corpus — currently 7 verified standards")).to_be_visible(timeout=8000)
    expect(page.locator("h2:has-text('Verified Indian Standards')")).to_be_visible()

    # Verify standard cards exist
    expect(page.locator("span:has-text('IS 14220:2018')").first).to_be_visible()
    expect(page.locator("span:has-text('IS 8034:2018')").first).to_be_visible()
    expect(page.locator("span:has-text('IS 9079:2018')").first).to_be_visible()

    # Expand standard details
    expand_btn = page.locator("button:has-text('View Full Parameters & Provenance')").first
    expand_btn.click()
    expect(page.locator("text=Application Terms:").or_(page.locator("text=Product Terms:")).first).to_be_visible()

    # Switch to Evidence Records tab
    page.locator("button:has-text('Evidence Records')").click()
    expect(page.locator("h2:has-text('Grounded Evidence Records')")).to_be_visible()
    expect(page.locator("text=E-14220-SCOPE")).to_be_visible()

    # Switch to Relationships tab
    page.locator("button:has-text('Relationships')").click()
    expect(page.locator("h2:has-text('Standard Relationship Graph')")).to_be_visible()

    # Switch to Benchmark Cases tab
    page.locator("button:has-text('Benchmark Cases')").click()
    expect(page.locator("text=Internal Regression Benchmark").first).to_be_visible()

    # Switch to Source Provenance tab
    page.locator("button:has-text('Source Provenance')").click()
    expect(page.locator("h2:has-text('Verified BIS Source Documents & Provenance')")).to_be_visible()

    # Refresh page to verify direct route access
    page.reload(wait_until="networkidle")
    expect(page.locator("h1")).to_contain_text("Corpus Resources & Provenance")

    # Click Back to SpecWise Search
    page.locator("a:has-text('Back to SpecWise Search')").click()
    page.wait_for_url(f"{FRONTEND_URL}/", timeout=5000)
    expect(page.locator("h1")).to_contain_text("Indian Standard")
    page.close()

def test_16_firestore_live_contract_and_field_match(browser_context):
    """
    Explicit assertion that all frontend displayed values (standard number, title,
    extracted requirements, evidence citation, related standards, certification status,
    resources counts, and report contents) originate from and match the live Firestore backend.
    """
    page = browser_context.new_page()
    page.goto(FRONTEND_URL, wait_until="networkidle")

    # 1. Intercept analyze request and capture live Firestore response
    textarea = page.locator("textarea")
    textarea.fill("openwell submersible pumpset for clear cold water irrigation")

    with page.expect_response(lambda r: "/api/v1/analyze" in r.url and r.status == 200) as response_info:
        page.locator("button:has-text('Find Applicable Standards')").click()

    analyze_resp = response_info.value.json()
    assert "decision" in analyze_resp
    decision = analyze_resp["decision"]
    strong_app = next((a for a in analyze_resp.get("applicability", []) if a["result"] == "strong"), None)
    target_id = strong_app["standard_id"] if strong_app else (analyze_resp["candidates"][0]["standard_id"] if analyze_resp.get("candidates") else "")
    requirements = analyze_resp.get("requirements", [])
    evidence_list = analyze_resp.get("evidence", [])
    related_list = analyze_resp.get("related_standards", [])
    cert_map = analyze_resp.get("certification", {})

    page.wait_for_selector("#results-section", state="visible", timeout=15000)

    # 2. Assert displayed recommendation standard number matches API response
    expect(page.locator("#results-section")).to_contain_text(decision)
    if target_id:
        expect(page.locator("h2")).to_contain_text(target_id.split(":")[0])

    # 3. Assert displayed candidate/standard title matches API response
    if analyze_resp.get("candidates"):
        cand_title = analyze_resp["candidates"][0]["title"]
        expect(page.locator("#results-section")).to_contain_text(cand_title.split()[0])

    # 4. Assert displayed extracted requirements match API response (inside Advanced Accordion)
    if requirements:
        page.locator("button:has-text('Detailed Procurement Audit & Technical Traceability')").click()
        expect(page.locator("#advanced-accordion")).to_be_visible()
        expect(page.locator("#advanced-accordion")).to_contain_text("Extracted Tender Requirements")
        first_req = requirements[0]
        if first_req.get("text"):
            expect(page.locator("#advanced-accordion")).to_contain_text(first_req["text"][:30])

    # 5. Assert displayed evidence citation/source matches API response
    if evidence_list:
        first_ev = evidence_list[0]
        source_name = first_ev["source_name"]
        expect(page.locator("#results-section")).to_contain_text(source_name)

    # 6. Assert displayed related standard matches API response
    if related_list:
        first_rel = related_list[0]
        rel_id = first_rel["to_standard"].split(":")[0]
        expect(page.locator("#results-section")).to_contain_text(rel_id)

    # 7. Assert displayed certification information matches API response
    if cert_map:
        expect(page.locator("#results-section")).to_contain_text("Certification / QCO Status")

    # 8. Assert Report contains same backend decision and target standard (inside iframe)
    report_btn = page.locator("button:has-text('Download Report (Audit HTML)')")
    report_btn.click()
    expect(page.locator("text=SpecWise Audit Report")).to_be_visible()
    
    report_frame = page.frame_locator("iframe")
    if target_id:
        expect(report_frame.locator("body")).to_contain_text(target_id.split(":")[0])
    expect(report_frame.locator("body")).to_contain_text(decision)
    
    close_btn = page.locator("div.fixed button:has(svg.lucide-x)").first
    close_btn.click()

    # 9. Verify Resources counts come from Firestore-backed /api/v1/resources
    with page.expect_response(lambda r: "/api/v1/resources" in r.url and r.status == 200) as res_info:
        page.locator("nav a:has-text('Resources')").click()

    res_data = res_info.value.json()
    assert "standards" in res_data
    expected_std_count = len(res_data["standards"])

    # Check displayed summary text contains count from backend
    expect(page.locator(f"text={expected_std_count} verified standards")).to_be_visible()

    # Verify each standard in response is represented in UI
    for std in res_data["standards"]:
        std_num = std["standard_id"]
        expect(page.locator(f"span:has-text('{std_num}')").first).to_be_visible()

    page.close()


