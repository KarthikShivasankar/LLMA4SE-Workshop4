"""The only file that talks to a model. OpenRouter via the official openai client."""
import os
from . import config

_client = None
OPENROUTER_URL = "https://openrouter.ai/api/v1"


def _client_or_make():
    global _client
    if _client is None:
        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. Export it or load a .env before running debtbuster."
            )
        from openai import OpenAI
        _client = OpenAI(
            api_key=key,
            base_url=os.environ.get("OPENROUTER_BASE_URL", OPENROUTER_URL),
            default_headers={
                "HTTP-Referer": "https://github.com/KarthikShivasankar/debtbuster",
                "X-Title": "debtbuster",
            },
        )
    return _client


def chat(system: str, user: str) -> str:
    resp = _client_or_make().chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        temperature=config.TEMPERATURE,
        max_tokens=config.MAX_TOKENS,
    )
    usage = getattr(resp, "usage", None)
    # usage is often None on OpenRouter — ignore it
    _ = usage
    choices = getattr(resp, "choices", None) or []
    if not choices:
        return ""
    return (choices[0].message.content or "").strip()
