from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.logger import get_logger
from database.connection import SessionLocal
from database.models import BISDocument, BISClause, StandardUpdate, QueryAudit
from retrieval.elasticsearch_client import ElasticClient
from retrieval.qdrant_client import QdrantStoreClient
from retrieval.neo4j_client import Neo4jGraphClient

logger = get_logger("continuous_learning")

class ContinuousLearningService:
    """
    Implements the Continuous Regulatory Learning and Knowledge Improvement loop:
    New BIS Standards + BIS Updates + User Feedback + Real-world Queries
    ↓
    Knowledge Improvement
    ↓
    RDA Engine
    ↓
    Updated Retrieval/Knowledge
    ↓
    Improved Answers
    """
    def __init__(self):
        self.es_client = ElasticClient()
        self.qdrant_client = QdrantStoreClient()
        self.neo4j_client = Neo4jGraphClient()

    def ingest_new_standard_version(
        self,
        standard_number: str,
        title: str,
        new_version: str,
        file_path: str,
        chunks: List[Dict[str, Any]],
        summary_of_changes: Optional[str] = None
    ) -> Dict[str, Any]:
        logger.info(f"Ingesting new standard version: {standard_number} (v{new_version})")
        db = SessionLocal()
        try:
            # 1. Check existing version in PostgreSQL
            existing = db.query(BISDocument).filter(
                BISDocument.standard_number == standard_number
            ).order_by(BISDocument.created_at.desc()).first()

            old_version = existing.version if existing else "0.0"

            # 2. Store new version in PostgreSQL
            doc_record = BISDocument(
                title=title,
                standard_number=standard_number,
                version=new_version,
                file_path=file_path,
                page_count=max([c.get("page_number", 1) for c in chunks]) if chunks else 1,
                processing_status="completed",
                doc_metadata={"change_summary": summary_of_changes or "Updated release"}
            )
            db.add(doc_record)
            db.commit()
            db.refresh(doc_record)

            # Store clauses in PostgreSQL
            for c in chunks:
                clause_record = BISClause(
                    document_id=doc_record.id,
                    clause_number=c.get("clause", "General"),
                    page_number=c.get("page_number", 1),
                    clause_title=c.get("clause_title", ""),
                    content=c.get("text", "")
                )
                db.add(clause_record)

            # Record standard update history
            update_audit = StandardUpdate(
                standard_number=standard_number,
                old_version=old_version,
                new_version=new_version,
                effective_date=datetime.utcnow(),
                summary_of_changes=summary_of_changes or f"Updated from v{old_version} to v{new_version}"
            )
            db.add(update_audit)
            db.commit()

            # 3. Update Elasticsearch index (Lexical)
            for idx, c in enumerate(chunks):
                doc_id = f"{standard_number}_{new_version}_{c.get('page_number', 1)}_{idx}"
                c["version"] = new_version
                self.es_client.index_chunk(c, doc_id)

            # 4. Update Qdrant vector database (Semantic)
            for c in chunks:
                self.qdrant_client.upsert_chunk(c)

            # 5. Update Neo4j Knowledge Graph relationships
            self.neo4j_client.sync_regulatory_chain(
                standard_number=standard_number,
                product_name=title,
                material="Compliant Material",
                industry="Regulated Industry",
                certification_scheme="Scheme-I (ISI Mark)",
                testing_requirement=f"Testing per {standard_number}:{new_version}",
                laboratory_name="BIS Recognized Laboratory",
                applicable_rule=f"BIS Quality Control Order for {standard_number}"
            )

            logger.info(f"Continuous learning update for {standard_number} v{new_version} completed successfully.")
            return {
                "status": "success",
                "document_id": doc_record.id,
                "standard_number": standard_number,
                "old_version": old_version,
                "new_version": new_version,
                "chunks_indexed": len(chunks)
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error during continuous learning update: {e}")
            raise e
        finally:
            db.close()

    def record_user_feedback(self, query_id: int, feedback: str, comments: Optional[str] = None):
        """
        Feedback loop for real-world queries to drive continuous learning.
        """
        db = SessionLocal()
        try:
            audit = db.query(QueryAudit).filter(QueryAudit.id == query_id).first()
            if audit:
                audit.user_feedback = feedback
                if comments:
                    info = dict(audit.verification_info or {})
                    info["user_comments"] = comments
                    audit.verification_info = info
                db.commit()
                logger.info(f"Feedback '{feedback}' recorded for query {query_id}.")
        finally:
            db.close()
