from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import init_db
from api.routes_query import router as query_router
from api.routes_documents import router as documents_router
from api.routes_standards import router as standards_router
from api.routes_feedback import router as feedback_router
from utils.logger import get_logger

logger = get_logger("main")

app = FastAPI(
    title="BIS AI Regulatory/Standards Question Answering System",
    version="1.0.0",
    description="Full-stack AI system for Bureau of Indian Standards (BIS) Question Answering, Regulatory Reasoning, and Evidence Verification"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(query_router, prefix="/api", tags=["Query & Reasoning"])
app.include_router(documents_router, prefix="/api", tags=["Document Ingestion"])
app.include_router(standards_router, prefix="/api", tags=["Standards & Schemes"])
app.include_router(feedback_router, prefix="/api", tags=["Continuous Learning Feedback"])

@app.on_event("startup")
def on_startup():
    logger.info("Initializing BIS Regulatory QA Application...")
    init_db()
    # Seed baseline BIS standards if needed
    try:
        from seed_data import seed_initial_bis_knowledge
        seed_initial_bis_knowledge()
    except Exception as e:
        logger.warning(f"Seed data execution: {e}")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "BIS Regulatory QA Assistant Backend",
        "subsystems": {
            "fastapi": "running",
            "indicbert": "available",
            "rda_engine": "active",
            "hybrid_retrieval": "active",
            "evidence_verification": "enforced"
        }
    }

if __name__ == "__main__":
    # pyrefly: ignore [missing-import]
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

