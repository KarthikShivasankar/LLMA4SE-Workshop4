# Workshop 4: Hands-on — Building Cooperative LLM Agent Workflows for Anti-pattern detection, Code Smell and Technical Debt Resolution
**LLMA4SE 2026** — 3 hours · CPU · OpenRouter + official `openai` client.

Thesis: **tools measure · the LLM interprets · a gate decides.**

Smell detectors (install from PyPI; these *are* the GitHub repos):

- [PyExamine](https://github.com/KarthikShivasankar/python_smells_detector) — `code-quality-analyzer` (MSR 2025). CLI: `analyze_code_quality`
- [MLScent](https://github.com/KarthikShivasankar/ml_smells_detector) — `ml-code-smell-detector` (CAIN 2025). CLI: `ml_smell_detector`

## Files

| File | Who |
|---|---|
| `LLMA4SE_Workshop4_Colab.ipynb` | Students — the whole workshop (Colab or local Jupyter). Runtime and a `debtbuster/` snapshot are inlined. |
| `LLMA4SE_Workshop4_Slides.pptx` | Instructors — room slides |
| `instruction_note.md` | Instructors |
| `students_handout.md` | Students (keep open) |

## Run

**Colab:** CPU runtime. Open the `.ipynb`. Ignore *Restart session* and the `google-auth` warning after the pip cell. Do **not** `git clone` into `/content/LLMA4SE-Workshop4` (that was the exit-128 failure). Part 4 writes `debtbuster/` from the embedded snapshot if the folder is missing.

**Local:** create a `.env` next to the notebook (never commit it):

```
OPENROUTER_API_KEY=sk-or-...
LLM_MODEL=openai/gpt-5.6-luna
```

Then open `LLMA4SE_Workshop4_Colab.ipynb` in Jupyter and run Part 0. The notebook pip-installs its own stack.

Key load order: `os.environ` / `.env` → Colab Secrets → hidden prompt. Never paste a key into a code cell.

## Provider

OpenRouter only. Client:

```python
from openai import OpenAI
OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
```

Any [OpenRouter slug](https://openrouter.ai/models) via `LLM_MODEL` + `switch_model("provider/slug")`. If you stay on OpenAI, use **only** `openai/gpt-5.6-luna` (the workshop default). That slug needs `max_completion_tokens` and `reasoning_effort="low"` — `llm()` already does this. Do not start on a free slug; that was the empty-reply / 0-findings failure.

## 3-hour map

| Time | Part | Students should see |
|---|---|---|
| 0:00–0:25 | 0 Setup + basics | a sentence back from `llm()` |
| 0:25–1:10 | 1 Parse then measure | `ast` walk; PyExamine on PayFlow; MLScent on the churn trainer |
| 1:10–1:50 | 2 Cooperative team | auditor → planner → refactorer → QA; sabotage caught by pytest |
| 1:50–2:30 | 3 Frameworks | LangChain / LangGraph (live graph) / Deep Agents + two subagents |
| 2:30–2:55 | 4 Debt and ship | six issues + `TECH_DEBT_REPORT.md` + `python -m debtbuster` |
| 2:55–3:00 | Wrap | three takeaways |

## Case study (written by the notebook — no git clone)

- **PayFlow** — `cases/payflow/checkout.py` + `test_checkout.py` (invoice charge / refund). Sabotage flips the refund-cap `>` check.
- **Churn trainer** — `cases/churn/train_churn.py` (scaler leakage, missing seed, train score reported)
- Part 4 classifies and triages six public issues from Flask, Requests, HTTPX, Pylint, and Django (`priority = interest ÷ principal`)

Contact: **Adela Nedisan Videsjorden** & **Karthik Shivashankar** (SINTEF Digital)
