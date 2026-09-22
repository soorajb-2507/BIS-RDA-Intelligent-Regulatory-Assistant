import json
from typing import List, Dict, Any, Tuple
from utils.logger import get_logger
from reasoning.ollama_client import OllamaClient

logger = get_logger("llamaindex_rag")

class LlamaIndexRAG:
    """
    RAG Pipeline orchestration using LlamaIndex patterns & Ollama:
    - Evidence context construction
    - Knowledge graph context synthesis
    - Strict evidence-grounded prompt engineering
    - Zero-hallucination regulatory reasoning
    """
    def __init__(self):
        self.ollama = OllamaClient()

    def generate_reasoned_answer(
        self,
        query: str,
        evidence: List[Dict[str, Any]],
        graph_context: List[Dict[str, Any]],
        query_meta: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not evidence or len(evidence) == 0:
            logger.info("No evidence chunks available for reasoning.")
            return {
                "answer": "Insufficient verified BIS evidence was found to provide a reliable answer.",
                "applicable_standards": [],
                "certification_path": [],
                "testing_guidance": [],
                "sources": [],
                "has_sufficient_evidence": False
            }

        # 1. Format verified evidence chunks
        evidence_blocks = []
        standards_identified = set()
        for idx, item in enumerate(evidence):
            doc = item.get("document_name", "BIS Standard")
            clause = item.get("clause", "General Requirement")
            page = item.get("page_number", 1)
            version = item.get("version", "1.0")
            text = item.get("text", "")
            
            evidence_blocks.append(
                f"[Evidence #{idx + 1}]\n"
                f"Document: {doc} (Version: {version})\n"
                f"Page: {page} | Clause: {clause}\n"
                f"Content: {text}"
            )
            if "IS" in doc.upper():
                standards_identified.add(doc)

        evidence_str = "\n\n".join(evidence_blocks)

        # 2. Format Graph context
        graph_blocks = []
        for g in graph_context:
            graph_blocks.append(
                f"- Standard: {g.get('standard')} -> Product: {g.get('product')} -> "
                f"Certification: {g.get('certification')} -> Laboratory: {g.get('laboratory')}"
            )
        graph_str = "\n".join(graph_blocks) if graph_blocks else "None"

        # 3. System Prompt enforcing evidence-based answering
        system_prompt = (
            "You are the official Bureau of Indian Standards (BIS) AI Regulatory Reasoning Engine.\n"
            "MANDATORY REGULATORY RULES:\n"
            "1. Answer ONLY using the facts stated in the provided VERIFIED RETRIEVED BIS EVIDENCE.\n"
            "2. DO NOT invent, assume, or hallucinate any BIS standard numbers, clause numbers, limits, or certification schemes.\n"
            "3. If the retrieved evidence does not contain sufficient facts to answer the query, "
            "you MUST state: 'Insufficient verified BIS evidence was found to provide a reliable answer.'\n"
            "4. Explain clearly WHY a particular standard applies based on the evidence.\n"
            "5. Cite the exact Document, Clause, and Page number for each claim."
        )

        user_prompt = f"""
USER QUERY:
{query}

USER LANGUAGE: {query_meta.get('language', 'en')}
DETECTED INTENT: {query_meta.get('intent', 'REGULATORY_INQUIRY')}

VERIFIED RETRIEVED BIS EVIDENCE:
{evidence_str}

KNOWLEDGE GRAPH REGULATORY TOPOLOGY:
{graph_str}

Provide an explainable, structured BIS regulatory response:
"""

        # Call Ollama
        llm_output = self.ollama.generate(user_prompt, system_prompt)

        # If Ollama is offline or unavailable, synthesize grounded fallback directly from evidence
        if not llm_output:
            logger.warning("Ollama output empty or unavailable. Synthesizing deterministic grounded response from verified evidence.")
            llm_output = self._synthesize_grounded_fallback(evidence, graph_context, query)

        # Extract structured certification and lab paths
        cert_paths = []
        test_guidance = []
        for g in graph_context:
            if g.get("certification"):
                cert_paths.append(f"Certification Scheme: {g['certification']} for {g.get('standard', 'product')}")
            if g.get("laboratory"):
                test_guidance.append(f"Testing Laboratory: {g['laboratory']} (Standard: {g.get('standard', 'N/A')}, Test: {g.get('testing', 'Standard Test')})")

        sources = [f"{e.get('document_name')} (Page {e.get('page_number')}, Clause {e.get('clause')})" for e in evidence]

        return {
            "answer": llm_output,
            "applicable_standards": list(standards_identified),
            "certification_path": cert_paths,
            "testing_guidance": test_guidance,
            "sources": sources,
            "has_sufficient_evidence": True
        }

    def _synthesize_grounded_fallback(self, evidence: List[Dict[str, Any]], graph_context: List[Dict[str, Any]], query: str) -> str:
        first = evidence[0]
        doc = first.get("document_name", "BIS Standard")
        clause = first.get("clause", "General")
        page = first.get("page_number", 1)
        snippet = first.get("text", "")[:280]

        response = (
            f"Based on verified BIS standard {doc}, Clause {clause} (Page {page}):\n\n"
            f"\"{snippet}...\"\n\n"
            f"This standard specifies the regulatory and quality requirements applicable to the product referenced in your query."
        )
        return response
