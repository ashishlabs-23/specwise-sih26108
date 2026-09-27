export type Decision = "RECOMMEND" | "REVIEW" | "ABSTAIN" | "OUT_OF_CORPUS";

export type StandardRole =
  | "PRIMARY_PRODUCT_STANDARD"
  | "CODE_OF_PRACTICE"
  | "TEST_METHOD"
  | "RELATED_STANDARD";

export interface Evidence {
  evidence_id: string;
  source_id: string;
  source_name: string;
  url: string;
  page?: number | null;
  section?: string | null;
  text: string;
  verified: boolean;
  requirement_ids: string[];
  candidate_standard_id?: string | null;
  evidence_scope: "supporting" | "context_only";
  inclusion_reason?: string | null;
}

export interface Requirement {
  requirement_id: string;
  item_id?: string | null;
  category: string;
  product?: string | null;
  attribute?: string | null;
  value?: string | null;
  unit?: string | null;
  constraint?: string | null;
  text: string;
  source_page?: number | null;
  extraction_method: string;
  extraction_confidence: number;
  standard_number?: string | null;
  part?: string | null;
  year?: string | null;
  source_citation?: string | null;
}

export interface RetrievalResult {
  standard_id: string;
  title: string;
  retrieval_paths: string[];
  rrf_score: number;
  rerank_score?: number | null;
}

export interface ApplicabilityAssessment {
  standard_id: string;
  result: "strong" | "possible" | "weak" | "unknown";
  reasons: string[];
  evidence_ids: string[];
}

export interface LifecycleAssessment {
  standard_id: string;
  state: "supported" | "warning" | "unknown";
  as_of_date?: string | null;
  reasons: string[];
  evidence_ids: string[];
}

export interface Relationship {
  from_standard: string;
  to_standard: string;
  relationship_type: string;
  evidence_ids: string[];
  verified: boolean;
  hop?: number | null;
}

export interface CoverageEntry {
  requirement_id: string;
  standard_id?: string | null;
  state:
    | "covered"
    | "partial"
    | "not_covered"
    | "conflicting"
    | "unknown"
    | "unverified_reference"
    | "edition_mismatch";
  reason: string;
  evidence_ids: string[];
}

export interface ConflictRecord {
  conflict_type: string;
  description: string;
  evidence_ids: string[];
}

export interface CertificationResult {
  state: "verified" | "not_verified_in_prototype_corpus" | "conflict";
  rule_type?: string | null;
  description?: string | null;
  effective_date?: string | null;
  evidence_ids: string[];
}

export interface StandardRecord {
  standard_id: string;
  title: string;
  scope: string;
  category: string;
  versions: string[];
  lifecycle_events: Array<{
    event: string;
    date: string;
    evidence_ids: string[];
  }>;
  certification_keys: string[];
  keywords: string[];
  evidence_ids: string[];
  conflicts_with: string[];
  standard_role: StandardRole;
  product_terms: string[];
  application_terms: string[];
  exclusion_terms: string[];
}

export interface AnalysisRequest {
  text?: string | null;
  file_path?: string | null;
  tender_date?: string | null;
}

export interface AnalysisResponse {
  analysis_id: string;
  input_text: string;
  language: {
    detected: "en" | "hi" | "kn" | "ta" | "te" | "mixed" | "unsupported";
    processing_mode: "native_english" | "translated_to_english" | "mixed" | "unsupported";
    translation_verified: boolean;
  };
  requirements: Requirement[];
  candidates: RetrievalResult[];
  applicability: ApplicabilityAssessment[];
  lifecycle: LifecycleAssessment[];
  related_standards: Relationship[];
  certification: Record<string, CertificationResult>;
  coverage: CoverageEntry[];
  gaps: CoverageEntry[];
  conflicts: ConflictRecord[];
  decision: Decision;
  decision_reasons: string[];
  evidence: Evidence[];
  context_evidence: Evidence[];
  tender_cited_standards: Requirement[];
  report_html?: string | null;
  timings_ms: Record<string, number>;
}
