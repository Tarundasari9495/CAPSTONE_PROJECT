// ─────────────────────────────────────────────────────────────
// Shared Types for Contract Analysis Tool
// ─────────────────────────────────────────────────────────────

export interface ContractUploadResponse {
  contract_id: string;
  file_name: string;
  status: ContractStatus;
}

export type ContractStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface ContractRecord {
  id: string;
  file_name: string;
  file_size: number;
  file_type: 'pdf' | 'docx';
  upload_date: string;
  status: ContractStatus;
  error_message?: string | null;
}

export interface ContractHistoryItem {
  id: string;
  file_name: string;
  upload_date: string;
  status: ContractStatus;
  risk_score?: number | null;
}

export interface Clause {
  id: string;
  clause_type: string;
  clause_text: string;
  page_number?: number | null;
}

export interface Risk {
  id: string;
  risk_level: RiskLevel;
  risk_description: string;
  clause_type?: string | null;
  created_at: string;
}

export type RiskLevel = 'high' | 'medium' | 'low';

export interface ContractSummary {
  executive_summary?: string;
  key_terms?: string;
  important_obligations?: string[];
  important_dates?: string[];
}

export interface ContractInformation {
  title?: string;
  effective_date?: string | null;
  expiration_date?: string | null;
  parties?: Array<{ name: string; role: string }>;
  contract_value?: string | null;
  renewal_terms?: string | null;
}

export interface AnalysisReport {
  id: string;
  contract_id: string;
  summary?: ContractSummary | null;
  contract_info?: ContractInformation | null;
  risk_score?: number | null;
  clauses: Clause[];
  risks: Risk[];
  created_at: string;
}

// ─────────────────────────────────────────────────────────────
// Streaming / SSE Progress Events
// ─────────────────────────────────────────────────────────────

export type ProgressStage =
  | 'extracting'
  | 'clauses'
  | 'risks'
  | 'data'
  | 'summary'
  | 'report'
  | 'complete'
  | 'error';

export interface ProgressEvent {
  stage: ProgressStage;
  message: string;
  report?: AnalysisReport;
  error_code?: string;
}

// ─────────────────────────────────────────────────────────────
// API Error Shape
// ─────────────────────────────────────────────────────────────

export interface ApiError {
  error_code: string;
  message: string;
}
