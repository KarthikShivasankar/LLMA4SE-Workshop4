# Workshop 4 · Hands-on: Building Cooperative LLM Agent Workflows
### for Anti-pattern Detection, Code Smell and Technical Debt Resolution

**LLMA4SE 2026** — 2nd International Summer School on LLM-based Agents for Software Engineering
Day 3 · **15:00 – 18:00**


---

## What's in this package

| File | What it is | Who it's for |
|---|---|---|
| `LLMA4SE_Workshop4_Colab.ipynb` | **The workshop.** One self-contained Google Colab notebook: all four parts, six agents, four static-analysis tools, a packaged CLI. Everything — key, installs, the `debtbuster` CLI — runs inside Colab. | Students — this is the only file they need |
| `LLMA4SE_Workshop4_Slides.pptx` | 20 lecture slides interleaved with the notebook sections. | Instructors (projected) |
| `instruction_note.md` | Minute-by-minute run of show, talking points, discussion prompts, troubleshooting. | Instructors |
| `students_handout.md` | Concepts, glossary, exercises, references — to keep. | Students (print or share) |
| `requirements.txt` | The dependency list (the notebook installs these itself). | Local runs / reference |
| `debtbuster/` | Offline **mirror** of the CLI package. Canonical source: [its own repo](https://github.com/KarthikShivasankar/debtbuster) — that is what Part 4 installs. | Reference only |

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
   - add `OPENAI_API_KEY` under Colab **Secrets** (🔑 in the left sidebar) and enable notebook access — *recommended*; add an optional second secret `OPENAI_MODEL` to pin the model;
   - let the notebook prompt you with a hidden input box.
3. Run cells top to bottom.

### What the markers in the notebook mean

The notebook is built to be *run*, not read. Five markers tell students what a cell wants from them:

| Marker | Action | Time |
|---|---|---|
| 🎯 **Predict** | edit a `MY_GUESS_…` line **before** running; the notebook grades the guess and keeps a running score | 30 s |
| 🧪 **Try it** | change one thing, re-run, watch what breaks | 1–3 min |
| 💬 **Discuss** | pair discussion, no single right answer | 1–2 min |
| ✍️ **Exercise** | code in the workspace cell; solutions in a `<details>` toggle | 10–15 min |
| ⏱ **Pit stop** | `pit_stop("Part 2")` prints elapsed vs. budgeted time and tells stragglers what to skip | 5 s |

There are four 🎯 predictions (complexity guessing, the sabotage gate, zero-shot accuracy, the CLI exit code)
and a `scoreboard()` at the end. Each Part closes with a cell that saves its result, so a student who falls
behind can skip the exercise and still start the next Part.

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

### `debtbuster` — the pipeline as a published package

Part 4 does **not** paste source into the notebook. Students `pip install` the real thing from its own public repository and drive it as a shell command:

```bash
pip install "git+https://github.com/KarthikShivasankar/debtbuster.git"

debtbuster audit inventory.py                            # deterministic only — no LLM, no cost
debtbuster fix   inventory.py --tests test_inventory.py  # the agent team, behind three gates
```

Repository: **[github.com/KarthikShivasankar/debtbuster](https://github.com/KarthikShivasankar/debtbuster)** (MIT).

The key reaches the subprocess through `os.environ`, exactly as it would in CI — nothing is baked into the package. `fix` exits **1** when the gate rejects and writes nothing, which is what makes it safe to put in a pipeline.

The notebook explains the package rather than reprinting it: what each of the six files does, which single file can hallucinate (`brain.py` — the other five are deterministic), and why the exit code is the real product.

## The two "patients" students operate on

- `inventory.py` — a working-but-smelly business module (mutable default arg, 7-param function, magic numbers, duplicated pricing logic, dead code) pinned by **7 behaviour tests**.
- `ml_project/train_model.py` — an ML training script with silent ML-specific smells (`== np.nan`, missing `optimizer.zero_grad()`, no seeds, no early stopping) that **MLScent** detects.

## Research tools featured

- **PyExamine** — *MSR 2025* · `pip install code-quality-analyzer` · [github.com/KarthikShivasankar/python_smells_detector](https://github.com/KarthikShivasankar/python_smells_detector)
- **MLScent** — *CAIN 2025* · `pip install ml-code-smell-detector` · [arXiv:2502.18466](https://arxiv.org/abs/2502.18466)
- **BEACon-TD / TD-Suite** — *JSS 2025* · [github.com/KarthikShivasankar/text_classification](https://github.com/KarthikShivasankar/text_classification)
- **debtbuster** — today's pipeline as an installable CLI · `pip install git+https://github.com/KarthikShivasankar/debtbuster.git` · [github.com/KarthikShivasankar/debtbuster](https://github.com/KarthikShivasankar/debtbuster)
- **tree-sitter** — the polyglot, incremental, error-tolerant parser §1.4 contrasts with Python's `ast` · [tree-sitter.github.io](https://tree-sitter.github.io/)



> **Deterministic tools measure, the LLM interprets, and a gate decides.** Everything else is plumbing.

For questions Contact: **Adela Nedisan Videsjorden** (SINTEF Digital)  & **Karthik Shivashankar** (SINTEF Digital)