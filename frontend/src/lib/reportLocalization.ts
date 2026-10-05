import { AnalysisResponse } from "@/types/api";
import { Language, Translations } from "@/context/LanguageContext";

export function generateLocalizedAuditHtml(
  response: AnalysisResponse,
  language: Language,
  t: Translations
): string {
  const strongCandidate = response.applicability?.find((a) => a.result === "strong");
  const primaryId =
    response.decision === "RECOMMEND"
      ? strongCandidate?.standard_id || response.candidates?.[0]?.standard_id || "N/A"
      : "N/A";
  const decision = response.decision || "ABSTAIN";
  const analysisId = response.analysis_id || "N/A";
  const totalMs = response.timings_ms?.total_ms ? `${Math.round(response.timings_ms.total_ms)} ms` : "—";

  const decisionColors: Record<string, { bg: string; text: string }> = {
    RECOMMEND: { bg: "#166534", text: "#ffffff" },
    REVIEW: { bg: "#854d0e", text: "#ffffff" },
    ABSTAIN: { bg: "#475569", text: "#ffffff" },
    OUT_OF_CORPUS: { bg: "#991b1b", text: "#ffffff" },
  };

  const currentDecColor = decisionColors[decision] || { bg: "#475569", text: "#ffffff" };

  const decisionLabel =
    decision === "RECOMMEND"
      ? t.definitiveMatch || "Definitive Match"
      : decision === "REVIEW"
      ? t.reviewRequired || "Technical Review Required"
      : decision === "OUT_OF_CORPUS"
      ? t.outOfCorpus || "Out of Prototype Corpus"
      : t.noPrimary || "Abstain / No Primary Selected";

  const candidates = response.candidates || [];
  const requirements = response.requirements || [];
  const related = response.related_standards || [];

  return `<!DOCTYPE html>
<html lang="${language}">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>SpecWise BIS Audit Report — ${analysisId}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 24px;
      color: #0f172a;
      background: #ffffff;
      line-height: 1.5;
    }
    .header {
      border-bottom: 2px solid #0b57d0;
      padding-bottom: 16px;
      margin-bottom: 24px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }
    .header h1 {
      margin: 0 0 4px 0;
      font-size: 24px;
      color: #0b57d0;
    }
    .header p {
      margin: 0;
      font-size: 13px;
      color: #64748b;
    }
    .badge {
      display: inline-block;
      padding: 6px 14px;
      border-radius: 6px;
      font-weight: 700;
      font-size: 14px;
      letter-spacing: 0.5px;
    }
    .meta-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      background: #f8fafc;
      padding: 16px;
      border-radius: 8px;
      margin-bottom: 24px;
      border: 1px solid #e2e8f0;
    }
    .meta-item {
      font-size: 12px;
    }
    .meta-label {
      color: #64748b;
      font-weight: 600;
      margin-bottom: 2px;
      text-transform: uppercase;
      font-size: 10px;
    }
    .meta-value {
      color: #0f172a;
      font-weight: 600;
    }
    h2 {
      font-size: 16px;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 6px;
      margin-top: 24px;
      margin-bottom: 12px;
      color: #1e293b;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 20px;
      font-size: 12px;
    }
    th, td {
      border: 1px solid #e2e8f0;
      padding: 8px 10px;
      text-align: left;
    }
    th {
      background: #f1f5f9;
      color: #334155;
      font-weight: 600;
    }
    tr:nth-child(even) {
      background: #f8fafc;
    }
    .summary-box {
      background: #eff6ff;
      border-left: 4px solid #0b57d0;
      padding: 14px;
      border-radius: 4px;
      margin-bottom: 20px;
      font-size: 13px;
    }
    .footer {
      margin-top: 36px;
      padding-top: 12px;
      border-top: 1px solid #e2e8f0;
      font-size: 11px;
      color: #94a3b8;
      text-align: center;
    }
    @media print {
      body { padding: 0; }
      .no-print { display: none; }
    }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <h1>SpecWise — ${t.auditReport || "BIS Audit Report"}</h1>
      <p>${t.tagline || "Right Standards. Safer Procurement."} · Bureau of Indian Standards Intelligence</p>
    </div>
    <div>
      <span class="badge" style="background: ${currentDecColor.bg}; color: ${currentDecColor.text};">
        ${decision}: ${decisionLabel}
      </span>
    </div>
  </div>

  <div class="meta-grid">
    <div class="meta-item">
      <div class="meta-label">Analysis ID</div>
      <div class="meta-value font-mono">${analysisId}</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">${t.primaryMatch || "Primary Recommendation"}</div>
      <div class="meta-value">${primaryId}</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">${t.decisionState || "Decision"}</div>
      <div class="meta-value">${decision}</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">${t.language || "Language"}</div>
      <div class="meta-value">${language.toUpperCase()}</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">Latency</div>
      <div class="meta-value">${totalMs}</div>
    </div>
  </div>

  <div class="summary-box">
    <strong>${t.summary || "Summary"}:</strong> ${(response.decision_reasons || []).join("; ") || response.input_text || "—"}
  </div>

  <h2>1. ${t.extractedRequirements || "Extracted Tender Requirements"}</h2>
  ${
    requirements.length > 0
      ? `<table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Category</th>
              <th>Requirement Text</th>
              <th>Method</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            ${requirements
              .map(
                (r) => `<tr>
                  <td style="font-family: monospace; font-weight: bold;">${r.requirement_id}</td>
                  <td>${r.category}</td>
                  <td>${r.text}</td>
                  <td>${r.extraction_method}</td>
                  <td>${Math.round(r.extraction_confidence * 100)}%</td>
                </tr>`
              )
              .join("")}
          </tbody>
        </table>`
      : `<p style="font-size: 12px; color: #64748b;">${t.noRequirementsFound || "No specific requirements extracted."}</p>`
  }

  <h2>2. ${t.candidateStandards || "Candidate Standards Evaluated"}</h2>
  ${
    candidates.length > 0
      ? `<table>
          <thead>
            <tr>
              <th>Standard Number</th>
              <th>Title</th>
              <th>Applicability</th>
              <th>Lifecycle</th>
              <th>Retrieval Paths</th>
            </tr>
          </thead>
          <tbody>
            ${candidates
              .map((c) => {
                const appl = response.applicability?.find((a) => a.standard_id === c.standard_id);
                const lc = response.lifecycle?.find((l) => l.standard_id === c.standard_id);
                const isPrimary = c.standard_id === primaryId;
                return `<tr style="${isPrimary ? "background: #f0fdf4; font-weight: 600;" : ""}">
                  <td>${c.standard_id} ${isPrimary ? "★ (Primary)" : ""}</td>
                  <td>${c.title}</td>
                  <td>${appl ? appl.result.toUpperCase() : "—"}</td>
                  <td>${lc ? lc.state.toUpperCase() : "—"}</td>
                  <td>${(c.retrieval_paths || []).join(", ") || "—"}</td>
                </tr>`;
              })
              .join("")}
          </tbody>
        </table>`
      : `<p style="font-size: 12px; color: #64748b;">${t.noCandidatesFound || "No candidates found."}</p>`
  }

  <h2>3. ${t.normativeReferences || "Normative References & Companion Specifications"}</h2>
  ${
    related.length > 0
      ? `<table>
          <thead>
            <tr>
              <th>From Standard</th>
              <th>To Standard</th>
              <th>Relationship</th>
              <th>Verified</th>
            </tr>
          </thead>
          <tbody>
            ${related
              .map(
                (rel) => `<tr>
                  <td>${rel.from_standard}</td>
                  <td style="font-weight: 600;">${rel.to_standard}</td>
                  <td>${rel.relationship_type.replace(/_/g, " ")}</td>
                  <td>${rel.verified ? "✅ Verified" : "⚠️ Unverified"}</td>
                </tr>`
              )
              .join("")}
          </tbody>
        </table>`
      : `<p style="font-size: 12px; color: #64748b;">${t.noRelatedStandards || "No normative companion standards attached."}</p>`
  }

  <div class="footer">
    <p>SpecWise Decision Engine · Bureau of Indian Standards Grounded Intelligence · ${t.prototypeNotice || "Prototype · Grounded in official BIS committee evidence"}</p>
    <p>Generated on ${new Date().toISOString()} · Analysis ID: ${analysisId}</p>
  </div>
</body>
</html>`;
}
