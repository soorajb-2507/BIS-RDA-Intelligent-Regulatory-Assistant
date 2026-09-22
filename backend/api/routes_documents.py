import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from database.connection import get_db
from database.models import BISDocument, BISClause
from models.schemas import DocumentUploadResponse
from processing.pdf_processor import DocumentProcessor
from services.continuous_learning import ContinuousLearningService
from utils.logger import get_logger

logger = get_logger("routes_documents")
router = APIRouter()
processor = DocumentProcessor()
learning_service = ContinuousLearningService()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_and_process_document(
    file: UploadFile = File(...),
    standard_number: str = Form(...),
    title: Optional[str] = Form(None),
    version: str = Form("1.0"),
    doc_type: str = Form("Standard"),
    db: Session = Depends(get_db)
):
    """
    BIS Document Ingestion Pipeline:
    Upload PDF -> PyMuPDF extraction -> PaddleOCR fallback -> Text Cleaning & Chunking
    -> PostgreSQL -> Elasticsearch -> Qdrant -> Neo4j -> Knowledge Base Ready
    """
    if not file.filename.lower().endswith((".pdf", ".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and scanned images are accepted.")

    saved_file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(saved_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        doc_title = title or standard_number

        # Process document
        chunks, meta_summary = processor.process_pdf(
            file_path=saved_file_path,
            doc_name=standard_number,
            version=version,
            doc_type=doc_type
        )

        # Ingest into Multi-Model Knowledge Base
        res = learning_service.ingest_new_standard_version(
            standard_number=standard_number,
            title=doc_title,
            new_version=version,
            file_path=saved_file_path,
            chunks=chunks,
            summary_of_changes=f"Initial ingestion of {standard_number} (v{version})"
        )

        return {
            "status": "success",
            "document_id": res["document_id"],
            "filename": file.filename,
            "standard_number": standard_number,
            "version": version,
            "page_count": meta_summary["page_count"],
            "is_scanned": meta_summary["is_scanned"],
            "chunks_created": len(chunks),
            "message": "Document successfully ingested, chunked, and indexed in PostgreSQL, Elasticsearch, Qdrant, and Neo4j."
        }
    except Exception as e:
        logger.error(f"Failed to process uploaded document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(BISDocument).order_by(BISDocument.created_at.desc()).all()
    results = []
    for d in docs:
        results.append({
            "id": d.id,
            "title": d.title,
            "standard_number": d.standard_number,
            "version": d.version,
            "doc_type": d.doc_type,
            "page_count": d.page_count,
            "is_scanned": d.is_scanned,
            "processing_status": d.processing_status,
            "created_at": d.created_at
        })
    return results

@router.get("/documents/{doc_id}")
def get_document_details(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(BISDocument).filter(BISDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    clauses = db.query(BISClause).filter(BISClause.document_id == doc_id).all()
    return {
        "id": doc.id,
        "title": doc.title,
        "standard_number": doc.standard_number,
        "version": doc.version,
        "doc_type": doc.doc_type,
        "page_count": doc.page_count,
        "is_scanned": doc.is_scanned,
        "created_at": doc.created_at,
        "clauses": [
            {
                "clause_number": c.clause_number,
                "clause_title": c.clause_title,
                "page_number": c.page_number,
                "snippet": c.content[:150]
            }
            for c in clauses
        ]
    }
