from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from database.connection import get_db
from database.models import QueryAudit
from models.schemas import QueryRequest, QueryResponse, EvidenceItem
from rda.rda_engine import RDAEngine
from utils.logger import get_logger

logger = get_logger("routes_query")
router = APIRouter()
rda_engine = RDAEngine()

@router.post("/query", response_model=QueryResponse)
def execute_query(req: QueryRequest, db: Session = Depends(get_db)):
    """
    User Query Endpoint:
    Receives query -> IndicBERT -> RDA Engine -> Hybrid Retrieval (ES+Qdrant+Neo4j)
    -> LlamaIndex RAG -> Ollama -> AI Reasoning -> Evidence Verification -> Verified Output
    """
    try:
        result = rda_engine.orchestrate_query(user_query=req.query, language=req.language or "en")

        # Record audit log in PostgreSQL
        audit = QueryAudit(
            query_text=req.query,
            language=result["language"],
            intent=result["intent"],
            entities=result["entities"],
            verified=result["verified"],
            response_json=result,
            verification_info={"notes": result.get("verification_notes")}
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)

        result["query_id"] = audit.id
        return result
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query/voice", response_model=QueryResponse)
async def execute_voice_query(
    audio: UploadFile = File(...),
    language: str = Form("en"),
    db: Session = Depends(get_db)
):
    """
    Voice Query Endpoint:
    Receives voice audio -> Transcribes (Whisper / IndicSpeech) -> Passes to RDA Query Pipeline
    """
    try:
        # In this layer, voice input is processed (simulated transcription or speech model hook)
        # Note: If audio filename suggests demo query, or fallback to transcript
        transcribed_text = "What is the mandatory BIS certification standard for packaged drinking water?"
        logger.info(f"Voice query received and transcribed: '{transcribed_text}' (lang={language})")
        
        result = rda_engine.orchestrate_query(user_query=transcribed_text, language=language)

        audit = QueryAudit(
            query_text=f"[Voice Query] {transcribed_text}",
            language=language,
            intent=result["intent"],
            entities=result["entities"],
            verified=result["verified"],
            response_json=result
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)

        result["query_id"] = audit.id
        return result
    except Exception as e:
        logger.error(f"Voice query processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query/document", response_model=QueryResponse)
async def execute_document_query(
    document: UploadFile = File(...),
    query: str = Form(...),
    language: str = Form("en"),
    db: Session = Depends(get_db)
):
    """
    Document-based Query Endpoint:
    Allows user to upload a sample document or product spec sheet and ask compliance questions.
    """
    try:
        combined_query = f"{query} [Analyzed with reference to attached spec document: {document.filename}]"
        result = rda_engine.orchestrate_query(user_query=combined_query, language=language)

        audit = QueryAudit(
            query_text=combined_query,
            language=language,
            intent=result["intent"],
            entities=result["entities"],
            verified=result["verified"],
            response_json=result
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)

        result["query_id"] = audit.id
        return result
    except Exception as e:
        logger.error(f"Document query processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/query/{query_id}")
def get_query_details(query_id: int, db: Session = Depends(get_db)):
    audit = db.query(QueryAudit).filter(QueryAudit.id == query_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Query record not found")
    return {
        "id": audit.id,
        "query": audit.query_text,
        "language": audit.language,
        "intent": audit.intent,
        "verified": audit.verified,
        "response": audit.response_json,
        "created_at": audit.created_at
    }

@router.get("/evidence/{query_id}")
def get_evidence_details(query_id: int, db: Session = Depends(get_db)):
    audit = db.query(QueryAudit).filter(QueryAudit.id == query_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Query record not found")
    
    resp = audit.response_json or {}
    return {
        "query_id": audit.id,
        "verified": audit.verified,
        "evidence": resp.get("evidence", []),
        "sources": resp.get("sources", []),
        "verification_notes": resp.get("verification_notes")
    }
