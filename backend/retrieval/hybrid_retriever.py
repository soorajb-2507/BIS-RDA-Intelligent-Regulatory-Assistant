from typing import List, Dict, Any
from utils.logger import get_logger
from retrieval.elasticsearch_client import ElasticClient
from retrieval.qdrant_client import QdrantStoreClient
from retrieval.neo4j_client import Neo4jGraphClient

logger = get_logger("hybrid_retriever")

class HybridRetriever:
    """
    Orchestrates Hybrid Retrieval strictly across:
    1. Elasticsearch (Lexical / Keyword Search)
    2. Qdrant (Semantic / Vector Search)
    3. Neo4j (Knowledge Graph Topology & Relationships)
    
    Combines and reranks retrieved evidence using Reciprocal Rank Fusion (RRF).
    """
    def __init__(self):
        self.es_client = ElasticClient()
        self.qdrant_client = QdrantStoreClient()
        self.neo4j_client = Neo4jGraphClient()

    def retrieve(self, query_info: Dict[str, Any], top_k: int = 6) -> Dict[str, Any]:
        query_text = query_info.get("normalized_query", "")
        detected_standards = query_info.get("detected_standards", [])
        product_terms = query_info.get("product_terms", [])
        clause_numbers = query_info.get("detected_clauses", [])

        logger.info(f"Initiating Hybrid Retrieval for query: '{query_text}'")

        # 1. Elasticsearch Keyword Retrieval
        es_results = self.es_client.search_keywords(
            query=query_text,
            standards=detected_standards,
            clause_numbers=clause_numbers,
            product_terms=product_terms,
            limit=top_k
        )

        # 2. Qdrant Semantic Retrieval
        qdrant_results = self.qdrant_client.search_semantic(
            query=query_text,
            limit=top_k
        )

        # 3. Neo4j Graph Retrieval
        graph_results = self.neo4j_client.find_relationships(
            standards=detected_standards,
            products=product_terms
        )

        # 4. Rerank and Combine Evidence using Reciprocal Rank Fusion (RRF)
        fused_evidence = self._reciprocal_rank_fusion(es_results, qdrant_results)

        logger.info(
            f"Hybrid retrieval finished. ES: {len(es_results)}, Qdrant: {len(qdrant_results)}, "
            f"Neo4j: {len(graph_results)}, Combined: {len(fused_evidence)}"
        )

        return {
            "evidence": fused_evidence[:top_k],
            "graph_context": graph_results,
            "retrieval_stats": {
                "elasticsearch_hits": len(es_results),
                "qdrant_hits": len(qdrant_results),
                "neo4j_relationships": len(graph_results)
            }
        }

    def _reciprocal_rank_fusion(
        self,
        es_results: List[Dict[str, Any]],
        qdrant_results: List[Dict[str, Any]],
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """
        RRF algorithm: score(d) = sum(1 / (k + rank(d)))
        """
        scores: Dict[str, float] = {}
        items: Dict[str, Dict[str, Any]] = {}

        # Process ES results
        for rank, item in enumerate(es_results):
            key = self._chunk_key(item)
            scores[key] = scores.get(key, 0.0) + (1.0 / (k + rank + 1))
            items[key] = item

        # Process Qdrant results
        for rank, item in enumerate(qdrant_results):
            key = self._chunk_key(item)
            scores[key] = scores.get(key, 0.0) + (1.0 / (k + rank + 1))
            if key not in items:
                items[key] = item

        # Sort items by fused score
        sorted_keys = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        ranked_evidence = []
        for key in sorted_keys:
            doc = dict(items[key])
            doc["fused_score"] = scores[key]
            ranked_evidence.append(doc)

        return ranked_evidence

    def _chunk_key(self, chunk: Dict[str, Any]) -> str:
        doc = chunk.get("document_name", "")
        page = chunk.get("page_number", 0)
        clause = chunk.get("clause", "")
        text_prefix = chunk.get("text", "")[:40]
        return f"{doc}__p{page}__c{clause}__{text_prefix}"
