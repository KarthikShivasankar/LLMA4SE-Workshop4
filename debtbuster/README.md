# debtbuster (workshop copy)

OpenRouter via `openai.OpenAI(base_url=https://openrouter.ai/api/v1)`.

```bash
pip install -e .
export OPENROUTER_API_KEY=sk-or-...
export LLM_MODEL=openai/gpt-4o-mini
debtbuster audit path/to/module.py
debtbuster fix   path/to/module.py --tests path/to/test_module.py
```

This folder is what Part 4 installs (`pip install -e ./debtbuster`). The standalone GitHub package may still read `OPENAI_API_KEY`.
