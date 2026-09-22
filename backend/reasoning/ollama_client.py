import os
import requests
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger("ollama_client")

class OllamaClient:
    """
    Ollama Local LLM Client.
    Connects strictly to local Ollama instance (Qwen / Llama).
    Does NOT call any external LLM API.
    """
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
        self._check_connection()

    def _check_connection(self):
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if resp.status_code == 200:
                logger.info(f"Connected to Ollama service at {self.base_url}. Model: {self.model}")
            else:
                logger.warning(f"Ollama returned status {resp.status_code} at {self.base_url}.")
        except Exception as e:
            logger.warning(f"Ollama service connection deferred or offline at {self.base_url}: {e}")

    def generate(self, prompt: str, system_prompt: str) -> Optional[str]:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for strict factual accuracy
                "top_p": 0.9
            }
        }
        try:
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.json().get("response", "").strip()
            else:
                logger.error(f"Ollama request failed with status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")

        return None
