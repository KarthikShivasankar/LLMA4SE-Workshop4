# Workshop 4 · Hands-on: Building Cooperative LLM Agent Workflows
### for Anti-pattern Detection, Code Smell and Technical Debt Resolution

**LLMA4SE 2026** — 2nd International Summer School on LLM-based Agents for Software Engineering
Day 3 · **15:00 – 18:00**

Instructors: **Karthik Shivashankar** (SINTEF Digital / University of Oslo) & **Adela Nedisan Videsjorden** (University of Oslo)
Contact: karthik13sankar@outlook.com

---

## What's in this package

| File | What it is | Who it's for |
|---|---|---|
| `LLMA4SE_Workshop4_Colab.ipynb` | **The workshop.** One self-contained Google Colab notebook: all four parts, six agents, four static-analysis tools, a packaged CLI. | Students — this is the only file they need |
| `LLMA4SE_Workshop4_Slides.pptx` | Lecture slides interleaved with the notebook sections. | Instructors (projected) |
| `instruction_note.md` | Minute-by-minute run of show, talking points, discussion prompts, troubleshooting. | Instructors |
| `students_handout.md` | Concepts, glossary, exercises, references — to keep. | Students (print or share) |
| `requirements.txt` | The dependency list (the notebook installs these itself). | Local runs / reference |

## Requirements

- A Google account and **free Google Colab**.
- An **OpenAI API key**. Budget: the full notebook costs roughly **$0.05–0.25 per student** on `gpt-4.1-mini`.
- **No GPU needed.** `Runtime → Change runtime type → CPU` is fine — the model lives behind the API.

Everything installs from one line:

```bash
pip install code-quality-analyzer ml-code-smell-detector radon pylint pytest pandas langgraph deepagents openai
```

*(Part 4's Deep Agents section adds `langchain-openai` in its own cell — `deepagents` reaches models through LangChain and needs the OpenAI binding.)*

## How to run it

1. Go to [colab.research.google.com](https://colab.research.google.com) → **File → Upload notebook** → pick `LLMA4SE_Workshop4_Colab.ipynb`.
2. Provide your API key **one** of three ways (the notebook tries them in order):
   - upload a `.env` file containing `OPENAI_API_KEY=sk-...` (optionally `OPENAI_MODEL=...`);
   - add `OPENAI_API_KEY` under Colab **Secrets** (🔑 in the left sidebar) and enable notebook access — *recommended*;
   - let the notebook prompt you with a hidden input box.
3. Run cells top to bottom.

> ⚠️ **Never paste a key into a code cell.** Notebooks get shared, committed and screenshotted.

## Choosing a model

`MODEL_NAME` is read from `OPENAI_MODEL` if your `.env` sets it, otherwise it defaults to `gpt-4.1-mini`.

| Model | Notes |
|---|---|
| `gpt-4.1-mini` | **Recommended for a live workshop.** Fast, cheap, good enough at long rewrites. |
| `gpt-4o-mini` | Cheapest; occasionally fails to return a complete module (which the QA gate catches — a teachable moment). |
| `gpt-4.1` | Strongest classic model; ~5× the cost. |
| `gpt-5.x`, `o*` | Reasoning models. Slower and pricier, but the best refactorers. The notebook's `llm()` detects them and switches to `max_completion_tokens`, dropping `temperature` — which those models reject. |

## What students build

Six agents, wired into one pipeline:

| # | Agent | Tools | Verified by |
|---|---|---|---|
| 1 | Code Auditor | radon · pylint · PyExamine | JSON contract |
| 2 | ML Auditor | MLScent | JSON contract |
| 3 | Refactorer | — | the QA gates |
| 4 | QA Verifier | ast · pytest · radon | *it is the verifier* |
| 5 | TD Classifier | — | gold labels |
| 6 | Triage Agent | — | human judgement |

Then the same pipeline is rebuilt in **LangGraph**, handed to an autonomous **Deep Agent**, and packaged as **`debtbuster`** — a `pip install`-able CLI that exits non-zero when the QA gate rejects, so it drops straight into CI.

## The two "patients" students operate on

- `inventory.py` — a working-but-smelly business module (mutable default arg, 7-param function, magic numbers, duplicated pricing logic, dead code) pinned by **7 behaviour tests**.
- `ml_project/train_model.py` — an ML training script with silent ML-specific smells (`== np.nan`, missing `optimizer.zero_grad()`, no seeds, no early stopping) that **MLScent** detects.

## Research tools featured

- **PyExamine** — *MSR 2025* · `pip install code-quality-analyzer` · [github.com/KarthikShivasankar/python_smells_detector](https://github.com/KarthikShivasankar/python_smells_detector)
- **MLScent** — *CAIN 2025* · `pip install ml-code-smell-detector` · [arXiv:2502.18466](https://arxiv.org/abs/2502.18466)
- **BEACon-TD / TD-Suite** — *JSS 2025* · [github.com/KarthikShivasankar/text_classification](https://github.com/KarthikShivasankar/text_classification)

## The thesis, in one sentence

> **Deterministic tools measure, the LLM interprets, and a gate decides.** Everything else is plumbing.
