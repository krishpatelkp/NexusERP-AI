"""
==========================================================
NexusERP-AI — Constants
==========================================================

This file contains configuration constants for the AI module.
They fallback to environment variables or standard defaults.
==========================================================
"""

import os
from django.conf import settings

# Ollama & Cloud LLM connection settings
OLLAMA_BASE_URL = getattr(settings, "OLLAMA_BASE_URL", os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
OLLAMA_MODEL = getattr(settings, "OLLAMA_MODEL", os.getenv("OLLAMA_MODEL", "qwen3:8b"))
OLLAMA_TIMEOUT = int(getattr(settings, "OLLAMA_TIMEOUT", os.getenv("OLLAMA_TIMEOUT", "60")))

# Cloud LLM API Keys (Groq / OpenAI)
GROQ_API_KEY = getattr(settings, "GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
GROQ_MODEL = getattr(settings, "GROQ_MODEL", os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
OPENAI_API_KEY = getattr(settings, "OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
OPENAI_MODEL = getattr(settings, "OPENAI_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

# Tool limits
MAX_LIMIT = int(getattr(settings, "MAX_LIMIT", os.getenv("MAX_LIMIT", "100")))

