export type SecurityTag = "PUBLIC" | "CONFIDENTIAL_HR" | "CONFIDENTIAL_INFRA";

export interface CitationSource {
  id: string;
  source_type: "commit" | "discussion" | "pr" | "doc";
  uri: string;
  title: string;
  timestamp: string;
  author: string;
  snippet: string;
  security_tag?: SecurityTag;
}

export interface CommitEvent {
  sha: string;
  author: string;
  email?: string;
  timestamp: string;
  message: string;
  files_changed: string[];
  insertions: number;
  deletions: number;
  diff_snippet?: string;
  security_tag: SecurityTag;
}

export interface DiscussionMessage {
  id: string;
  author: string;
  channel: string;
  timestamp: string;
  text: string;
  thread_id?: string;
  security_tag: SecurityTag;
}

export interface DecisionNode {
  id: string;
  title: string;
  summary: string;
  rationale: string;
  timestamp: string;
  authors: string[];
  status: "ACTIVE" | "REVERTED" | "SUPERSEDED" | "UNDER_REVIEW";
  citations: CitationSource[];
  grounding_score: number;
  has_contradiction: boolean;
  quarantined_for_review: boolean;
}

export interface ContradictionAlert {
  id: string;
  topic: string;
  claim_a: string;
  source_a: CitationSource;
  claim_b: string;
  source_b: CitationSource;
  contradiction_score: number;
  explanation: string;
  severity: "HIGH" | "MEDIUM" | "LOW";
  status: "OPEN" | "RESOLVED_BY_LEAVER" | "FALSE_POSITIVE";
}

export interface OrphanRiskFile {
  file_path: string;
  primary_author: string;
  blame_percentage: number;
  total_lines: number;
  single_author_lines: number;
  last_modified_date: string;
  bus_factor_risk: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  risk_rationale: string;
}

export interface LeaverQuestion {
  id: string;
  file_path: string;
  question: string;
  context: string;
  options: string[];
  suggested_answer?: string;
}

export interface LeaverReviewSubmission {
  responses: Record<string, string>;
  additional_notes?: string;
  approved_by: string;
  approved_at?: string;
  digital_signature?: string;
  public_key?: string;
  canonical_sha256?: string;
}

export interface KanbanTask {
  id: string;
  stage: "DAY_1" | "DAY_7" | "DAY_30";
  title: string;
  description: string;
  priority: "URGENT" | "HIGH" | "MEDIUM";
  category: "ARCHITECTURE" | "DEBUGGING" | "DEPLOYMENT" | "CODE_WALKTHROUGH";
  linked_file?: string;
  linked_pr?: string;
  citation_id?: string;
  completed: boolean;
}

export interface HandoverWorkspace {
  project_name: string;
  leaver_name: string;
  institution: string;
  generated_at: string;
  viewer_role: "ADMIN" | "JUNIOR_SUCCESSOR" | "AUDITOR";
  executive_summary: string;
  orphan_risk_files: OrphanRiskFile[];
  decisions: DecisionNode[];
  contradictions: ContradictionAlert[];
  kanban_tasks: KanbanTask[];
  stats: {
    bus_factor_files_count?: number;
    active_decisions_count?: number;
    unresolved_contradictions?: number;
    leaver_review_completed?: boolean;
    digital_signature?: string;
  };
}

export interface DAGNode {
  id: string;
  label: string;
  full_title?: string;
  author?: string;
  timestamp?: string;
  node_type: "commit" | "discussion" | "decision" | "task";
  badge: string;
  grounding_score?: number;
  has_contradiction?: boolean;
}

export interface DAGEdge {
  source: string;
  target: string;
  relation: string;
}

export interface DAGGraph {
  node_count: number;
  edge_count: number;
  is_dag: boolean;
  nodes: DAGNode[];
  edges: DAGEdge[];
}

