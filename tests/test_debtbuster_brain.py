"""debtbuster must talk to OpenRouter through openai.OpenAI, not api.openai.com."""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "debtbuster", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def test_brain_requires_openrouter_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    import debtbuster.brain as brain
    brain._client = None
    try:
        brain.chat("sys", "user")
        raise AssertionError("expected RuntimeError when key is missing")
    except RuntimeError as e:
        assert "OPENROUTER_API_KEY" in str(e)


def test_brain_client_uses_openrouter_url(monkeypatch):
    pytest.importorskip("openai")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    import debtbuster.brain as brain
    brain._client = None
    client = brain._client_or_make()
    assert "openrouter.ai" in str(client.base_url)


def test_config_model_comes_from_llm_model(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "anthropic/claude-sonnet-4")
    import importlib
    import debtbuster.config as config
    importlib.reload(config)
    assert config.MODEL == "anthropic/claude-sonnet-4"
