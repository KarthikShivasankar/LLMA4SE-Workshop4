"""The only file that talks to a model. Swap providers here, nowhere else."""
from openai import OpenAI
from . import config

_client = None

def chat(system: str, user: str) -> str:
    global _client
    if _client is None:
        _client = OpenAI()          # reads OPENAI_API_KEY
    resp = _client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        temperature=config.TEMPERATURE,
        max_tokens=config.MAX_TOKENS,
    )
    return (resp.choices[0].message.content or "").strip()