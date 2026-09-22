from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class QueryRequest(BaseModel):
    query: str = Field(..., description="User's BIS regulatory question")
    language: Optional[str] = Field("en", description="Query language code (en, hi, ta, te, bn, etc.)")

class EvidenceItem(BaseModel):
    document: str
    clause: str
    page: int
    version: str
    snippet: str
    relevance_score: float = 0.95

class QueryResponse(BaseModel):
    query_id: Optional[int] = None
    original_query: str
    language: str
    intent: str
    entities: List[str]
    applicable_standards: List[str]
    certification_path: List[str]
    testing_guidance: List[str]
    evidence: List[EvidenceItem]
    sources: List[str]
    verified: bool
    verification_notes: Optional[str] = None
    answer: str

class DocumentUploadResponse(BaseModel):
    status: str
    document_id: Optional[int] = None
    filename: str
    standard_number: str
    version: str
    page_count: int
    is_scanned: bool
    chunks_created: int
    message: str

class FeedbackRequest(BaseModel):
    query_id: int
    feedback: str = Field(..., description="'helpful', 'unhelpful', or 'incorrect'")
    comments: Optional[str] = None

class StandardResponse(BaseModel):
    standard_number: str
    title: str
    doc_type: str
    version: str
    clause_count: int
    created_at: datetime
