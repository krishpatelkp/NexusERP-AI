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

# Ollama connection settings
OLLAMA_BASE_URL = getattr(settings, "OLLAMA_BASE_URL", os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
OLLAMA_MODEL = getattr(settings, "OLLAMA_MODEL", os.getenv("OLLAMA_MODEL", "qwen3:8b"))
OLLAMA_TIMEOUT = int(getattr(settings, "OLLAMA_TIMEOUT", os.getenv("OLLAMA_TIMEOUT", "60")))

# Tool limits
MAX_LIMIT = int(getattr(settings, "MAX_LIMIT", os.getenv("MAX_LIMIT", "100")))
