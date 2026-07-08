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
)
from ai.exceptions import (
    LLMConnectionException,
    LLMResponseException,
)


# ==========================================================
# OLLAMA CLIENT
# ==========================================================

class OllamaClient:
    """
    Thin client for the Ollama API.

    Responsibilities:
        - Send prompts to Ollama
        - Return raw text responses
        - Handle connection errors cleanly

    This class does NOT:
        - Build prompts (that is prompt_builder.py)
        - Parse responses (that is parser.py)
        - Choose tools (that is planner.py)
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

    def chat(
        self,
        messages: list,
        temperature: float = 0.1,
        stream: bool = False,
    ) -> str:
        """
        Send a list of messages to Ollama and return
        the assistant's response as a string.

        Parameters
        ----------
        messages : list of dict
            Each dict must have "role" and "content".
            Example:
                [
                    {"role": "system",    "content": "..."},
                    {"role": "user",      "content": "..."},
                    {"role": "assistant", "content": "..."},
                ]

        temperature : float
            Lower = more deterministic (default 0.1 for tool use).

        stream : bool
            Always False for now. Streaming is a future feature.

        Returns
        -------
        str
            The assistant's reply text.

        Raises
        ------
        LLMConnectionException
            If Ollama is not running or unreachable.

        LLMResponseException
            If Ollama returns an unexpected response format.
        """

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
                "Make sure Ollama is running."
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
        Returns True if Ollama is reachable.
        Used by the health check endpoint.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )
            return response.status_code == 200
        except Exception:
            return False