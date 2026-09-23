from html import escape

# ── Helpers ───────────────────────────────────────────────────────────────────

def _section(title: str, content: str, anchor: str = "") -> str:
    id_attr = f' id="{escape(anchor)}"' if anchor else ""
    return f'<h2{id_attr}>{escape(title)}</h2>\n{content}\n'


def _table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "<p><em>None.</em></p>"
    ths = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f"<table><tr>{ths}</tr>{body}</table>"


def _badge(text: str, color: str) -> str:
    return (
        f'<span style="display:inline-block;padding:2px 8px;border-radius:3px;'
        f'background:{color};color:#fff;font-size:.8em;font-weight:bold">'
        f'{escape(text)}</span>'
    )


_DECISION_COLOR = {
    "RECOMMEND": "#1a7a1a",
    "REVIEW": "#7a5a00",
    "ABSTAIN": "#555",
    "OUT_OF_CORPUS": "#7a1a1a",
}

_APPL_COLOR = {
    "strong": "#1a7a1a",
    "possible": "#7a5a00",
    "weak": "#999",
    "unknown": "#aaa",
}

_LC_COLOR = {
    "supported": "#1a7a1a",
    "warning": "#c05000",
    "unknown": "#999",
}

_CERT_RESTRICTED = "SOURCE ACCESS RESTRICTED — DETAILS NOT VERIFIED"
_CERT_NOT_IN_KB  = "NOT VERIFIED IN CURRENT KNOWLEDGE BASE"


# ── Primary candidate detail block ────────────────────────────────────────────

def _primary_candidate_block(
    cand, appl_map, lc_map, cert_map, ev_index, by_id
) -> str:
    sid = cand.standard_id
    std = by_id.get(sid)
    appl = appl_map.get(sid)
    lc = lc_map.get(sid)
    cert = cert_map.get(sid)

    appl_result = appl.result if appl else "unknown"
    appl_color = _APPL_COLOR.get(appl_result, "#aaa")
    appl_reasons = "; ".join(appl.reasons[:3]) if appl else "—"

    lc_state = lc.state if lc else "unknown"
    lc_color = _LC_COLOR.get(lc_state, "#aaa")
    lc_notes = "; ".join(lc.reasons[:2]) if lc else "—"

    paths_str = escape(", ".join(cand.retrieval_paths) or "—")
    rrf_str = f"{cand.rrf_score:.6f}"

    # Certification
    if cert is None:
        cert_html = f'<em>{escape(_CERT_NOT_IN_KB)}</em>'
    elif cert.state == "not_verified_in_prototype_corpus":
        cert_html = f'<em>{escape(_CERT_RESTRICTED)}</em>'
    elif cert.state == "verified":
        rule = escape(cert.rule_type or "—")
        eff = escape(str(cert.effective_date) if cert.effective_date else "—")
        desc = escape(cert.description or "—")
        cert_html = f"Verified | Rule: {rule} | Effective: {eff}<br><small>{desc}</small>"
    else:
        cert_html = f'<em>{escape(_CERT_RESTRICTED)}</em>'

    # Evidence for this standard
    ev_ids = appl.evidence_ids if appl else (std.evidence_ids if std else [])
    ev_links = []
    for eid in sorted(set(ev_ids)):
        ev = ev_index.get(eid)
        if ev:
            ev_links.append(
                f'<a href="{escape(ev.url)}" target="_blank">{escape(ev.evidence_id)}</a>'
                f" — {escape(ev.source_name)}"
            )
    ev_html = "<ul>" + "".join(f"<li>{x}</li>" for x in ev_links) + "</ul>" if ev_links else "<p><em>No evidence loaded.</em></p>"

    return f"""
<div class="candidate-block">
  <h3>{escape(sid)} — {escape(cand.title)}</h3>
  <table class="detail-table">
    <tr><th>Applicability</th><td>{_badge(appl_result, appl_color)} {escape(appl_reasons)}</td></tr>
    <tr><th>Lifecycle</th><td>{_badge(lc_state, lc_color)} {escape(lc_notes)}</td></tr>
    <tr><th>Retrieval Paths</th><td>{paths_str} (RRF {rrf_str})</td></tr>
    <tr><th>Certification / QCO</th><td>{cert_html}</td></tr>
  </table>
  <p><strong>Evidence:</strong></p>{ev_html}
</div>"""


# ── Main builder ──────────────────────────────────────────────────────────────

def build_html(result, by_id: dict = None) -> str:
    """
    Build the evidence-traceable HTML report.

    Separates candidates into:
      - Primary Product Standards (PRIMARY_PRODUCT_STANDARD role)
      - Related / Code of Practice Standards (all other roles)
    """
    by_id = by_id or {}

    # ── Index maps for O(1) lookup ─────────────────────────────────────────────
    appl_map  = {a.standard_id: a for a in result.applicability}
    lc_map    = {l.standard_id: l for l in result.lifecycle}
    cert_map  = result.certification
    ev_index  = {e.evidence_id: e for e in result.evidence}

    # ── Split candidates by role ───────────────────────────────────────────────
    primary_cands = []
    related_cands = []
    for c in result.candidates:
        std = by_id.get(c.standard_id)
        role = getattr(std, "standard_role", "PRIMARY_PRODUCT_STANDARD") if std else "PRIMARY_PRODUCT_STANDARD"
        if role == "PRIMARY_PRODUCT_STANDARD":
            primary_cands.append(c)
        else:
            related_cands.append((c, role))

    # ── Decision ──────────────────────────────────────────────────────────────
    d_color = _DECISION_COLOR.get(result.decision, "#333")
    decision_html = (
        f'<p><strong style="color:{d_color};font-size:1.3em">{escape(result.decision)}</strong></p>'
        f'<ul>{"".join(f"<li>{escape(r)}</li>" for r in result.decision_reasons)}</ul>'
    )

    # ── Requirements ──────────────────────────────────────────────────────────
    req_rows = [
        [escape(r.requirement_id), escape(r.category),
         escape(r.extraction_method), f"{r.extraction_confidence:.0%}",
         escape(r.text[:140])]
        for r in result.requirements
    ]
    reqs_html = _table(["ID", "Category", "Method", "Conf", "Text"], req_rows)

    # ── Primary candidates (detailed) ─────────────────────────────────────────
    if primary_cands:
        primary_html = "".join(
            _primary_candidate_block(c, appl_map, lc_map, cert_map, ev_index, by_id)
            for c in primary_cands
        )
    else:
        primary_html = "<p><em>No primary product standards retrieved above the relevance floor.</em></p>"

    # ── Related / CoP candidates (summary table) ───────────────────────────────
    if related_cands:
        rel_cand_rows = []
        for c, role in related_cands:
            appl = appl_map.get(c.standard_id)
            appl_r = appl.result if appl else "unknown"
            cert = cert_map.get(c.standard_id)
            cert_note = (
                _CERT_RESTRICTED if cert and cert.state == "not_verified_in_prototype_corpus"
                else (cert.description or "—") if cert
                else _CERT_NOT_IN_KB
            )
            rel_cand_rows.append([
                escape(c.standard_id),
                escape(c.title),
                escape(role),
                _badge(appl_r, _APPL_COLOR.get(appl_r, "#aaa")),
                escape(", ".join(c.retrieval_paths) or "—"),
                escape(cert_note[:120]),
            ])
        related_cands_html = _table(
            ["Standard", "Title", "Role", "Applicability", "Paths", "Cert / QCO Note"],
            rel_cand_rows
        )
        related_cands_html += (
            "<p><small>Related and code-of-practice standards are retrieved for context. "
            "They are not treated as primary product recommendations.</small></p>"
        )
    else:
        related_cands_html = "<p><em>No related or code-of-practice standards retrieved.</em></p>"

    # ── Coverage matrix ────────────────────────────────────────────────────────
    cov_rows = [
        [escape(x.requirement_id), escape(x.standard_id or "—"),
         escape(x.state), escape(x.reason[:140])]
        for x in result.coverage
    ]
    cov_html = _table(["Requirement", "Standard", "State", "Reason"], cov_rows)

    # ── Gaps ──────────────────────────────────────────────────────────────────
    if result.gaps:
        gap_rows = [
            [escape(g.requirement_id), escape(g.state), escape(g.reason[:140])]
            for g in result.gaps
        ]
        gaps_html = _table(["Requirement", "State", "Reason"], gap_rows)
    else:
        gaps_html = "<p>No coverage gaps detected within the prototype corpus.</p>"

    # ── Conflicts ─────────────────────────────────────────────────────────────
    if result.conflicts:
        conf_rows = [
            [escape(x.conflict_type), escape(x.description[:180])]
            for x in result.conflicts
        ]
        conf_html = _table(["Type", "Description"], conf_rows)
    else:
        conf_html = "<p>No conflicts detected within the prototype corpus.</p>"

    # ── Graph-expanded related standards ──────────────────────────────────────
    if result.related_standards:
        gs_rows = [
            [escape(r.from_standard), escape(r.to_standard),
             escape(r.relationship_type),
             escape(str(r.hop) if r.hop is not None else "—")]
            for r in result.related_standards
        ]
        gs_html = _table(["From", "To", "Relationship", "Hop"], gs_rows)
    else:
        gs_html = "<p>No verified relationship edges in the prototype corpus.</p>"

    # ── Evidence provenance (all) ──────────────────────────────────────────────
    ev_rows = [
        [escape(e.evidence_id),
         escape(e.source_name),
         f'<a href="{escape(e.url)}" target="_blank">source link</a>',
         escape(str(e.page) if e.page else "—"),
         escape(e.text[:160])]
        for e in result.evidence
    ]
    ev_html = _table(["ID", "Source", "URL", "Page", "Excerpt"], ev_rows)

    # ── Timings ───────────────────────────────────────────────────────────────
    timing_rows = [
        [escape(k), f"{v:.1f} ms"]
        for k, v in sorted(result.timings_ms.items())
    ]
    timing_html = _table(["Phase", "Latency"], timing_rows)

    # ── TOC ───────────────────────────────────────────────────────────────────
    toc = """<nav><ul style="list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:8px;font-size:.85em">
<li><a href="#decision">Decision</a></li>
<li><a href="#requirements">Requirements</a></li>
<li><a href="#primary">Primary Standards</a></li>
<li><a href="#related-cands">Related / CoP Standards</a></li>
<li><a href="#coverage">Coverage</a></li>
<li><a href="#gaps">Gaps</a></li>
<li><a href="#conflicts">Conflicts</a></li>
<li><a href="#graph">Graph Expansion</a></li>
<li><a href="#evidence">Evidence</a></li>
<li><a href="#timings">Timings</a></li>
</ul></nav>"""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>SIH26108 Evidence Report — {escape(result.analysis_id)}</title>
<style>
body{{font-family:Arial,sans-serif;margin:32px;color:#222;max-width:1200px}}
h1{{color:#1a3a6a}}
h2{{color:#1a3a6a;border-bottom:2px solid #c8d8e8;padding-bottom:4px;margin-top:2em}}
h3{{color:#2a4a7a;margin-top:1.2em}}
table{{border-collapse:collapse;width:100%;margin-bottom:12px}}
th,td{{border:1px solid #ccc;padding:6px 8px;text-align:left;font-size:.86em;vertical-align:top}}
th{{background:#e8f0f8;font-weight:600}}
.candidate-block{{border:1px solid #c8d8e8;border-radius:4px;padding:14px;margin-bottom:16px;background:#f8fbff}}
.detail-table{{width:100%;margin-bottom:8px}}
.detail-table th{{width:160px;background:#eef3fa}}
.disclaimer{{background:#fff3cd;border:1px solid #ffc107;padding:10px 14px;border-radius:4px;font-size:.85em;margin:12px 0}}
nav{{background:#f0f4f8;padding:10px 14px;border-radius:4px;margin-bottom:16px}}
a{{color:#1a3a6a}}
</style>
</head>
<body>
<h1>SIH26108 Evidence-Traceable Report</h1>
<p><em>Analysis ID: {escape(result.analysis_id)}</em></p>

{toc}

<div class="disclaimer">
⚠ <strong>Prototype Disclaimer:</strong> This report is generated from a curated seed corpus
covering pump-sector Indian Standards only. Where certification or QCO information is not
available in the prototype corpus, it is marked
<em>SOURCE ACCESS RESTRICTED — DETAILS NOT VERIFIED</em> or
<em>NOT VERIFIED IN CURRENT KNOWLEDGE BASE</em>.
This is not a complete BIS catalogue or legal determination and must not be used as the
sole basis for procurement decisions.
</div>

{_section("Decision", decision_html, "decision")}

{_section("Requirements Extracted", reqs_html, "requirements")}

{_section("Primary Product Standards", primary_html, "primary")}

{_section("Related / Code of Practice Standards", related_cands_html, "related-cands")}

{_section("Coverage Matrix", cov_html, "coverage")}

{_section("Coverage Gaps", gaps_html, "gaps")}

{_section("Conflicts", conf_html, "conflicts")}

{_section("Graph-Expanded Related Standards", gs_html, "graph")}

{_section("Evidence Provenance", ev_html, "evidence")}

{_section("Phase Timings", timing_html, "timings")}

<p style="margin-top:2em;font-size:.8em;color:#888">
Input: <em>{escape(result.input_text[:300])}</em>
</p>
</body>
</html>"""
