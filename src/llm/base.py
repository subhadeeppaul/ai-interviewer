# src/llm/base.py
from __future__ import annotations
from typing import List, Dict

from .ollama_client import OllamaClient


class LLMClient:
    def chat(self, messages: List[Dict], **kwargs) -> str:
        raise NotImplementedError


def build_llm() -> OllamaClient:
    return OllamaClient()
