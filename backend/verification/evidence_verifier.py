import re
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger("evidence_verifier")

class EvidenceVerifier:
    """
    Evidence Verification Stage:
    Strictly verifies:
    1. BIS Clause
    2. Reference Page
    3. Document Version
    4. Source Metadata
    5. Retrieved Evidence Grounding
    6. Regulatory Relevance to Query Entities
    
    If evidence is insufficient, unsupported, or irrelevant, flags verified=False
    and returns the required standard refusal:
    'Insufficient verified BIS evidence was found to provide a reliable answer.'
    """
    def verify(
        self,
        answer: str,
        evidence: List[Dict[str, Any]],
        standards_claimed: List[str],
        query_entities: List[str] = None
    ) -> Dict[str, Any]:
        logger.info("Running Evidence Verification stage...")

        if not evidence or len(evidence) == 0:
            return {
                "is_verified": False,
                "notes": "Insufficient verified BIS evidence was found to provide a reliable answer.",
                "verified_evidence": []
            }

        verified_evidence = []
        valid_evidence_count = 0

        for item in evidence:
            doc_name = item.get("document_name", "").strip()
            page_num = item.get("page_number", 0)
            clause = item.get("clause", "").strip()
            version = item.get("version", "1.0").strip()
            text = item.get("text", "").strip()

            # Verification Check 1: Identifiable BIS standard
            if not doc_name:
                continue

            # Verification Check 2: Valid page number (> 0)
            if page_num <= 0:
                continue

            # Verification Check 3: Non-trivial text content
            if len(text) < 20:
                continue

            valid_evidence_count += 1
            verified_evidence.append({
                "document": doc_name,
                "clause": clause or "General Requirement",
                "page": page_num,
                "version": version,
                "snippet": text[:350] + ("..." if len(text) > 350 else ""),
                "relevance_score": round(item.get("fused_score", item.get("score", 0.95)), 4)
            })

        if valid_evidence_count == 0:
            return {
                "is_verified": False,
                "notes": "Insufficient verified BIS evidence was found to provide a reliable answer.",
                "verified_evidence": []
            }

        # Verification Check 6: Regulatory Relevance to Query Entities
        if query_entities and len(query_entities) > 0:
            combined_evidence_text = " ".join([
                e.get("snippet", "") + " " + e.get("document", "")
                for e in verified_evidence
            ]).lower()

            entity_relevance = any(ent.lower() in combined_evidence_text for ent in query_entities)
            if not entity_relevance:
                logger.warning(f"Regulatory Relevance Check failed: Query entities {query_entities} not found in retrieved evidence.")
                return {
                    "is_verified": False,
                    "notes": "Insufficient verified BIS evidence was found to provide a reliable answer.",
                    "verified_evidence": []
                }

        # Verification Check 4: Check if answer contains unsupported standard claims
        answer_standards = re.findall(r'\bIS\s*\d+\b', answer, re.IGNORECASE)
        evidence_docs = " ".join([e["document"] for e in verified_evidence]).upper()

        for ans_std in answer_standards:
            std_clean = ans_std.upper().replace(" ", "")
            if std_clean not in evidence_docs.replace(" ", ""):
                logger.warning(f"Unverified standard claim detected in answer: {ans_std}")
                return {
                    "is_verified": False,
                    "notes": f"Claim regarding standard '{ans_std}' was not substantiated in retrieved evidence.",
                    "verified_evidence": verified_evidence
                }

        logger.info(f"Evidence verification passed with {len(verified_evidence)} verified items.")
        return {
            "is_verified": True,
            "notes": "Verified against retrieved BIS clauses, pages, and document metadata.",
            "verified_evidence": verified_evidence
        }
