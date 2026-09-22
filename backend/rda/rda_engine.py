from typing import Dict, Any, List
from utils.logger import get_logger
from nlp.indicbert_service import IndicBERTService
from rda.regulatory_mapper import RegulatoryMapper
from retrieval.hybrid_retriever import HybridRetriever
from reasoning.llamaindex_rag import LlamaIndexRAG
from verification.evidence_verifier import EvidenceVerifier

logger = get_logger("rda_engine")

class RDAEngine:
    """
    RDA = Regulatory DNA / Regulatory Decision Architecture.
    
    Orchestrates the complete 13-stage BIS Regulatory Workflow:
    1. Receive user query
    2. Understand intent (IndicBERT)
    3. Identify product/entity information
    4. Identify regulatory domain
    5. Identify applicable standards
    6. Map query to regulatory concepts
    7. Search knowledge sources
    8. Retrieve supporting evidence
    9. Combine keyword (ES), semantic (Qdrant) and graph (Neo4j) retrieval
    10. Pass verified context to reasoning layer (LlamaIndex)
    11. Generate structured regulatory answer (Ollama Qwen/Llama)
    12. Send answer and evidence to verification
    13. Return verified answer to frontend
    """
    def __init__(self):
        self.nlp = IndicBERTService()
        self.mapper = RegulatoryMapper()
        self.retriever = HybridRetriever()
        self.rag = LlamaIndexRAG()
        self.verifier = EvidenceVerifier()

    def orchestrate_query(self, user_query: str, language: str = "en") -> Dict[str, Any]:
        logger.info(f"[RDA Stage 1] Receiving user query: '{user_query}' (lang={language})")

        # Stage 2 & 3: Intent & Entity Understanding via IndicBERT
        query_meta = self.nlp.analyze_query(user_query, language)
        intent = query_meta["intent"]
        entities = query_meta["product_terms"]
        detected_standards = query_meta["detected_standards"]

        # Stage 4, 5, 6: Domain, Standard Identification & Concept Mapping
        mapped_concepts = self.mapper.map_to_concepts(entities, detected_standards)
        regulatory_domain = query_meta["regulatory_domain"]
        if mapped_concepts:
            for c in mapped_concepts:
                if c["standard"] not in detected_standards:
                    detected_standards.append(c["standard"])

        query_meta["detected_standards"] = detected_standards

        # Stage 7, 8, 9: Hybrid Knowledge Retrieval (Elasticsearch + Qdrant + Neo4j)
        retrieval_bundle = self.retriever.retrieve(query_meta, top_k=5)
        raw_evidence = retrieval_bundle["evidence"]
        graph_context = retrieval_bundle["graph_context"]

        # If knowledge base didn't return graph context, augment from regulatory taxonomy
        if not graph_context and mapped_concepts:
            for c in mapped_concepts:
                graph_context.append({
                    "standard": c["standard"],
                    "product": c["title"],
                    "material": c["material"],
                    "industry": c["industry"],
                    "certification": c["scheme"],
                    "testing": c["testing"],
                    "laboratory": c["lab"],
                    "rule": c["rule"]
                })

        # Stage 10 & 11: Pass verified context to LlamaIndex & Ollama AI Reasoning
        reasoning_output = self.rag.generate_reasoned_answer(
            query=user_query,
            evidence=raw_evidence,
            graph_context=graph_context,
            query_meta=query_meta
        )

        # Stage 12: Evidence Verification Stage
        verification_result = self.verifier.verify(
            answer=reasoning_output["answer"],
            evidence=raw_evidence,
            standards_claimed=reasoning_output.get("applicable_standards", []),
            query_entities=entities
        )

        # Stage 13: Final Verified Response Packaging
        if not verification_result["is_verified"]:
            logger.warning("[RDA Stage 13] Response failed verification. Returning grounded refusal.")
            return {
                "original_query": user_query,
                "language": query_meta.get("language", language),
                "intent": intent,
                "entities": entities,
                "applicable_standards": [],
                "certification_path": [],
                "testing_guidance": [],
                "evidence": [],
                "sources": [],
                "verified": False,
                "verification_notes": verification_result.get("notes", "Insufficient verified BIS evidence was found to provide a reliable answer."),
                "answer": "Insufficient verified BIS evidence was found to provide a reliable answer."
            }

        logger.info("[RDA Stage 13] Verified answer generated successfully.")
        return {
            "original_query": user_query,
            "language": query_meta.get("language", language),
            "intent": intent,
            "entities": entities,
            "applicable_standards": reasoning_output.get("applicable_standards", detected_standards),
            "certification_path": reasoning_output.get("certification_path", []),
            "testing_guidance": reasoning_output.get("testing_guidance", []),
            "evidence": verification_result["verified_evidence"],
            "sources": reasoning_output.get("sources", []),
            "verified": True,
            "verification_notes": verification_result["notes"],
            "answer": reasoning_output["answer"]
        }
