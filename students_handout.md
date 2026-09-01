# Student Handout — Building Cooperative LLM Agent Workflows
### LLMA4SE 2026 · Workshop 4 · Karthik Shivashankar & Adela Nedisan Videsjorden

Keep this. Everything you build today runs in **one Colab notebook** and fits in your head.

> **The idea:** deterministic tools *measure*, LLMs *interpret*, verification gates *decide*.
> Architecture beats model choice — you will prove this to yourself by 18:00.

---

## 0 · Setup, in 60 seconds

1. Open `LLMA4SE_Workshop4_Colab.ipynb` in Colab. **Runtime → CPU is fine** — no GPU needed.
2. Give it your OpenAI key, one of three ways:
   - a `.env` file with `OPENAI_API_KEY=sk-...` (upload via the 📁 sidebar), or
   - Colab **Secrets** (🔑 sidebar) → `OPENAI_API_KEY` → enable notebook access ← *recommended*, or
   - let it prompt you (hidden input).
3. Run Part 0. When a sentence about code smells comes back, you are ready.

> ⚠️ **Never paste a key into a code cell.** Notebooks get shared, committed and screenshotted.
> 💰 The whole notebook costs roughly **$0.05–0.25**. `cost_report()` shows the running total any time.

---

## 1 · Core concepts

**Code smell.** A surface symptom of a deeper design problem (Fowler). *Not a bug* — the code works. Today's examples: mutable default arguments, magic numbers, long parameter lists, duplicated logic, dead code.

**Anti-pattern.** A commonly used solution that looks reasonable and is reliably counterproductive — a smell with a name and a story.

**Technical debt** (Cunningham, 1992). The cost of choosing the quick option now.
- **Principal** = effort to fix it properly, once.
- **Interest** = the recurring drag until you do.
Studies put the waste at roughly **23–42% of development time**. Triage rule from Part 3: `priority = interest ÷ principal`. High interest, low principal = your quick wins.

**ML-specific smells.** A category classic linters cannot see: missing random seeds (unreproducible results), `x == np.nan` (always `False` — the branch never runs), missing `optimizer.zero_grad()` (gradients accumulate → wrong training), no early stopping / checkpointing / `model.eval()`. They rarely crash; they silently corrupt *science*. Detected today by **MLScent** (76 detectors).

**Agent** — our minimal, framework-free definition. Four ingredients:
1. a **role** — the system prompt that sets values and output rules;
2. a **brain** — the LLM (one `llm()` helper, shared by every agent);
3. **tools** — plain Python callables that produce *evidence*;
4. a **contract** — a strict JSON or code-block schema, so the next agent can **parse**, not *read*.

Change the role and the tools, keep the skeleton: that is how the Code Auditor became the ML Auditor in two cells.

**Blackboard state.** Every agent reads and writes one shared `WorkflowState` with a `record()` audit trail — a flight recorder for the workflow. The alternative is message passing (agents talk point-to-point). Blackboard wins on **auditability** for small teams; message passing scales to larger, decoupled ones.

**Verification gates.** Part 2's QA agent deliberately contains **no LLM**:

| Gate | Cost | Catches |
|---|---|---|
| 1 · `ast.parse` | microseconds | broken syntax, truncated output |
| 2 · `pytest` in a sandbox | ~1 second | **behaviour changes** — the dangerous ones |
| 3 · complexity delta | ~1 second | "refactorings" that made things worse |

Cheapest gate first: fail fast, spend compute only on survivors. Rejections loop back to the Refactorer **with the failure reason attached** — that feedback is what makes iteration 2 smarter than iteration 1.

Remember the sabotage demo: a plausible patch that changed the VAT rate from 0.25 to 0.20 sailed past human-style review and died at gate 2 in one second. **Never let the fox audit the henhouse.**

---

## 2 · The five agentic failure patterns

| Pattern | Symptom | Mitigation you built |
|---|---|---|
| **Plausible-but-wrong code** | patch looks perfect, silently changes a constant | gate 2 — behaviour tests |
| **Contract drift** | prose instead of JSON / a code block | strict parser + retry |
| **Reward hacking** | "simplifies" by deleting features | gates 2 and 3 together |
| **Runaway loops** | agent retries forever, burning budget | `max_iterations` |
| **Unverifiable claims** | "I refactored it safely!" | **no LLM inside the verifier** |

---

## 3 · The six agents you build

| # | Agent | Tools | Output contract | Verified by |
|---|---|---|---|---|
| 1 | Code Auditor | radon · pylint · PyExamine | JSON findings | the contract itself |
| 2 | ML Auditor | MLScent | JSON findings | the contract itself |
| 3 | Refactorer | — | one fenced code block | the QA gates |
| 4 | QA Verifier | ast · pytest · radon | verdict dict | *it is the verifier* |
| 5 | TD Classifier | — | one label from a closed set | gold labels |
| 6 | Triage Agent | — | `{interest, principal, rationale}` | human judgement |

Then in Part 4 the same team is rebuilt three ways — **LangGraph**, an autonomous **Deep Agent**, and the `debtbuster` CLI — and the QA gates stay byte-for-byte identical. That is the punchline: **verification is a property of the task, not of the framework.**

---

## 4 · The tools (your agents' senses)

| Tool | Install | What it sees | Where the output goes |
|---|---|---|---|
| `radon` | `pip install radon` | cyclomatic complexity, maintainability index | stdout |
| `pylint` | `pip install pylint` | ~400 lint rules, incl. `dangerous-default-value` | stdout (JSON) |
| **PyExamine** | `pip install code-quality-analyzer` | 49 metrics across code / structural / architectural levels | **`pyexamine_report.txt`** |
| **MLScent** | `pip install ml-code-smell-detector` | 76 ML anti-patterns (PyTorch, TF, sklearn, pandas, numpy, HF) | **`output/analysis_report.txt`** |

> 🐛 The two research tools write **files**, not stdout. If a tool "produced no report", check the file path.

---

## 5 · Exercises

| # | Where | Task |
|---|---|---|
| **1** | §1.6 | Write an AST tool that finds magic numbers, register it on the auditor, re-audit. *Lesson: capability grows through **tools**, not bigger models.* |
| **2A** | §2.6 | Add a Documenter agent — docstrings only, nothing else changed — and push its output through the same gate. |
| **2B** | §2.6 | Add a 4th gate: maintainability index must improve too. Does anything still get accepted? |
| **2C** | §2.6 | Delete one HARD RULE from the refactorer prompt. Which one was load-bearing? |
| **3** | §3.5 | **Bring your own code.** Paste a module of yours, write 2–3 behaviour tests, run `full_pipeline`. |
| **4A** | §4.4 | Add an MLScent gate: reject any patch that increases the ML smell count. |
| **4B** | §4.4 | Swap `config.MODEL`. Measure iterations-to-acceptance, wall clock, and cost. Is the expensive model cheaper *per accepted patch*? |
| **4C** | §4.4 | Give the Deep Agent the gate as a tool. Does an autonomous agent voluntarily verify itself? |

---

## 6 · Glossary

- **Blackboard** — shared mutable state all agents read/write.
- **Contract** — the output schema an agent must obey (JSON object, fenced code block).
- **Cyclomatic complexity (CC)** — count of independent paths through a function. Every `if` adds one.
- **Gate** — a deterministic accept/reject check standing between a proposal and reality.
- **Interest / principal** — recurring cost of debt vs one-off cost of fixing it.
- **Maintainability index (MI)** — 0–100 composite score; higher is better.
- **Orchestrator** — the code that sequences agents and owns the retry loop and the stop condition.
- **Reasoning model** — `gpt-5.x` / `o*`: spends hidden tokens thinking. Rejects `temperature`, uses `max_completion_tokens`.
- **Zero-shot classification** — labelling with a prompt and a closed label set, no training examples.

---

## 7 · Where to go next

| Today's toy | Production equivalent |
|---|---|
| `WorkflowState` dataclass | LangGraph state graphs · AutoGen conversations · CrewAI crews |
| a prompted general model | fine-tuned small models — cheaper **and** more consistent for narrow tasks |
| zero-shot TD classifier | **BEACon-TD / TD-Suite** fine-tuned transformers (13 debt types) |
| 4 hand-wrapped tools | **PyExamine** (49 metrics) · **MLScent** (76 ML anti-patterns) · full linter farms |
| 7 pytest tests as the gate | full CI: coverage thresholds, mutation testing, canary deploys |

---

## 8 · References

- **PyExamine** — Shivashankar & Martini, *MSR 2025* · `pip install code-quality-analyzer` · [github.com/KarthikShivasankar/python_smells_detector](https://github.com/KarthikShivasankar/python_smells_detector)
- **MLScent** — Shivashankar, *CAIN 2025* · `pip install ml-code-smell-detector` · [arXiv:2502.18466](https://arxiv.org/abs/2502.18466)
- **BEACon-TD / TD-Suite** — *Journal of Systems and Software*, 2025 · [github.com/KarthikShivasankar/text_classification](https://github.com/KarthikShivasankar/text_classification)
- *Enhancing Python Code Maintainability through LLM-Based Approaches* — Shivashankar & Martini, 2025
- Fowler, *Refactoring* (2nd ed.) — the smell taxonomy everything builds on
- Cunningham (1992) — the original debt metaphor. Two pages. Read it verbatim.
- LangGraph docs · [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/) · Deep Agents · [github.com/langchain-ai/deepagents](https://github.com/langchain-ai/deepagents)

---

## The three sentences worth remembering

1. **Deterministic tools measure; the LLM interprets; a gate decides.**
2. **Never let the component that can hallucinate be the component that certifies it did not.**
3. **Capability grows through tools and verification, not through bigger models.**

*Questions after today: karthik13sankar@outlook.com*
