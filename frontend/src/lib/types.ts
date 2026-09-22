export interface EvidenceItem {
  document: string;
  clause: string;
  page: number;
  version: string;
  snippet: string;
  relevance_score: number;
}

export interface QueryResponse {
  query_id?: number;
  original_query: string;
  language: string;
  intent: string;
  entities: string[];
  applicable_standards: string[];
  certification_path: string[];
  testing_guidance: string[];
  evidence: EvidenceItem[];
  sources: string[];
  verified: boolean;
  verification_notes?: string | null;
  answer: string;
}

export interface DocumentUploadResponse {
  status: string;
  document_id?: number;
  filename: string;
  standard_number: string;
  version: string;
  page_count: number;
  is_scanned: boolean;
  chunks_created: number;
  message: string;
}

export interface BISDocumentRecord {
  id: number;
  title: string;
  standard_number: string;
  version: string;
  doc_type: string;
  page_count: number;
  is_scanned: boolean;
  processing_status: string;
  created_at: string;
}

export interface BISStandardSummary {
  standard_number: string;
  title: string;
  version: string;
  doc_type: string;
  source: string;
}
