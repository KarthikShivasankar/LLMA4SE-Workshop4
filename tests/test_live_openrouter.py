"""Optional live call. Loads the parent .env; never prints the key."""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import workshop_lib as wl


@pytest.mark.integration
def test_live_openrouter_smoke():
    wl.reset_client()
    wl.load_dotenv()
    if not os.environ.get("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY not set")
    text = wl.llm("Reply with the single word: ok", max_new_tokens=16, temperature=0.0)
    assert isinstance(text, str)
    # Free / reasoning models may return empty; the call must not raise.
