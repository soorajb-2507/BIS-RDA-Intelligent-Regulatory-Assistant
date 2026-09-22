import os
import uuid
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger("qdrant_client")

class QdrantStoreClient:
    # Shared in-memory vectors across all instances when Qdrant service is offline
    _shared_in_memory_vectors: List[Dict[str, Any]] = []

    def __init__(self):
        host = os.getenv("QDRANT_HOST", "qdrant")
        port = int(os.getenv("QDRANT_PORT", "6333"))
        self.collection_name = os.getenv("QDRANT_COLLECTION", "bis_chunks_collection")
        self.client = None
        self.embedder = None

        self._init_embedder()
        self._init_qdrant(host, port)

    def _init_embedder(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("SentenceTransformer embedder initialized.")
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer: {e}. Semantic search will use fallback embeddings.")

    def _init_qdrant(self, host: str, port: int):
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams
            self.client = QdrantClient(host=host, port=port, timeout=5)
            
            # Check or create collection
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Connected to Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.warning(f"Qdrant connection failed: {e}. Operating with in-memory semantic fallback.")
            self.client = None

    def upsert_chunk(self, chunk: Dict[str, Any]):
        key = f"{chunk.get('document_name')}_{chunk.get('clause')}_{chunk.get('page_number')}"
        existing_keys = {
            f"{c['payload'].get('document_name')}_{c['payload'].get('clause')}_{c['payload'].get('page_number')}"
            for c in QdrantStoreClient._shared_in_memory_vectors
        }
        
        vector = self._get_embedding(chunk.get("text", ""))
        point_id = str(uuid.uuid4())

        if key not in existing_keys:
            QdrantStoreClient._shared_in_memory_vectors.append({
                "id": point_id,
                "vector": vector,
                "payload": chunk
            })

        if self.client and vector:
            try:
                from qdrant_client.models import PointStruct
                point = PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=chunk
                )
                self.client.upsert(collection_name=self.collection_name, points=[point])
            except Exception as e:
                logger.error(f"Qdrant upsert error: {e}")

    def search_semantic(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        query_vec = self._get_embedding(query)
        if not query_vec:
            return []

        if self.client:
            try:
                hits = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vec,
                    limit=limit
                )
                results = []
                for hit in hits:
                    if float(hit.score) >= 0.40:  # Minimum relevance score
                        payload = dict(hit.payload)
                        payload["score"] = float(hit.score)
                        payload["retrieval_method"] = "semantic_qdrant"
                        results.append(payload)
                return results
            except Exception as e:
                logger.error(f"Qdrant search error: {e}")

        # In-memory cosine similarity fallback
        return self._in_memory_similarity_search(query_vec, limit)

    def _get_embedding(self, text: str) -> List[float]:
        if self.embedder:
            try:
                return self.embedder.encode(text).tolist()
            except Exception as e:
                logger.error(f"Embedding generation error: {e}")
        # Deterministic fallback vector
        import hashlib
        h = hashlib.sha256(text.encode('utf-8')).digest()
        base = [float(b) / 255.0 for b in h]
        return (base * (384 // len(base) + 1))[:384]

    def _in_memory_similarity_search(self, query_vec: List[float], limit: int) -> List[Dict[str, Any]]:
        import numpy as np
        if not QdrantStoreClient._shared_in_memory_vectors:
            return []

        q = np.array(query_vec[:384])
        norm_q = np.linalg.norm(q)
        if norm_q == 0:
            return []

        scored = []
        for item in QdrantStoreClient._shared_in_memory_vectors:
            v = np.array(item["vector"][:384])
            norm_v = np.linalg.norm(v)
            if norm_v > 0:
                sim = float(np.dot(q, v) / (norm_q * norm_v))
                if sim >= 0.40:  # Enforce minimum semantic relevance
                    payload = dict(item["payload"])
                    payload["score"] = sim
                    payload["retrieval_method"] = "semantic_in_memory"
                    scored.append(payload)

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]
