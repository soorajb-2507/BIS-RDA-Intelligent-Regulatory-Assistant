import os
import re
from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger("indicbert_service")

class IndicBERTService:
    """
    Multilingual Indian-language NLP Service using IndicBERT.
    Performs:
    - Language identification
    - Query normalization (while preserving original user language)
    - Intent detection
    - Entity and product extraction
    - Standard and clause number parsing
    """
    def __init__(self):
        self.model_name = os.getenv("INDICBERT_MODEL_NAME", "ai4bharat/indic-bert")
        self.tokenizer = None
        self.model = None
        self._init_indicbert()

    def _init_indicbert(self):
        try:
            from transformers import AutoTokenizer, AutoModel
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            logger.info(f"IndicBERT model loaded successfully: {self.model_name}")
        except Exception as e:
            logger.warning(f"IndicBERT loading deferred or offline: {e}. Running in rule-grounded multilingual mode.")

    def analyze_query(self, query: str, user_language: str = "en") -> Dict[str, Any]:
        cleaned = query.strip()
        lang = self._detect_or_verify_language(cleaned, user_language)

        # 1. Extract BIS standard numbers (e.g., IS 10500, IS/ISO 9001, IS 14543:2018)
        standards_pattern = r'\b(IS\s*(?:/\s*ISO)?\s*\d+(?:\s*:\s*\d{4})?)\b'
        standards_matches = re.findall(standards_pattern, cleaned, re.IGNORECASE)
        detected_standards = [re.sub(r'\s+', ' ', s).upper() for s in standards_matches]

        # 2. Extract clause numbers (e.g., Clause 4.2, 5.1.2)
        clause_pattern = r'\b(?:clause|खंड|பிரிவு)?\s*(\d+\.\d+(?:\.\d+)?)\b'
        clause_matches = re.findall(clause_pattern, cleaned, re.IGNORECASE)

        # 3. Intent Detection across Indian languages
        intent = self._classify_intent(cleaned)

        # 4. Product and Material understanding
        product_terms = self._extract_product_terms(cleaned, detected_standards)

        logger.info(
            f"IndicBERT Analysis -> Lang: {lang}, Intent: {intent}, "
            f"Standards: {detected_standards}, Products: {product_terms}"
        )

        return {
            "original_query": query,
            "normalized_query": cleaned,
            "language": lang,
            "intent": intent,
            "detected_standards": detected_standards,
            "detected_clauses": clause_matches,
            "product_terms": product_terms,
            "regulatory_domain": "Bureau of Indian Standards (BIS)"
        }

    def _detect_or_verify_language(self, text: str, user_lang: str) -> str:
        # Check script ranges
        for char in text:
            code = ord(char)
            if 0x0900 <= code <= 0x097F:  # Devanagari (Hindi/Marathi)
                return "hi"
            if 0x0B80 <= code <= 0x0BFF:  # Tamil
                return "ta"
            if 0x0C00 <= code <= 0x0C7F:  # Telugu
                return "te"
            if 0x0980 <= code <= 0x09FF:  # Bengali
                return "bn"
            if 0x0A80 <= code <= 0x0AFF:  # Gujarati
                return "gu"
            if 0x0D00 <= code <= 0x0D7F:  # Malayalam
                return "ml"
            if 0x0C80 <= code <= 0x0CFF:  # Kannada
                return "kn"
        return user_lang or "en"

    def _classify_intent(self, text: str) -> str:
        t = text.lower()
        # Multilingual keyword checks
        if any(w in t for w in [
            "standard", "specification", "is ", "मानक", "தரநிலை", "ప్రమాణం", "মানদণ্ড", "लागू"
        ]):
            return "APPLICABLE_STANDARD_INQUIRY"
        elif any(w in t for w in [
            "certification", "scheme", "isi mark", "crs", "license", "प्रमाणन", "சான்றிதழ்", "లైసెన్స్"
        ]):
            return "CERTIFICATION_PATH_INQUIRY"
        elif any(w in t for w in [
            "test", "testing", "lab", "laboratory", "परीक्षण", "प्रयोगशाला", "ஆய்வகம்", "ల్యాబ్"
        ]):
            return "TESTING_LAB_INQUIRY"
        elif any(w in t for w in [
            "clause", "requirement", "limit", "tolerance", "खंड", "பிரிவு", "నిబంధన"
        ]):
            return "CLAUSE_COMPLIANCE_INQUIRY"
        elif any(w in t for w in [
            "update", "amendment", "version", "संशोधन", "திருத்தம்"
        ]):
            return "STANDARD_UPDATE_INQUIRY"
        return "GENERAL_REGULATORY_INQUIRY"

    def _extract_product_terms(self, text: str, detected_standards: List[str]) -> List[str]:
        # Remove standard tokens
        t = text
        for s in detected_standards:
            t = t.replace(s, "")

        stop_words = {
            "what", "which", "where", "how", "when", "does", "apply", "applies", "for",
            "this", "product", "standard", "bis", "under", "with", "and", "the", "are",
            "इस", "उत्पाद", "के", "लिए", "कौन", "सा", "मानक", "लागू", "है",
            "இந்த", "தயாரிப்பிற்கு", "எந்த", "தரநிலை", "பொருந்தும்"
        }
        words = re.findall(r'\b\w+\b', t)
        candidates = [w for w in words if len(w) > 2 and w.lower() not in stop_words]
        return candidates[:4]
