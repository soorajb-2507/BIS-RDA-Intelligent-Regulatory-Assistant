# backend/processing/__init__.py
from .pdf_processor import DocumentProcessor
from .ocr_engine import PaddleOCREngine
from .chunker import TextChunker
from .clause_extractor import extract_clauses
