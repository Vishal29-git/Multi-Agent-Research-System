import os
import json
import logging
import requests
from backend.config import settings

logger = logging.getLogger(__name__)

# Global cache for Ollama server availability check
_ollama_checked = False
_ollama_available = False

def check_ollama_available(base_url: str, model_name: str) -> bool:
    global _ollama_checked, _ollama_available
    if _ollama_checked:
        return _ollama_available

    _ollama_checked = True
    try:
        # Check if Ollama server responds and has the model loaded
        url = f"{base_url.rstrip('/')}/api/tags"
        resp = requests.get(url, timeout=0.5)
        if resp.status_code == 200:
            models_data = resp.json().get("models", [])
            model_names = [m.get("name", "") for m in models_data]
            # Verify if requested model is downloaded
            if any(model_name in m for m in model_names):
                _ollama_available = True
                logger.info(f"Ollama server & model '{model_name}' verified online at {base_url}")
            else:
                _ollama_available = False
                logger.info(f"Ollama running at {base_url} but model '{model_name}' not pulled. Using free local engine.")
        else:
            _ollama_available = False
    except Exception as e:
        _ollama_available = False
        logger.info(f"Ollama server not reachable at {base_url}: {e}. Using free local research engine.")
    return _ollama_available


class BaseAgent:
    def __init__(self, role_name: str):
        self.role_name = role_name
        self.ollama_url = settings.OLLAMA_BASE_URL.rstrip('/')
        self.model = settings.OLLAMA_MODEL

    def _call_ollama(self, prompt: str, system_prompt: str = "") -> str:
        global _ollama_available
        if not check_ollama_available(self.ollama_url, self.model):
            return ""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3
            }
        }
        try:
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=(1.0, 4.0))
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
        except Exception as e:
            logger.warning(f"Ollama generation timeout/error: {e}. Switching to free local engine.")
            _ollama_available = False
        return ""

    def generate_json(self, prompt: str, system_prompt: str = "", fallback_data: dict = None) -> dict:
        json_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY a valid, single JSON object with your response. Do not include markdown code blocks, backticks, or extra text."
        raw = self._call_ollama(json_prompt, system_prompt)
        
        if raw:
            cleaned = raw.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse LLM JSON output from {self.role_name}: {e}")

        return fallback_data or {}

    def generate_text(self, prompt: str, system_prompt: str = "", fallback_text: str = "") -> str:
        raw = self._call_ollama(prompt, system_prompt)
        if raw:
            return raw
        return fallback_text
