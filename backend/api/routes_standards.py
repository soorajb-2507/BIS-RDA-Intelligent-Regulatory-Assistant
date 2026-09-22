from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import BISDocument, BISLaboratory, CertificationScheme
from rda.regulatory_mapper import REGULATORY_TAXONOMY

router = APIRouter()

@router.get("/standards")
def list_standards(db: Session = Depends(get_db)):
    """
    Returns list of indexed BIS standards and regulatory schemes.
    """
    docs = db.query(BISDocument).all()
    standards_list = []
    seen = set()

    for d in docs:
        if d.standard_number not in seen:
            seen.add(d.standard_number)
            standards_list.append({
                "standard_number": d.standard_number,
                "title": d.title,
                "version": d.version,
                "doc_type": d.doc_type,
                "source": "PostgreSQL Knowledge Base"
            })

    # Also include standard BIS benchmark taxonomy
    for key, val in REGULATORY_TAXONOMY.items():
        if val["standard"] not in seen:
            seen.add(val["standard"])
            standards_list.append({
                "standard_number": val["standard"],
                "title": val["title"],
                "version": "Current",
                "doc_type": "Standard",
                "source": "BIS Regulatory Master Catalog"
            })

    return standards_list

@router.get("/standards/{standard_number}")
def get_standard_detail(standard_number: str, db: Session = Depends(get_db)):
    doc = db.query(BISDocument).filter(BISDocument.standard_number.ilike(f"%{standard_number}%")).first()
    
    # Check taxonomy for enrichment
    enriched = None
    for key, val in REGULATORY_TAXONOMY.items():
        if standard_number.upper().replace(" ", "") in val["standard"].upper().replace(" ", ""):
            enriched = val
            break

    if not doc and not enriched:
        raise HTTPException(status_code=404, detail=f"Standard {standard_number} not found")

    return {
        "standard_number": doc.standard_number if doc else enriched["standard"],
        "title": doc.title if doc else enriched["title"],
        "version": doc.version if doc else "Current",
        "taxonomy": enriched
    }
