# src/llm/base.py
from __future__ import annotations
from typing import List, Dict

from .ollama_client import OllamaClient


class LLMClient:
    def chat(self, messages: List[Dict], **kwargs) -> str:  # interface-like
        raise NotImplementedError


def build_llm() -> OllamaClient:
    # Ollama-only build
    return OllamaClient()
