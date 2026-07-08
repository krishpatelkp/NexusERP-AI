"""
==========================================================
NexusERP-AI — Planner
==========================================================

The Planner decides which tools to run for a given question.

Responsibilities:
    - Receive the user's question
    - Ask the LLM which tools to use
    - Return an ordered list of tool names

The Planner does NOT:
    - Run tools
    - Query the database
    - Build the final response
==========================================================
"""

import json

from ai.llm.ollama_client import OllamaClient
from ai.llm.parser import parse_tool_selection
from ai.prompts import TOOL_SELECTION_PROMPT
from ai.exceptions import PlannerException


class Planner:
    """
    Uses the LLM to decide which tools answer the question.

    Parameters
    ----------
    client : OllamaClient
    registry : ToolRegistry
    """

    def __init__(self, client: OllamaClient, registry):
        self.client = client
        self.registry = registry

    def plan(self, question: str) -> list:
        """
        Given a user question, return an ordered list
        of tool names to execute.

        Parameters
        ----------
        question : str

        Returns
        -------
        list of str
            Tool names in execution order.

        Raises
        ------
        PlannerException
            If the LLM fails to return a valid plan.
        """

        # Build the tool list description for the LLM
        tool_descriptions = self.registry.list_for_llm()

        tool_list_text = "\n".join([
            f"- {t['name']}: {t['description']}"
            for t in tool_descriptions
        ])

        prompt = TOOL_SELECTION_PROMPT.format(
            tool_list=tool_list_text,
            question=question,
        )

        messages = [
            {
                "role":    "user",
                "content": prompt,
            }
        ]

        try:
            response_text = self.client.chat(
                messages=messages,
                temperature=0.0,
            )
            parsed = parse_tool_selection(response_text)
            return parsed.get("tools", [])

        except Exception as exc:
            raise PlannerException(
                f"Planner failed to select tools: {exc}"
            )