"""
==========================================================
NexusERP-AI — LLM Response Parser
==========================================================

Parses raw LLM text responses into structured data.
==========================================================
"""

import json
import re

from ai.exceptions import LLMResponseException


def parse_tool_selection(response_text: str) -> dict:
    """
    Parse the LLM's tool selection response into a dict.

    The LLM is prompted to return:
        {"tools": ["tool_name"], "reasoning": "..."}

    This function extracts that JSON even if the LLM
    wraps it in markdown code blocks.

    Parameters
    ----------
    response_text : str
        Raw text from OllamaClient.chat()

    Returns
    -------
    dict with keys: tools (list), reasoning (str)

    Raises
    ------
    LLMResponseException
        If valid JSON cannot be extracted.
    """

    # Strip markdown code blocks if present
    cleaned = re.sub(r"```(?:json)?", "", response_text).strip()
    cleaned = cleaned.strip("`").strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find JSON object within the text
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                raise LLMResponseException(
                    f"Cannot parse tool selection from: {response_text[:300]}"
                )
        else:
            raise LLMResponseException(
                f"No JSON found in tool selection response: {response_text[:300]}"
            )

    if "tools" not in data:
        raise LLMResponseException(
            f"Tool selection response missing 'tools' key: {data}"
        )

    return {
        "tools":     data.get("tools", []),
        "reasoning": data.get("reasoning", ""),
    }