# src/llm/ollama_client.py
from __future__ import annotations
import os
from typing import List, Dict, Any

try:
    from ollama import Client as Ollama
except Exception as e: 
    Ollama = None


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except Exception:
        return default


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except Exception:
        return default


class OllamaClient:
    def __init__(self) -> None:
        if Ollama is None:
            raise RuntimeError("ollama package not installed. pip install ollama")
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "mistral")

        self.default_options: Dict[str, Any] = {
            "temperature": _float_env("OLLAMA_TEMPERATURE", 0.3),
            "top_p": _float_env("OLLAMA_TOP_P", 0.9),
            "num_ctx": _int_env("OLLAMA_NUM_CTX", 2048),
            "num_predict": _int_env("OLLAMA_NUM_PREDICT", 256),
           
        }

        self.client = Ollama(host=host)

    def chat(self, messages: List[Dict], **kwargs) -> str:
       
        user_options = kwargs.pop("options", {}) or {}
        options = {**self.default_options, **user_options}
        resp = self.client.chat(model=self.model, messages=messages, stream=False, options=options)
        return resp["message"]["content"].strip()
