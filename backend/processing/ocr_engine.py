import numpy as np
from utils.logger import get_logger

logger = get_logger("ocr_engine")

class PaddleOCREngine:
    def __init__(self):
        self.ocr = None
        self._initialize_paddle()

    def _initialize_paddle(self):
        try:
            from paddleocr import PaddleOCR
            # Initialize with English and Indian language support (Devanagari)
            self.ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            logger.info("PaddleOCR engine initialized successfully.")
        except Exception as e:
            logger.warning(f"PaddleOCR failed to initialize: {e}. OCR will operate in fallback mode.")
            self.ocr = None

    def extract_text_from_image(self, img_bytes: bytes) -> str:
        """
        Extracts text from image bytes using PaddleOCR.
        """
        if not self.ocr:
            logger.warning("OCR engine not available; returning empty OCR text.")
            return ""

        try:
            import cv2
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            result = self.ocr.ocr(img, cls=True)
            extracted_lines = []
            if result and len(result) > 0 and result[0]:
                for line in result[0]:
                    text = line[1][0]
                    confidence = line[1][1]
                    if confidence > 0.4:
                        extracted_lines.append(text)
            
            return "\n".join(extracted_lines)
        except Exception as e:
            logger.error(f"Error during OCR extraction: {e}")
            return ""
