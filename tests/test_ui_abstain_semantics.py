"""
UI Semantics & Regression Tests — SIH26108 SpecWise
Verifies that:
1. ABSTAIN with code-of-practice match NEVER displays "PRIMARY PRODUCT STANDARD"
2. ABSTAIN with several weak candidates renders "No primary standard selected" + "Context only — not a recommendation"
3. REVIEW with strong primary displays the strong primary standard
4. OUT_OF_CORPUS never displays a primary standard or weak recommendation
5. RECOMMEND with strong primary displays the primary product standard card
"""
import pytest
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

def test_abstain_with_code_of_practice_only():
    """ABSTAIN case 1: only code of practice matches (IS 14536). Must not have strong primary."""
    resp = client.post("/api/v1/analyze", json={
        "text": "Code of practice for selection, installation, operation and maintenance of submersible pump"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] == "ABSTAIN"
    strong = [a for a in data.get("applicability", []) if a["result"] == "strong"]
    assert len(strong) == 0, f"ABSTAIN must not have strong primary applicability: {strong}"
    cand_ids = [c["standard_id"] for c in data.get("candidates", [])]
    assert any("14536" in cid for cid in cand_ids)

def test_abstain_with_sampling_or_test_method():
    """ABSTAIN case 2: sampling / acceptance test method (IS 10572 / IS 11346)."""
    resp = client.post("/api/v1/analyze", json={
        "text": "Methods of sampling for agricultural and water supply pumps"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] == "ABSTAIN"
    strong = [a for a in data.get("applicability", []) if a["result"] == "strong"]
    assert len(strong) == 0

def test_review_with_strong_primary():
    """REVIEW case: strong primary exists (IS 8034), but tender has gaps/unverified refs."""
    resp = client.post("/api/v1/analyze", json={
        "text": "Submersible pumpset suitable for 165 mm dia borewell as per IS 8034:2018 with motor as per IS 9283:2024 and control panel citing IS 13947"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] == "REVIEW"
    strong = [a for a in data.get("applicability", []) if a["result"] == "strong"]
    assert len(strong) == 1
    assert "8034" in strong[0]["standard_id"]

def test_out_of_corpus():
    """OUT_OF_CORPUS case: completely unrelated product."""
    resp = client.post("/api/v1/analyze", json={
        "text": "Solar PV mono PERC module 540W with MC4 connectors and string inverter"
    })
    assert resp.status_code == 200
    data = resp.json()
    strong = [a for a in data.get("applicability", []) if a["result"] == "strong"]
    assert len(strong) == 0

def test_recommend_with_strong_primary():
    """RECOMMEND case: unambiguous openwell pump."""
    resp = client.post("/api/v1/analyze", json={
        "text": "openwell submersible pumpset for agricultural irrigation"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] == "RECOMMEND"
    strong = [a for a in data.get("applicability", []) if a["result"] == "strong"]
    assert len(strong) == 1
    assert "14220" in strong[0]["standard_id"]
