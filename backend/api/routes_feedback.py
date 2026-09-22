from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from models.schemas import FeedbackRequest
from services.continuous_learning import ContinuousLearningService

router = APIRouter()
learning_service = ContinuousLearningService()

@router.post("/feedback")
def submit_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Continuous Learning Feedback Endpoint:
    Allows users to provide feedback on query responses (helpful, unhelpful, incorrect)
    to drive continuous regulatory knowledge improvement.
    """
    try:
        learning_service.record_user_feedback(
            query_id=req.query_id,
            feedback=req.feedback,
            comments=req.comments
        )
        return {
            "status": "success",
            "message": "Feedback recorded for continuous knowledge improvement.",
            "query_id": req.query_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
