# Workshop 4: Hands-on — Building Cooperative LLM Agent Workflows for Anti-pattern detection, Code Smell and Technical Debt Resolution
**LLMA4SE 2026** — 3 hours · CPU · OpenRouter.

Thesis: tools measure, the LLM interprets, a gate decides.

Smell detectors (install from PyPI; these *are* the GitHub repos):

- [PyExamine](https://github.com/KarthikShivasankar/python_smells_detector) — `code-quality-analyzer` (MSR 2025)
- [MLScent](https://github.com/KarthikShivasankar/ml_smells_detector) — `ml-code-smell-detector` (CAIN 2025)

## Files

| File | Who |
|---|---|
| `LLMA4SE_Workshop4_Colab.ipynb` | Students — the whole workshop (Colab or local Jupyter) |
| `instruction_note.md` | Instructors |
| `students_handout.md` | Students (keep) |
| `.env.example` | Copy to `.env` (never commit `.env`) |
| `requirements.txt` | Local install (optional; the notebook pip-installs) |
| `workshop_lib.py` | Source used to *build* the notebook; already inlined inside it |
| `debtbuster/` | Local OpenRouter-aware CLI — Part 4 is `pip install -e ./debtbuster` |

Regenerate the notebook after editing the builder: `python scripts/build_notebook.py`.

## Run

**Colab:** open the GitHub folder (so `debtbuster/` is next to the notebook) or upload both. CPU runtime. Part 4 runs `pip install -e ./debtbuster`.

**Local:**

```bash
cp .env.example .env   # then fill OPENROUTER_API_KEY
pip install -r requirements.txt
jupyter notebook LLMA4SE_Workshop4_Colab.ipynb
```

Key load order: `os.environ` / `.env` → Colab Secrets → hidden prompt. The notebook never reads `userdata` in the `llm()` cell.

## Provider

OpenRouter only. Client:

```python
from openai import OpenAI
OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
```

Any [OpenRouter slug](https://openrouter.ai/models) via `LLM_MODEL`. Default `openai/gpt-4o-mini`.

## Patients (real GitHub, pinned)

- [pallets/itsdangerous@2.2.0](https://github.com/pallets/itsdangerous) — `src/itsdangerous/timed.py` + `tests/test_itsdangerous/test_timed.py`
- [pytorch/examples](https://github.com/pytorch/examples) — `mnist/`
- Part 4 uses six public issues from Flask, Requests, HTTPX, Pylint, Django

## Tests

```bash
pytest tests/test_workshop_runtime.py tests/test_debtbuster_brain.py -q
```

Part 4 installs the **local** `./debtbuster` package (`OPENROUTER_API_KEY` + OpenRouter `base_url`). Do not `pip install git+https://github.com/KarthikShivasankar/debtbuster.git` for this session — that package still expects `OPENAI_API_KEY`.

Contact: **Adela Nedisan Videsjorden** & **Karthik Shivashankar** (SINTEF Digital)
