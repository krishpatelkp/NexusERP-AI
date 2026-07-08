"""
==========================================================
NexusERP-AI — Exceptions
==========================================================

This file contains custom exception classes for the AI module.
==========================================================
"""

class AIException(Exception):
    """Base exception class for the AI module."""
    pass


class LLMConnectionException(AIException):
    """Raised when the AI service cannot connect to the LLM (e.g. Ollama)."""
    pass


class LLMResponseException(AIException):
    """Raised when the LLM returns an unexpected or invalid response format."""
    pass


class PlannerException(AIException):
    """Raised when the planner fails to construct a valid execution plan."""
    pass


class ToolNotFoundException(AIException):
    """Raised when a requested tool is not found in the registry."""
    pass
