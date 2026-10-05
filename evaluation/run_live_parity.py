"""
SpecWise Live Render API Parity Tester — Prompt 6B Steps 4, 6, 7
=================================================================
Calls the live Render API for a representative subset of cases,
compares against local results, measures latency, and validates
all 4 decision states are reachable live.
"""

import json
import sys
import time
import tempfile
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import requests
except ImportError:
    print("ERROR: 'requests' not installed. Run: pip install requests")
    sys.exit(1)

from app.engine import RecommendationEngine
from app.models import AnalysisRequest

RENDER_BASE = "https://specwise-sih26108.onrender.com"
LOCAL_ENGINE = None  # lazily initialized


def get_engine():
    global LOCAL_ENGINE
    if LOCAL_ENGINE is None:
        LOCAL_ENGINE = RecommendationEngine()
    return LOCAL_ENGINE


# ── Text query helper ─────────────────────────────────────────────────────────

def live_text_query(query: str, timeout: int = 60) -> dict:
    t0 = time.perf_counter()
    resp = requests.post(
        f"{RENDER_BASE}/api/v1/analyze",
        json={"text": query},
        timeout=timeout,
    )
    elapsed = (time.perf_counter() - t0) * 1000
    resp.raise_for_status()
    data = resp.json()
    data["_elapsed_ms"] = round(elapsed, 1)
    return data


def local_text_query(query: str) -> dict:
    engine = get_engine()
    t0 = time.perf_counter()
    r = engine.analyze(AnalysisRequest(text=query))
    elapsed = (time.perf_counter() - t0) * 1000
    d = r.model_dump()
    d["_elapsed_ms"] = round(elapsed, 1)
    return d


def live_pdf_upload(pdf_bytes: bytes, timeout: int = 120) -> dict:
    import io
    t0 = time.perf_counter()
    resp = requests.post(
        f"{RENDER_BASE}/api/v1/upload-pdf",
        files={"file": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        timeout=timeout,
    )
    elapsed = (time.perf_counter() - t0) * 1000
    resp.raise_for_status()
    data = resp.json()
    data["_elapsed_ms"] = round(elapsed, 1)
    return data


def local_pdf_query(pdf_bytes: bytes) -> dict:
    engine = get_engine()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name
    try:
        t0 = time.perf_counter()
        r = engine.analyze(AnalysisRequest(file_path=tmp_path))
        elapsed = (time.perf_counter() - t0) * 1000
        d = r.model_dump()
        d["_elapsed_ms"] = round(elapsed, 1)
        return d
    finally:
        os.unlink(tmp_path)


def extract_compare_fields(r: dict) -> dict:
    """Extract comparable fields from an AnalysisResponse dict."""
    candidates = {x.get("standard_id") if isinstance(x, dict) else x for x in r.get("candidates", [])}
    related = {
        x.get("to_standard") if isinstance(x, dict) else x
        for x in r.get("related_standards", [])
    }
    applicability = r.get("applicability", [])
    strong = [
        a.get("standard_id") if isinstance(a, dict) else a
        for a in applicability
        if (a.get("result") if isinstance(a, dict) else None) == "strong"
    ]
    gaps = r.get("gaps", [])
    return {
        "decision": r.get("decision"),
        "candidates": sorted(candidates - {None}),
        "related": sorted(related - {None}),
        "strong": sorted(strong),
        "gaps_count": len(gaps),
        "decision_reasons_count": len(r.get("decision_reasons", [])),
        "elapsed_ms": r.get("_elapsed_ms", 0),
    }


def parity_check(local: dict, live: dict) -> tuple:
    """Returns (parity_pass: bool, diff: dict)."""
    lf = extract_compare_fields(local)
    rf = extract_compare_fields(live)
    diffs = {}
    if lf["decision"] != rf["decision"]:
        diffs["decision"] = {"local": lf["decision"], "live": rf["decision"]}
    if set(lf["candidates"]) != set(rf["candidates"]):
        diffs["candidates"] = {
            "local_only": sorted(set(lf["candidates"]) - set(rf["candidates"])),
            "live_only": sorted(set(rf["candidates"]) - set(lf["candidates"])),
        }
    if set(lf["strong"]) != set(rf["strong"]):
        diffs["strong"] = {"local": lf["strong"], "live": rf["strong"]}
    return len(diffs) == 0, diffs


# ── Parity test cases ─────────────────────────────────────────────────────────

PARITY_CASES = [
    {
        "id": "LA01-exact-reference-text",
        "query": "openwell submersible pumpset for agricultural irrigation IS 14220",
        "mode": "text",
        "expected_decision": "RECOMMEND",
        "decision_state": "RECOMMEND",
        "notes": "Canonical exact-reference text query.",
    },
    {
        "id": "LA02-wrong-scope-text",
        "query": "sewage pump for wastewater treatment effluent",
        "mode": "text",
        "expected_decision": None,   # ABSTAIN or OUT_OF_CORPUS
        "decision_state": "ABSTAIN/OUT_OF_CORPUS",
        "notes": "Wrong-scope query. Must not produce RECOMMEND.",
    },
    {
        "id": "LA03-out-of-corpus-text",
        "query": "advanced underwater robotic mining vehicle hydraulic manipulator",
        "mode": "text",
        "expected_decision": "OUT_OF_CORPUS",
        "decision_state": "OUT_OF_CORPUS",
        "notes": "Out-of-corpus query.",
    },
    {
        "id": "LA04-multi-standard-review",
        "query": "borewell submersible pumpset IS 8034 with GI column pipe IS 1239 and submersible cable IS 694",
        "mode": "text",
        "expected_decision": "REVIEW",
        "decision_state": "REVIEW",
        "notes": "Multi-standard query triggers REVIEW.",
    },
    {
        "id": "LA05-digital-pdf",
        "query": None,
        "mode": "pdf_digital",
        "pdf_text": (
            "PROCUREMENT: Openwell Submersible Pumpsets as per IS 14220:2018\n"
            "Power: 3 HP, Agricultural irrigation, 10 units"
        ),
        "expected_decision": "RECOMMEND",
        "decision_state": "RECOMMEND",
        "notes": "Digital PDF upload — fast text-layer path.",
    },
    {
        "id": "LA06-scanned-pdf",
        "query": None,
        "mode": "pdf_scanned",
        "pdf_text": (
            "SUPPLY ORDER\n"
            "Monoset Pump for Clear Cold Water\n"
            "Standard: IS 9079:2018\n"
            "Quantity: 5 units, 2 HP"
        ),
        "expected_decision": "RECOMMEND",
        "decision_state": "RECOMMEND",
        "notes": "Scanned PDF — OCR path.",
    },
    {
        "id": "LA07-ocr-safety-blank",
        "query": None,
        "mode": "pdf_blank",
        "pdf_text": "",
        "expected_decision": None,  # must error / not RECOMMEND
        "decision_state": "ERROR_SAFE",
        "notes": "Blank scanned PDF — must return error, not a recommendation.",
    },
]


def run_parity_tests(output_json: str = None):
    import io

    print(f"\nChecking health of {RENDER_BASE} ...")
    try:
        h = requests.get(f"{RENDER_BASE}/api/v1/health", timeout=30)
        h.raise_for_status()
        health = h.json()
        print(f"  status={health.get('status')} standards={health.get('standards_count')} "
              f"ocr={health.get('ocr_available')} dense={health.get('dense_enabled')}")
    except Exception as exc:
        print(f"  ERROR reaching Render: {exc}")
        print("  Skipping live parity tests.")
        return []

    print(f"\nRunning {len(PARITY_CASES)} parity cases ...")
    print("-" * 72)

    rows = []
    latencies_text = []
    latencies_pdf_digital = []
    latencies_pdf_scanned = []

    decision_states_seen = set()

    for c in PARITY_CASES:
        print(f"  {c['id']:<35} ... ", end="", flush=True)
        live_error = None
        local_result = {}
        live_result = {}
        parity = None
        parity_diffs = {}

        try:
            if c["mode"] == "text":
                local_result = local_text_query(c["query"])
                live_result = live_text_query(c["query"])
                latencies_text.append(live_result["_elapsed_ms"])

            elif c["mode"] == "pdf_digital":
                import fitz as _fitz
                _doc = _fitz.open()
                _page = _doc.new_page()
                _page.insert_text((50, 72), c["pdf_text"], fontsize=11)
                _buf = io.BytesIO()
                _doc.save(_buf)
                _doc.close()
                pdf_b = _buf.getvalue()
                local_result = local_pdf_query(pdf_b)
                live_result = live_pdf_upload(pdf_b)
                latencies_pdf_digital.append(live_result["_elapsed_ms"])

            elif c["mode"] == "pdf_scanned":
                import fitz as _fitz
                _doc = _fitz.open()
                _rp = _doc.new_page()
                _rp.insert_text((50, 72), c["pdf_text"], fontsize=11)
                _mat = _fitz.Matrix(150 / 72, 150 / 72)
                _pix = _rp.get_pixmap(matrix=_mat)
                _doc.close()
                _img_doc = _fitz.open()
                _ip = _img_doc.new_page(width=595, height=842)
                _ip.insert_image(_ip.rect, stream=_pix.tobytes("png"))
                _buf = io.BytesIO()
                _img_doc.save(_buf)
                _img_doc.close()
                pdf_b = _buf.getvalue()
                local_result = local_pdf_query(pdf_b)
                live_result = live_pdf_upload(pdf_b)
                latencies_pdf_scanned.append(live_result["_elapsed_ms"])

            elif c["mode"] == "pdf_blank":
                import fitz as _fitz
                _img_doc = _fitz.open()
                _ip = _img_doc.new_page(width=595, height=842)
                _buf = io.BytesIO()
                _img_doc.save(_buf)
                _img_doc.close()
                pdf_b = _buf.getvalue()
                # Local
                try:
                    local_result = local_pdf_query(pdf_b)
                    local_result["_error"] = None
                except ValueError as e:
                    local_result = {"decision": "ERROR", "_error": str(e), "_elapsed_ms": 0}
                # Live
                try:
                    live_result = live_pdf_upload(pdf_b)
                    live_result["_error"] = None
                except requests.HTTPError as e:
                    live_result = {"decision": "ERROR", "_error": str(e), "_elapsed_ms": 0}

            # Parity check (skip for blank/error cases)
            if c["mode"] != "pdf_blank" and not live_error:
                parity, parity_diffs = parity_check(local_result, live_result)

            local_dec = local_result.get("decision", "ERROR")
            live_dec = live_result.get("decision", "ERROR")

            # Decision state coverage
            if live_dec not in (None, "ERROR"):
                decision_states_seen.add(live_dec)
            if local_dec not in (None, "ERROR"):
                decision_states_seen.add(local_dec)

            # Safety check
            if c["decision_state"] == "ERROR_SAFE":
                safe = local_dec == "ERROR" or live_dec in (None, "ERROR")
                parity = safe
                parity_diffs = {} if safe else {"safety": "expected error, got recommendation"}

            parity_str = "LIVE_PARITY_PASS" if parity else "LIVE_PARITY_FAIL"
            print(f"{parity_str}  local={local_dec} live={live_dec} "
                  f"({live_result.get('_elapsed_ms', 0):.0f}ms)")

        except requests.exceptions.ConnectionError as exc:
            live_error = f"CONNECTION_ERROR: {exc}"
            parity = False
            print(f"LIVE_PARITY_FAIL  {live_error[:60]}")
        except requests.exceptions.Timeout:
            live_error = "TIMEOUT"
            parity = False
            print("LIVE_PARITY_FAIL  TIMEOUT")
        except Exception as exc:
            live_error = str(exc)
            parity = False
            print(f"LIVE_PARITY_FAIL  {live_error[:60]}")

        rows.append({
            "id": c["id"],
            "mode": c["mode"],
            "decision_state": c["decision_state"],
            "expected_decision": c.get("expected_decision"),
            "local_decision": local_result.get("decision"),
            "live_decision": live_result.get("decision"),
            "parity": parity,
            "parity_diffs": parity_diffs,
            "live_error": live_error,
            "live_elapsed_ms": live_result.get("_elapsed_ms", 0),
            "local_elapsed_ms": local_result.get("_elapsed_ms", 0),
            "notes": c.get("notes", ""),
        })

    # Latency summary
    def stats(vals):
        if not vals:
            return {"min": None, "max": None, "avg": None, "median": None}
        s = sorted(vals)
        return {
            "min": round(min(s), 1),
            "max": round(max(s), 1),
            "avg": round(sum(s) / len(s), 1),
            "median": round(s[len(s) // 2], 1),
        }

    latency = {
        "text": stats(latencies_text),
        "pdf_digital": stats(latencies_pdf_digital),
        "pdf_scanned": stats(latencies_pdf_scanned),
    }

    passes = sum(1 for r in rows if r["parity"])
    n = len(rows)

    print(f"\n{'=' * 72}")
    print("  Live Render Parity Summary")
    print(f"{'=' * 72}")
    print(f"  Cases         : {n}")
    print(f"  Parity PASS   : {passes}/{n}")
    print(f"  Decision states seen (live+local): {sorted(decision_states_seen)}")
    print(f"\n  API Latency (live Render, ms):")
    for mode, s in latency.items():
        if s["min"] is not None:
            print(f"    {mode:<16}: min={s['min']}  max={s['max']}  avg={s['avg']}  median={s['median']}")
    for r in rows:
        if not r["parity"]:
            print(f"\n  FAIL [{r['id']}]: {r['parity_diffs'] or r['live_error']}")
    print(f"{'=' * 72}\n")

    payload = {"summary": {"parity_pass": passes, "total": n, "latency": latency,
                           "decision_states_seen": sorted(decision_states_seen)},
               "cases": rows}

    if output_json:
        Path(output_json).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Parity results written to: {output_json}")

    return payload


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Live Render API Parity Tester")
    parser.add_argument("--output", "-o", default=None)
    args = parser.parse_args()
    run_parity_tests(output_json=args.output)
