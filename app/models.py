from datetime import date
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field

Decision = Literal["RECOMMEND", "REVIEW", "ABSTAIN", "OUT_OF_CORPUS"]

class Evidence(BaseModel):
    evidence_id: str
    source_id: str
    source_name: str
    url: str
    page: Optional[int] = None
    section: Optional[str] = None
    text: str
    verified: bool = True
    domain: Optional[str] = "pumps"

class Requirement(BaseModel):
    requirement_id: str
    category: str
    product: Optional[str] = None
    attribute: Optional[str] = None
    value: Optional[str] = None
    unit: Optional[str] = None
    constraint: Optional[str] = None
    text: str
    source_page: Optional[int] = None
    extraction_method: str = "rule"
    extraction_confidence: float = 0.0

class RetrievalResult(BaseModel):
    standard_id: str
    title: str
    retrieval_paths: list[str] = Field(default_factory=list)
    rrf_score: float = 0.0
    rerank_score: Optional[float] = None

class ApplicabilityAssessment(BaseModel):
    standard_id: str
    result: Literal["strong", "possible", "weak", "unknown"]
    reasons: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)

class LifecycleAssessment(BaseModel):
    standard_id: str
    state: Literal["supported", "warning", "unknown"]
    as_of_date: Optional[date] = None
    reasons: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)

class Relationship(BaseModel):
    from_standard: str
    to_standard: str
    relationship_type: str
    evidence_ids: list[str] = Field(default_factory=list)
    verified: bool = True
    hop: Optional[int] = None  # CON-09: 1 = direct, 2 = transitive

class CoverageEntry(BaseModel):
    requirement_id: str
    standard_id: Optional[str]
    state: Literal[
        "covered",
        "partial",
        "not_covered",
        "conflicting",
        "unknown",
        "unverified_reference",
        "edition_mismatch",
    ]
    reason: str
    evidence_ids: list[str] = Field(default_factory=list)

class ConflictRecord(BaseModel):
    conflict_type: str
    description: str
    evidence_ids: list[str] = Field(default_factory=list)

class CertificationResult(BaseModel):
    state: Literal["verified", "not_verified_in_prototype_corpus", "conflict"]
    rule_type: Optional[str] = None
    description: Optional[str] = None
    effective_date: Optional[date] = None
    evidence_ids: list[str] = Field(default_factory=list)

class CertificationRule(BaseModel):
    standard_id: str
    rule_type: str
    description: str
    effective_date: Optional[date] = None
    evidence_ids: list[str] = Field(default_factory=list)
    verified: bool = False

# Valid role values for StandardRecord.standard_role
StandardRole = Literal[
    "PRIMARY_PRODUCT_STANDARD",
    "CODE_OF_PRACTICE",
    "TEST_METHOD",
    "RELATED_STANDARD",
]

class StandardRecord(BaseModel):
    standard_id: str
    title: str
    scope: str
    category: str = "pumps"
    domain: str = "pumps"  # Multi-domain support: e.g. "pumps", "electrical", "textiles", "automotive"
    versions: list[str] = Field(default_factory=list)
    lifecycle_events: list[dict[str, Any]] = Field(default_factory=list)
    certification_keys: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    conflicts_with: list[str] = Field(default_factory=list)
    # Applicability discriminator fields — populated from verified evidence only
    standard_role: StandardRole = "PRIMARY_PRODUCT_STANDARD"
    product_terms: list[str] = Field(default_factory=list)     # strong discriminating product nouns
    application_terms: list[str] = Field(default_factory=list) # context (agriculture, irrigation…)
    exclusion_terms: list[str] = Field(default_factory=list)   # words that signal this std does NOT apply
    # Firestore / Vector search extension fields
    embedding: Optional[list[float]] = None
    embedding_model: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)     # flexible domain-agnostic properties

class SourceRecord(BaseModel):
    source_id: str
    name: str
    publisher: str
    url: str
    source_type: str
    retrieved_at: str
    notes: str

class BenchmarkCase(BaseModel):
    id: str
    query: str
    expected_contains: list[str] = Field(default_factory=list)
    expected_decision: Optional[Decision] = None
    expected_cert: Optional[dict[str, str]] = None
    notes: Optional[str] = None

class AnalysisRequest(BaseModel):
    text: Optional[str] = None
    file_path: Optional[str] = None
    tender_date: Optional[date] = None

class AnalysisResponse(BaseModel):
    analysis_id: str
    input_text: str
    requirements: list[Requirement]
    candidates: list[RetrievalResult]
    applicability: list[ApplicabilityAssessment]
    lifecycle: list[LifecycleAssessment]
    related_standards: list[Relationship]
    certification: dict[str, CertificationResult]
    coverage: list[CoverageEntry]
    gaps: list[CoverageEntry]
    conflicts: list[ConflictRecord]
    decision: Decision
    decision_reasons: list[str]
    evidence: list[Evidence]
    report_html: Optional[str] = None
    timings_ms: dict[str, float] = Field(default_factory=dict)

