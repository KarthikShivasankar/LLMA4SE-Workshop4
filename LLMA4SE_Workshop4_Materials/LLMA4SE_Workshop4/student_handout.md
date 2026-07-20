# Student Handout — Building Cooperative LLM Agent Workflows
### LLMA4SE 2026 · Workshop 4 · Karthik Shivashankar & Adela Nedisan Videsjorden

Keep this. Everything you build today runs on **free Colab** and fits in your head: three notebooks, one idea.

> **The idea:** deterministic tools *measure*, LLMs *interpret*, verification gates *decide*. Architecture beats model size — today's brain is only 1.5B parameters.

---

## 1 · Core concepts

**Code smell.** A surface symptom of a deeper design problem (Fowler). Not a bug: the code *works*. Examples you'll meet: mutable default arguments, magic numbers, long parameter lists, duplicated logic, dead code.

**Anti-pattern.** A commonly used solution that looks reasonable and is reliably counterproductive — a smell with a name and a story.

**Technical debt (Cunningham, 1992).** The cost of choosing the quick option now. **Principal** = effort to fix; **interest** = the recurring drag it causes until you do. Studies put the waste at roughly 23–42% of development time. Triage rule of thumb from Part 3: `priority = interest / principal` — high-interest, low-principal items are your quick wins.

**ML-specific smells.** A category classic linters can't see: missing random seeds (unreproducible results), `x == np.nan` (always `False` — the branch never runs), missing `optimizer.zero_grad()` (gradients accumulate → wrong training), no early stopping/checkpointing/`model.eval()`. They rarely crash; they silently corrupt *science*. Detected today by **MLScent** (76 detectors).

**Agent (our minimal, framework-free definition).** Four ingredients:
1. a **role** — the system prompt that sets values and output rules;
2. a **brain** — the LLM (`llm()` helper, same for every agent);
3. **tools** — plain Python callables producing *evidence*;
4. a **contract** — a strict JSON/code-block output schema so the next agent can *parse*, not *read*.

Change the role and tools, keep the skeleton: that's how the Code Auditor became the ML Auditor in two cells.

**Blackboard state.** All agents read/write one shared `WorkflowState` object with a `record()` audit trail — a flight recorder for the workflow. Alternative: message passing (agents talk point-to-point). Blackboard wins for auditability in small teams; message passing scales to larger, decoupled ones.

**Verification gates.** Part 2's QA agent deliberately contains **no LLM**: gate 1 `ast.parse` (syntax) → gate 2 pytest in a sandbox (behavior) → gate 3 radon complexity must not worsen (quality). Rejections loop back to the Refactorer *with the failure reason*. Remember the sabotage demo: a plausible patch that changed the VAT rate sailed past human-style review and died at gate 2. **Never let the fox audit the henhouse.**

## 2 · The six agentic failure patterns (Part 2 lab)

| Pattern | Symptom | Mitigation you built |
|---|---|---|
| Hallucinated success | "All tests pass!" (they don't) | deterministic QA gates |
| Silent behavior change | plausible diff, different semantics | behavior-pinning tests |
| Format drift | prose instead of JSON/code block | strict contracts + extractors |
| Infinite loops | refactor⇄reject forever | `max_iterations` + budget |
| Context loss | agent forgets earlier findings | blackboard state |
| Scope creep | "improved" things nobody asked for | invariants in the role prompt |

## 3 · Exercises recap

- **Ex 1 (Part 1):** add a magic-number AST detector tool to the auditor. ⭐ Bonus: prompt it to rank findings.
- **Ex 2 (Part 2):** A — Docstring Agent; B — maintainability-index gate; C — token budget in `WorkflowState`; **D — ML refactoring team:** point the workflow at `ml_project/train_model.py`, which has *no tests* — replace gate 2 with "MLScent smell count must strictly decrease." Think about what that gate can be fooled by.
- **Final challenge (Part 3):** run `full_pipeline()` on your own 30–80 lines of code.

## 4 · Glossary quickies

`radon` complexity/maintainability metrics · `pylint` classic linter · **PyExamine** 49-metric Python smell detector (91% recall, MSR 2025) · **MLScent** 76 ML anti-pattern detectors (CAIN 2025) · **BEACon-TD** technical-debt classification benchmark, 13 debt types (JSS 2025) · *cyclomatic complexity (CC)* independent paths through code · *MI* maintainability index · *temperature 0* deterministic decoding for classification.

## 5 · From workshop to production (→ Notebook Part 4, bonus)

You built the orchestrator in ~30 lines of Python on purpose — and then, in the bonus Part 4, rebuilt it with the production stack so you can see it's the *same pattern* wearing different clothes:

| Hand-built (Parts 1–3) | Production (Part 4) | What you gain / pay |
|---|---|---|
| `llm()` over in-process transformers | **Ollama** server (`qwen2.5-coder:7b`, 4-bit) | stronger brain in the same VRAM; one model, many clients; one-string model swap |
| `WorkflowState` + `run_workflow()` | **LangGraph** `StateGraph` + conditional edges | typed state, free diagrams, checkpointing; costs a dependency |
| Auditor with tools + JSON contract | **Deep Agent** (`deepagents`): `write_todos`, file tools, sub-agents | autonomy & planning; costs control and predictability |
| notebook cells | **`debtbuster`** CLI harness | 5 files + tests + `pip install -e .`; exit code 1 on gate rejection → CI-ready |

Also in the ecosystem: **AutoGen** (conversations = message passing), **CrewAI** (roles = our system prompts). You now know what all of them are abstracting.

**Part 4 exercises:** A — add an MLScent gate (`--ml` flag); B — deep-agent fixer vs LangGraph team, 3-run comparison; C — LangGraph checkpointing (rebuild the flight recorder); D — 7b vs 3b model-swap measurement.

## 6 · References & tools

- Shivashankar & Martini — **PyExamine**, MSR 2025 · `pip install code-quality-analyzer` · github.com/KarthikShivasankar/python_smells_detector
- Shivashankar — **MLScent**, CAIN 2025 · arXiv:2502.18466 · `pip install git+https://github.com/KarthikShivasankar/ml_smells_detector.git`
- Shivashankar et al. — **BEACon-TD / TD-Suite**, JSS 2025 · github.com/KarthikShivasankar/text_classification
- Shivashankar & Martini, 2025 — LLM agents & maintainability
- Fowler — *Refactoring* (2nd ed.) · Cunningham (1992) — the debt metaphor
- Model: **Qwen2.5-Coder-1.5B-Instruct** (Hugging Face)

Questions after today: **karthik13sankar@outlook.com**
