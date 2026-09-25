import fitz
import pytest
from fastapi.testclient import TestClient
from app.api.main import app
from app.engine import RecommendationEngine
from app.models import AnalysisRequest


GANGA_KALYANA_TEXT = """GOVERNMENT OF KARNATAKA - BACKWARD CLASSES WELFARE DEPARTMENT
SUPPLY, INSTALLATION & COMMISSIONING OF SUBMERSIBLE PUMPS SETS WITH ACCESSORIES SUITABLE FOR 165 MM DIA BOREWELLS.

Technical specifications:
1. Submersible Pumpset: suitable for 165 mm dia borewells, multi-stage centrifugal pump conforming to IS 8034:2018.
2. Submersible Motor: water-filled submersible motor conforming to IS 9283:2024, 3-phase, 415V, 50Hz, 5 HP.
3. Riser Pipes: 50mm GI pipes Class B as per IS 1239 / 90.
4. Submersible Cable: 3-core flat PVC insulated submersible cable as per IS 694-1990.
5. Control Panel: starter panel with switchgear and capacitors conforming to IS 13947 / IS 2834."""


@pytest.fixture
def client():
    return TestClient(app)


def test_text_pdf_tender_equivalence(client):
    """Regression test: identical text and PDF tender inputs yield equivalent routing, primary recommendation, and decisions."""
    # 1. Text Analysis
    res_text = client.post("/api/v1/analyze", json={"text": GANGA_KALYANA_TEXT})
    assert res_text.status_code == 200
    data_text = res_text.json()

    # 2. PDF Analysis
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    y = 40
    for line in GANGA_KALYANA_TEXT.split("\n"):
        page.insert_text((30, y), line, fontsize=8)
        y += 16
    pdf_bytes = doc.tobytes()
    doc.close()

    res_pdf = client.post(
        "/api/v1/upload-pdf",
        files={"file": ("ganga_kalyana.pdf", pdf_bytes, "application/pdf")},
    )
    assert res_pdf.status_code == 200
    data_pdf = res_pdf.json()

    # Invariants
    # IS 13947 and IS 2834 are cited by the tender but NOT in the corpus,
    # so coverage gaps exist → decision is REVIEW, not RECOMMEND.
    assert data_text["decision"] == "REVIEW"
    assert data_pdf["decision"] == "REVIEW"
    assert data_text["decision"] == data_pdf["decision"]

    # Primary strong candidates match
    strong_text = [
        c["standard_id"]
        for c in data_text["candidates"]
        if any(a["standard_id"] == c["standard_id"] and a["result"] == "strong" for a in data_text["applicability"])
    ]
    strong_pdf = [
        c["standard_id"]
        for c in data_pdf["candidates"]
        if any(a["standard_id"] == c["standard_id"] and a["result"] == "strong" for a in data_pdf["applicability"])
    ]
    assert strong_text == ["IS 8034:2018"]
    assert strong_pdf == ["IS 8034:2018"]

    # Related standards match
    assert len(data_text["related_standards"]) == len(data_pdf["related_standards"])
    rel_text_pairs = [(r["from_standard"], r["to_standard"]) for r in data_text["related_standards"]]
    rel_pdf_pairs = [(r["from_standard"], r["to_standard"]) for r in data_pdf["related_standards"]]
    assert rel_text_pairs == rel_pdf_pairs

    # Gaps must exist: IS 13947 and IS 2834 are unverified references
    assert len(data_text["gaps"]) >= 1, "Expected gaps for uncorpus IS 13947/IS 2834 citations"
    gap_states_text = {g["state"] for g in data_text["gaps"]}
    assert "unverified_reference" in gap_states_text, \
        f"Expected unverified_reference gap state; got {gap_states_text}"

    # No hallucinated conflicts (conflict detection is separate from coverage gaps)
    assert data_text["conflicts"] == []
    assert data_pdf["conflicts"] == []



def test_unverified_certification_no_false_legal_claim(client):
    """Regression test: unverified certification state must not assert legal force or say not mandatory without evidence."""
    res = client.post("/api/v1/analyze", json={"text": GANGA_KALYANA_TEXT})
    assert res.status_code == 200
    data = res.json()
    cert = data["certification"]

    for std_id, cert_res in cert.items():
        assert cert_res["state"] == "not_verified_in_prototype_corpus"
        assert "SOURCE ACCESS RESTRICTED" in cert_res["description"]
        # Ensure it does not falsely claim full legal force or dismiss without evidence
        assert "not mandatory" not in cert_res["description"].lower()


def test_primary_vs_related_distinction(client):
    """Regression test: IS 8034:2018 is primary; accessory standards (IS 1239, IS 694, IS 9283) do not become primary."""
    res = client.post("/api/v1/analyze", json={"text": GANGA_KALYANA_TEXT})
    assert res.status_code == 200
    data = res.json()

    appl_map = {a["standard_id"]: a["result"] for a in data["applicability"]}
    assert appl_map["IS 8034:2018"] == "strong"
    assert appl_map.get("IS 1239:1990") == "weak"  # Role ceiling
    assert appl_map.get("IS 694:2010") == "weak"    # Role ceiling
    assert appl_map.get("IS 9283:2024") == "weak"   # Role ceiling
    assert appl_map.get("IS 14536:2018") == "possible"  # Code of practice ceiling


def test_tender_cited_unverified_references(client):
    """Regression test: IS 13947 and IS 2834 are extracted from tender but identified as unverified in prototype corpus."""
    res = client.post("/api/v1/analyze", json={"text": GANGA_KALYANA_TEXT})
    assert res.status_code == 200
    data = res.json()

    extracted_is_refs = [
        r["value"] for r in data["requirements"] if r["category"] == "reference"
    ]
    assert any("13947" in ref for ref in extracted_is_refs)
    assert any("2834" in ref for ref in extracted_is_refs)

    # These standards must NOT be present in candidate list since they are not in corpus
    candidate_ids = [c["standard_id"] for c in data["candidates"]]
    assert not any("13947" in cid for cid in candidate_ids)
    assert not any("2834" in cid for cid in candidate_ids)

    # Must generate unverified_reference gaps
    unverified_gaps = [g for g in data["gaps"] if g["state"] == "unverified_reference"]
    assert len(unverified_gaps) >= 2
    assert any("13947" in g["reason"] for g in unverified_gaps)
    assert any("2834" in g["reason"] for g in unverified_gaps)


def test_edition_mismatch_and_currentness_handling(client):
    """Regression test: IS 694:1990 cited in tender vs IS 694:2010 in corpus produces edition_mismatch gap."""
    res = client.post("/api/v1/analyze", json={"text": GANGA_KALYANA_TEXT})
    assert res.status_code == 200
    data = res.json()

    mismatch_gaps = [g for g in data["gaps"] if g["state"] == "edition_mismatch"]
    assert len(mismatch_gaps) >= 1
    cable_gap = next((g for g in mismatch_gaps if "694" in (g["standard_id"] or "") or "694" in g["reason"]), None)
    assert cable_gap is not None
    assert "IS 694:2010" in cable_gap["standard_id"]
    assert "IS 694:1990" in cable_gap["reason"]
    assert "current edition" in cable_gap["reason"]

    # Decision reasons must explicitly describe edition mismatch
    assert any("edition mismatch" in r.lower() or "currentness" in r.lower() for r in data["decision_reasons"])


def test_decision_gate_cases_a_through_e(client):
    """
    Regression test covering Decision Gate Scenarios A through E:
    A. Strong primary + all requirements covered -> RECOMMEND
    B. Strong primary + unverified tender reference -> REVIEW
    C. Strong primary + historical/current edition mismatch -> REVIEW
    D. Completely unsupported requirement -> OUT_OF_CORPUS or ABSTAIN
    E. Multiple plausible strong standards -> REVIEW
    """
    # Case A: Strong primary + fully covered requirements
    res_a = client.post("/api/v1/analyze", json={
        "text": "openwell submersible pumpset for agricultural irrigation"
    })
    assert res_a.status_code == 200
    data_a = res_a.json()
    assert data_a["decision"] == "RECOMMEND"
    assert data_a["candidates"][0]["standard_id"] == "IS 14220:2018"

    # Case B: Strong primary + unverified tender reference (e.g. IS 99999)
    res_b = client.post("/api/v1/analyze", json={
        "text": "openwell submersible pumpset for agricultural irrigation as per IS 99999."
    })
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert data_b["decision"] == "REVIEW"
    assert any(g["state"] == "unverified_reference" for g in data_b["gaps"])
    assert any("IS 99999" in r for r in data_b["decision_reasons"])

    # Case C: Strong primary + historical/current edition mismatch
    res_c = client.post("/api/v1/analyze", json={
        "text": "submersible pumpset for borewell agricultural irrigation as per IS 8034:2002 and PVC cable as per IS 694-1990."
    })
    assert res_c.status_code == 200
    data_c = res_c.json()
    assert data_c["decision"] == "REVIEW"
    assert any(g["state"] == "edition_mismatch" for g in data_c["gaps"])

    # Case D: Completely unsupported requirement / out of corpus
    res_d = client.post("/api/v1/analyze", json={
        "text": "quantum computing post-quantum encryption key distribution algorithm"
    })
    assert res_d.status_code == 200
    data_d = res_d.json()
    assert data_d["decision"] == "OUT_OF_CORPUS"

    # Case E: Multiple plausible strong standards (ambiguous pump)
    res_e = client.post("/api/v1/analyze", json={
        "text": "pumpset"
    })
    assert res_e.status_code == 200
    data_e = res_e.json()
    assert data_e["decision"] in {"REVIEW", "ABSTAIN"}


def test_no_fabricated_standard_or_relationship(client):
    """Regression test: Unverified citations never fabricate standard records or relationship edges."""
    res = client.post("/api/v1/analyze", json={
        "text": "supply of special pump conforming to IS 99991 and starter panel as per IS 99992."
    })
    assert res.status_code == 200
    data = res.json()

    # Standards list must not contain fabricated IDs
    cands = [c["standard_id"] for c in data["candidates"]]
    assert "IS 99991" not in cands
    assert "IS 99992" not in cands

    # Related standards graph must not contain fabricated IDs
    for rel in data["related_standards"]:
        assert "99991" not in rel["from_standard"] and "99991" not in rel["to_standard"]
        assert "99992" not in rel["from_standard"] and "99992" not in rel["to_standard"]


def test_evidence_vs_source_separation(client):
    """Regression test: Sources and Evidence remain strictly distinct data models."""
    res = client.get("/api/v1/resources")
    assert res.status_code == 200
    data = res.json()

    sources = data["sources"]
    evidence = data["evidence"]

    # Check sources structure
    for s in sources:
        assert "source_id" in s
        assert "name" in s
        assert "url" in s
        assert "publisher" in s
        assert "source_type" in s

    # Check evidence structure
    for e in evidence:
        assert "evidence_id" in e
        assert "source_id" in e
        assert "text" in e
        assert "verified" in e
        # Evidence must link to a valid source_id
        source_ids = {s["source_id"] for s in sources}
        assert e["source_id"] in source_ids
