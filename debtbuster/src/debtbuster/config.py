"""Single source of truth -- change the brain here, nowhere else."""
import os

MODEL = os.environ.get("LLM_MODEL", "openai/gpt-4o-mini")
MAX_ITERATIONS = 3
TEMPERATURE = 0.1
MAX_TOKENS = 2000
