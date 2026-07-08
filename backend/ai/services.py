"""
==========================================================
NexusERP-AI — AI Service
==========================================================

The main orchestrator for the AI module.

Flow:
    1. Receive question + context
    2. Planner selects tools
    3. Executor runs tools
    4. LLM generates natural language response
    5. Return response

This is the AI equivalent of your other service classes.
==========================================================
"""

import json

from ai.llm.ollama_client import OllamaClient
from ai.planner import Planner
from ai.executor import Executor
from ai.memory import ConversationMemory
from ai.prompts import SYSTEM_PROMPT, RESPONSE_PROMPT
from ai.tools.base import ToolContext
from ai.exceptions import AIException, LLMConnectionException


class AIService:
    """
    Main entry point for the AI module.

    Called by AIChatAPIView.
    Coordinates Planner, Executor, and LLM.
    """

    def __init__(self):
        from ai.tools import registry
        self.registry = registry
        self.client = OllamaClient()
        self.planner = Planner(self.client, self.registry)
        self.executor = Executor(self.registry)

    def chat(
        self,
        question: str,
        company,
        user,
        conversation_history: list = None,
    ) -> dict:
        """
        Process a chat message and return the AI response.

        Parameters
        ----------
        question : str
            The user's natural language question.

        company : Company instance
            Used for data isolation in all tools.

        user : User instance
            The authenticated user.

        conversation_history : list, optional
            Previous messages for context.

        Returns
        -------
        dict
            {
                "response":     str,   — natural language answer
                "tools_used":   list,  — tool names that ran
                "tool_results": list,  — raw structured data
                "success":      bool,
            }
        """

        context = ToolContext(
            company=company,
            user=user,
        )

        # ── Step 1: Check Ollama is available ─────────────
        if not self.client.is_available():
            return {
                "response": (
                    "I'm currently unable to connect to the AI model. "
                    "Please ensure Ollama is running and try again."
                ),
                "tools_used":   [],
                "tool_results": [],
                "success":      False,
            }

        # ── Step 2: Plan — choose tools ───────────────────
        try:
            tool_names = self.planner.plan(question)
        except Exception as exc:
            return {
                "response": (
                    "I had trouble understanding your question. "
                    "Could you rephrase it?"
                ),
                "tools_used":   [],
                "tool_results": [],
                "success":      False,
            }

        # ── Step 3: Execute tools ─────────────────────────
        tool_results = []
        tools_used = []

        if tool_names:
            results = self.executor.execute(
                tool_names=tool_names,
                context=context,
            )

            for result in results:
                tools_used.append(result.tool)
                tool_results.append(result.to_dict())

        # ── Step 4: Build messages for LLM ───────────────
        tool_results_text = json.dumps(
            tool_results,
            indent=2,
            default=str,
        )

        response_prompt = RESPONSE_PROMPT.format(
            question=question,
            tool_results=tool_results_text,
        )

        messages = [
            {
                "role":    "system",
                "content": SYSTEM_PROMPT,
            },
        ]

        # Add conversation history for context
        if conversation_history:
            messages.extend(conversation_history)

        messages.append({
            "role":    "user",
            "content": response_prompt,
        })

        # ── Step 5: Get LLM response ──────────────────────
        try:
            response_text = self.client.chat(
                messages=messages,
                temperature=0.3,
            )
        except LLMConnectionException as exc:
            return {
                "response":     str(exc),
                "tools_used":   tools_used,
                "tool_results": tool_results,
                "success":      False,
            }

        return {
            "response":     response_text,
            "tools_used":   tools_used,
            "tool_results": tool_results,
            "success":      True,
        }