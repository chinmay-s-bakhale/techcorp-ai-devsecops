"""Thin client for the local Ollama server."""
import os

import requests

import config

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")

# System prompt is supplied through the environment, never hardcoded in source
SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", "")


def ask(user_message):
    """Send one prompt to the model and return its text response."""
    payload = {
        "model": MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": user_message,
        "stream": False,
    }
    headers = {"Authorization": "Bearer " + config.API_KEY} if config.API_KEY else {}
    try:
        r = requests.post(OLLAMA_URL, json=payload, headers=headers, timeout=120)
        r.raise_for_status()
        return r.json().get("response", "")
    except requests.RequestException as exc:
        return "LLM backend error: " + str(exc)
