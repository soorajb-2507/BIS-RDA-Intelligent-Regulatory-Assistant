import os
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger("elasticsearch_client")

STOP_WORDS = {
    "what", "is", "the", "for", "a", "an", "and", "or", "in", "on", "at", "to", "of", "with",
    "by", "under", "this", "that", "these", "those", "how", "which", "where", "when", "does",
    "standard", "standards", "bis", "requirement", "requirements", "specification", "specifications",
    "apply", "applies"
}

class ElasticClient:
    # Shared in-memory store across all instances when Elasticsearch service is offline
    _shared_in_memory_index: List[Dict[str, Any]] = []

    def __init__(self):
        url = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
        self.index_name = os.getenv("ELASTICSEARCH_INDEX", "bis_standards_index")
        self.client = None

        try:
            from elasticsearch import Elasticsearch
            self.client = Elasticsearch(url, request_timeout=5)
            if self.client.ping():
                logger.info(f"Connected to Elasticsearch at {url}")
                self._ensure_index()
            else:
                logger.warning(f"Elasticsearch ping failed at {url}. Operating with in-memory lexical fallback.")
                self.client = None
        except Exception as e:
            logger.warning(f"Elasticsearch connection failed: {e}. Operating with in-memory lexical fallback.")
            self.client = None

    def _ensure_index(self):
        try:
            if not self.client.indices.exists(index=self.index_name):
                mappings = {
                    "mappings": {
                        "properties": {
                            "document_name": {"type": "keyword"},
                            "standard_number": {"type": "keyword"},
                            "clause": {"type": "keyword"},
                            "clause_title": {"type": "text"},
                            "page_number": {"type": "integer"},
                            "version": {"type": "keyword"},
                            "doc_type": {"type": "keyword"},
                            "source": {"type": "keyword"},
                            "text": {"type": "text", "analyzer": "standard"}
                        }
                    }
                }
                self.client.indices.create(index=self.index_name, body=mappings)
                logger.info(f"Created Elasticsearch index: {self.index_name}")
        except Exception as e:
            logger.error(f"Error ensuring Elasticsearch index: {e}")

    def index_chunk(self, chunk: Dict[str, Any], doc_id: str):
        # Save to shared in-memory fallback cache (deduplicated)
        key = f"{chunk.get('document_name')}_{chunk.get('clause')}_{chunk.get('page_number')}"
        existing_keys = {f"{c.get('document_name')}_{c.get('clause')}_{c.get('page_number')}" for c in ElasticClient._shared_in_memory_index}
        if key not in existing_keys:
            ElasticClient._shared_in_memory_index.append(chunk)

        if self.client:
            try:
                self.client.index(index=self.index_name, id=doc_id, document=chunk)
            except Exception as e:
                logger.error(f"Failed to index chunk {doc_id} in Elasticsearch: {e}")

    def search_keywords(
        self,
        query: str,
        standards: List[str] = None,
        clause_numbers: List[str] = None,
        product_terms: List[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Performs lexical/keyword search: exact matching, clause numbers, standard numbers, product terms.
        """
        if self.client:
            try:
                should_clauses = [
                    {"match": {"text": {"query": query, "boost": 1.0}}},
                    {"match_phrase": {"text": {"query": query, "boost": 2.0}}}
                ]
                
                if standards:
                    for std in standards:
                        should_clauses.append({"term": {"standard_number": {"value": std, "boost": 3.0}}})
                        should_clauses.append({"match": {"text": {"query": std, "boost": 2.5}}})

                if clause_numbers:
                    for cl in clause_numbers:
                        should_clauses.append({"term": {"clause": {"value": cl, "boost": 3.0}}})

                if product_terms:
                    for prod in product_terms:
                        should_clauses.append({"match": {"text": {"query": prod, "boost": 1.5}}})

                body = {
                    "query": {"bool": {"should": should_clauses}},
                    "size": limit
                }

                res = self.client.search(index=self.index_name, body=body)
                hits = []
                for hit in res["hits"]["hits"]:
                    src = hit["_source"]
                    src["score"] = float(hit["_score"])
                    src["retrieval_method"] = "lexical_elasticsearch"
                    hits.append(src)
                return hits
            except Exception as e:
                logger.error(f"Elasticsearch search failed: {e}")

        # In-memory lexical search fallback
        return self._in_memory_search(query, standards, clause_numbers, product_terms, limit)

    def _in_memory_search(
        self,
        query: str,
        standards: List[str],
        clause_numbers: List[str],
        product_terms: List[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        results = []
        # Filter stop words so generic words don't trigger spurious matches
        q_tokens = {w for w in query.lower().split() if w not in STOP_WORDS and len(w) > 2}
        stds = [s.lower().replace(" ", "") for s in (standards or [])]
        clauses = [c.lower() for c in (clause_numbers or [])]

        for chunk in ElasticClient._shared_in_memory_index:
            text_lower = chunk.get("text", "").lower()
            doc_name = chunk.get("document_name", "").lower().replace(" ", "")
            std_no = chunk.get("standard_number", "").lower().replace(" ", "")
            clause = str(chunk.get("clause", "")).lower()

            score = 0.0
            # Meaningful token overlap
            if q_tokens:
                overlap = sum(1 for token in q_tokens if token in text_lower)
                if overlap > 0:
                    score += overlap / len(q_tokens)

            # Standard match boost
            if stds and any(s in doc_name or s in std_no for s in stds):
                score += 2.0

            # Clause match boost
            if clauses and any(c in clause for c in clauses):
                score += 1.5

            if score > 0.3:
                item = dict(chunk)
                item["score"] = score
                item["retrieval_method"] = "lexical_in_memory"
                results.append(item)

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
