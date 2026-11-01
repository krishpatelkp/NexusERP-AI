"""
==========================================================
NexusERP-AI — Ollama Client
==========================================================

This is the only file that talks to Ollama.
Nothing else in the AI module communicates
with the LLM directly.
==========================================================
"""

import json
import requests

from ai.constants import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    GROQ_API_KEY,
    GROQ_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)
from ai.exceptions import (
    LLMConnectionException,
    LLMResponseException,
)


# ==========================================================
# OLLAMA & CLOUD LLM CLIENT
# ==========================================================

class OllamaClient:
    """
    Thin client for Ollama API & Cloud LLM Providers (Groq / OpenAI).

    Responsibilities:
        - Send prompts to Groq / OpenAI (if API key present) or local Ollama
        - Return raw text responses
        - Handle connection errors cleanly
    """

    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_MODEL,
        timeout: int = OLLAMA_TIMEOUT,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._chat_url = f"{self.base_url}/api/chat"

    def _chat_cloud_openai(self, api_key: str, endpoint: str, model: str, messages: list, temperature: float) -> str:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            raise LLMConnectionException(f"Cloud LLM API error ({endpoint}): {exc}")

        try:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise LLMResponseException(f"Invalid response from Cloud LLM API: {exc}")


    def chat(
        self,
        messages: list,
        temperature: float = 0.1,
        stream: bool = False,
    ) -> str:
        """
        Send a list of messages to Cloud API (Groq/OpenAI) or local Ollama.
        """
        # Priority 1: Groq Cloud API
        if GROQ_API_KEY:
            return self._chat_cloud_openai(
                api_key=GROQ_API_KEY,
                endpoint="https://api.groq.com/openai/v1/chat/completions",
                model=GROQ_MODEL,
                messages=messages,
                temperature=temperature,
            )

        # Priority 2: OpenAI Cloud API
        if OPENAI_API_KEY:
            return self._chat_cloud_openai(
                api_key=OPENAI_API_KEY,
                endpoint="https://api.openai.com/v1/chat/completions",
                model=OPENAI_MODEL,
                messages=messages,
                temperature=temperature,
            )

        # Priority 3: Local Ollama
        payload = {
            "model":    self.model,
            "messages": messages,
            "stream":   stream,
            "options": {
                "temperature": temperature,
            },
        }

        try:
            response = requests.post(
                self._chat_url,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

        except requests.exceptions.ConnectionError:
            raise LLMConnectionException(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running or set GROQ_API_KEY in environment."
            )

        except requests.exceptions.Timeout:
            raise LLMConnectionException(
                f"Ollama request timed out after {self.timeout}s."
            )

        except requests.exceptions.HTTPError as exc:
            raise LLMConnectionException(
                f"Ollama returned HTTP error: {exc}"
            )

        try:
            data = response.json()
            return data["message"]["content"]

        except (KeyError, json.JSONDecodeError) as exc:
            raise LLMResponseException(
                f"Unexpected Ollama response format: {exc}\n"
                f"Raw response: {response.text[:500]}"
            )

    def is_available(self) -> bool:
        """
        Returns True if Cloud LLM API key is present or local Ollama is reachable.
        """
        if GROQ_API_KEY or OPENAI_API_KEY:
            return True

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )
            return response.status_code == 200
        except Exception:
            return False