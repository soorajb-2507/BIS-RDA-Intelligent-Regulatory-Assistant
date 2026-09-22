import os
from typing import List, Dict, Any, Tuple
from utils.logger import get_logger
from processing.ocr_engine import PaddleOCREngine
from processing.chunker import TextChunker
from processing.clause_extractor import extract_clauses

logger = get_logger("pdf_processor")

class DocumentProcessor:
    def __init__(self):
        self.ocr_engine = PaddleOCREngine()
        self.chunker = TextChunker()

    def process_pdf(
        self,
        file_path: str,
        doc_name: str,
        version: str = "1.0",
        doc_type: str = "Standard"
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Loads PDF using PyMuPDF. Checks if usable text exists per page.
        Falls back to PaddleOCR for scanned or low-text pages.
        Returns:
            (all_chunks, metadata_summary)
        """
        import fitz  # PyMuPDF

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        doc = fitz.open(file_path)
        page_count = len(doc)
        all_chunks = []
        is_scanned_doc = False
        scanned_pages = 0

        logger.info(f"Processing PDF '{doc_name}' ({page_count} pages) using PyMuPDF...")

        doc_meta = doc.metadata or {}

        for page_num in range(page_count):
            page = doc[page_num]
            text = page.get_text("text").strip()

            # Automatic check if usable text exists
            if len(text) < 50:
                logger.info(f"Page {page_num + 1} has insufficient text ({len(text)} chars). Triggering PaddleOCR fallback...")
                scanned_pages += 1
                try:
                    pix = page.get_pixmap(dpi=200)
                    img_bytes = pix.tobytes("png")
                    ocr_text = self.ocr_engine.extract_text_from_image(img_bytes)
                    if len(ocr_text.strip()) > len(text):
                        text = ocr_text
                except Exception as e:
                    logger.error(f"Failed to run OCR on page {page_num + 1}: {e}")

            clauses = extract_clauses(text)
            page_chunks = self.chunker.create_chunks(
                text=text,
                doc_name=doc_name,
                page_number=page_num + 1,
                version=version,
                doc_type=doc_type,
                clauses=clauses
            )
            all_chunks.extend(page_chunks)

        if scanned_pages > page_count / 2:
            is_scanned_doc = True

        doc.close()

        metadata_summary = {
            "document_name": doc_name,
            "version": version,
            "doc_type": doc_type,
            "page_count": page_count,
            "is_scanned": is_scanned_doc,
            "chunks_count": len(all_chunks),
            "pdf_metadata": doc_meta
        }

        logger.info(f"Completed processing '{doc_name}'. Generated {len(all_chunks)} chunks.")
        return all_chunks, metadata_summary
