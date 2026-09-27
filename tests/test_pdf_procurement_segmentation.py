import fitz
import pytest
from fastapi.testclient import TestClient

from app.api.main import app


def _pdf(tmp_path, name, text):
    path = tmp_path / name
    document = fitz.open()
    page = document.new_page()
    page.insert_textbox(fitz.Rect(40, 40, 550, 800), text, fontsize=10)
    document.save(path)
    document.close()
    return path


@pytest.mark.parametrize(("name", "text", "decision"), [
    ("mixed-pump-solar.pdf", "Supply package: (a) borewell submersible pumpset; (b) solar PV modules; (c) MPPT inverter; (d) mounting structure.", "REVIEW"),
    ("pump-cable-pipe.pdf", "Supply package: (a) borewell submersible pumpset; (b) submersible cable; (c) GI rising pipe.", "REVIEW"),
    ("openwell-accessories.pdf", "Supply openwell submersible pumpset for irrigation, complete with accessories.", "RECOMMEND"),
    ("single-pump-attributes.pdf", "Supply borewell submersible pumpset, 5 HP, 415 V, 3 phase, 24 m head, 12 L/s discharge, cast iron casing.", "RECOMMEND"),
    ("long-numbered.pdf", "TITLE: Water supply tender\nEligibility: bidder details\n1. borewell submersible pumpset\n2. solar PV modules\n3. inverter\nWarranty: two years", "REVIEW"),
    ("mixed-unrelated.pdf", "Supply package: (a) laboratory centrifuge; (b) UPS; (c) computer workstation.", "OUT_OF_CORPUS"),
])
def test_pdf_upload_preserves_procurement_item_boundaries(tmp_path, name, text, decision):
    path = _pdf(tmp_path, name, text)
    with TestClient(app) as client, path.open("rb") as handle:
        response = client.post("/api/v1/upload-pdf", files={"file": (name, handle, "application/pdf")})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["decision"] == decision
    if decision == "REVIEW":
        assert any(entry["state"] == "not_covered" for entry in body["gaps"])

