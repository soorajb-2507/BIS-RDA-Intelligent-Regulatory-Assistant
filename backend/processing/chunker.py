import re
from typing import List, Dict, Any

class TextChunker:
    def __init__(self, chunk_size: int = 400, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def clean_text(self, text: str) -> str:
        """
        Normalizes whitespace, removes control characters, and standardizes punctuation.
        """
        if not text:
            return ""
        # Remove repeated hyphens or underscores (often headers/footers)
        text = re.sub(r'[-_]{3,}', ' ', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def create_chunks(
        self,
        text: str,
        doc_name: str,
        page_number: int,
        version: str = "1.0",
        doc_type: str = "Standard",
        clauses: List[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        cleaned = self.clean_text(text)
        words = cleaned.split()
        if not words:
            return []

        chunks = []
        clause_str = clauses[0]["clause_number"] if clauses and len(clauses) > 0 else "General"
        clause_title = clauses[0]["clause_title"] if clauses and len(clauses) > 0 else ""

        step = max(1, self.chunk_size - self.overlap)
        for i in range(0, len(words), step):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            # Check if a specific clause appears in this chunk
            active_clause = clause_str
            active_title = clause_title
            if clauses:
                for c in clauses:
                    if c["clause_number"] in chunk_text:
                        active_clause = c["clause_number"]
                        active_title = c["clause_title"]
                        break

            chunks.append({
                "document_name": doc_name,
                "page_number": page_number,
                "version": version,
                "doc_type": doc_type,
                "clause": active_clause,
                "clause_title": active_title,
                "source": f"{doc_name} (Ver {version}, Page {page_number})",
                "text": chunk_text
            })

        return chunks
