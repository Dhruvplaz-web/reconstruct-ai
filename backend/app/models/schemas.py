from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class CitationSource(BaseModel):
    id: str = Field(..., description="Unique source identifier")
    source_type: Literal["commit", "discussion", "pr", "doc"]
    uri: str = Field(..., description="URI or path to source record")
    title: str = Field(..., description="Human readable title")
    timestamp: str = Field(..., description="ISO timestamp")
    author: str = Field(..., description="Original creator")
    snippet: str = Field(..., description="Exact diff or message snippet")
    security_tag: Optional[str] = Field(default="PUBLIC", description="Security clearance tag: PUBLIC, CONFIDENTIAL_HR, INFRA_KEYS")

class CommitEvent(BaseModel):
    sha: str
    author: str
    email: Optional[str] = None
    timestamp: str
    message: str
    files_changed: List[str] = Field(default_factory=list)
    insertions: int = 0
    deletions: int = 0
    diff_snippet: Optional[str] = None
    security_tag: str = "PUBLIC"

class DiscussionMessage(BaseModel):
    id: str
    author: str
    channel: str
    timestamp: str
    text: str
    thread_id: Optional[str] = None
    security_tag: str = "PUBLIC"

class DecisionNode(BaseModel):
    id: str
    title: str
    summary: str
    rationale: str
    timestamp: str
    authors: List[str]
    status: Literal["ACTIVE", "REVERTED", "SUPERSEDED", "UNDER_REVIEW"] = "ACTIVE"
    citations: List[CitationSource] = Field(default_factory=list)
    grounding_score: float = Field(..., ge=0.0, le=1.0, description="Epistemic grounding score G(A)")
    has_contradiction: bool = False
    quarantined_for_review: bool = False

class ContradictionAlert(BaseModel):
    id: str
    topic: str
    claim_a: str
    source_a: CitationSource
    claim_b: str
    source_b: CitationSource
    contradiction_score: float = Field(..., ge=0.0, le=1.0, description="Probability of contradiction from DeBERTa-v3")
    explanation: str
    severity: Literal["HIGH", "MEDIUM", "LOW"] = "HIGH"
    status: Literal["OPEN", "RESOLVED_BY_LEAVER", "FALSE_POSITIVE"] = "OPEN"

class OrphanRiskFile(BaseModel):
    file_path: str
    primary_author: str
    blame_percentage: float = Field(..., ge=0.0, le=100.0)
    total_lines: int
    single_author_lines: int
    last_modified_date: str
    bus_factor_risk: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    risk_rationale: str

class LeaverQuestion(BaseModel):
    id: str
    file_path: str
    question: str
    context: str
    options: List[str]
    suggested_answer: Optional[str] = None

class LeaverReviewSubmission(BaseModel):
    responses: Dict[str, str] = Field(..., description="Mapping of question_id to selected answer or text")
    additional_notes: Optional[str] = None
    approved_by: str
    approved_at: Optional[str] = None
    digital_signature: Optional[str] = None
    public_key: Optional[str] = None
    canonical_sha256: Optional[str] = None

class KanbanTask(BaseModel):
    id: str
    stage: Literal["DAY_1", "DAY_7", "DAY_30"]
    title: str
    description: str
    priority: Literal["URGENT", "HIGH", "MEDIUM"] = "HIGH"
    category: Literal["ARCHITECTURE", "DEBUGGING", "DEPLOYMENT", "CODE_WALKTHROUGH"]
    linked_file: Optional[str] = None
    linked_pr: Optional[str] = None
    citation_id: Optional[str] = None
    completed: bool = False

class HandoverWorkspace(BaseModel):
    project_name: str
    leaver_name: str
    institution: str = "JSPM RSCOE, Pune"
    generated_at: str
    viewer_role: Literal["ADMIN", "JUNIOR_SUCCESSOR", "AUDITOR"] = "JUNIOR_SUCCESSOR"
    executive_summary: str
    orphan_risk_files: List[OrphanRiskFile]
    decisions: List[DecisionNode]
    contradictions: List[ContradictionAlert]
    kanban_tasks: List[KanbanTask]
    stats: Dict[str, Any] = Field(default_factory=dict)

