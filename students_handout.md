# Student Handout — Workshop 4
**Hands-on — Building Cooperative LLM Agent Workflows for Anti-pattern detection, Code Smell and Technical Debt Resolution**

**LLMA4SE 2026** · 3 hours · Karthik Shivashankar & Adela Nedisan Videsjorden

Deterministic tools *measure*, LLMs *interpret*, gates *decide*.

## Setup (60 s)

1. Open `LLMA4SE_Workshop4_Colab.ipynb` (Colab CPU or local Jupyter) from the workshop folder so `debtbuster/` is next to it.
2. Local: copy `.env.example` → `.env`. Or provide `OPENROUTER_API_KEY` via Colab Secrets, `os.environ`, or the hidden prompt.
3. Optional: `LLM_MODEL=<openrouter-slug>` (default `openai/gpt-4o-mini`).
4. Run Part 0. A one-sentence definition of a code smell means you are ready.

Never paste a key into a code cell. The key lives in `os.environ` so `!debtbuster` inherits it.

Markers: **Predict** (edit `MY_GUESS_…` first) · **Try it** · **Discuss** · **Exercise** · **Pit stop**.

## 3-hour map

| Time | Part | You should see |
|---|---|---|
| 0:00–0:25 | 0 Setup + basics | a sentence back from `llm()` |
| 0:25–1:10 | 1 Parse then measure | `ast` walk; PyExamine; MLScent |
| 1:10–1:50 | 2 Cooperative team | planner → auditor → refactorer → QA; sabotage |
| 1:50–2:30 | 3 Frameworks | LangChain / LangGraph / Deep Agents + two subagents |
| 2:30–2:55 | 4 Debt and ship | six issues + `TECH_DEBT_REPORT.md` + `debtbuster` |
| 2:55–3:00 | Wrap | three takeaways |

## Concepts

- **Smell / anti-pattern / debt** — works, but costs interest until you pay principal. Triage: `priority = interest ÷ principal`.
- **AST** — source is a string; smells are queries on a tree (`FunctionDef`, `If`, `Call`). Grep lies. Gate 1 is `ast.parse`.
- **Tree-sitter** — incremental, error-tolerant, many languages (editors, Semgrep). PyExamine and MLScent use **astroid** / CPython `ast` instead (Python-aware scopes).
- **Agent** — role (system prompt), brain (`llm()` → OpenRouter via `openai.OpenAI`), tools, contract (JSON or one code block).
- **Team** — planner (≤3 smells) · auditor · refactorer · QA. Shared **blackboard**. If it is not on the board, it did not happen.
- **Gates** — `ast.parse` · upstream pytest · complexity. No LLM in the verifier.
- **Stack** — `openai` client (HTTP) → **LangChain** (`ChatOpenAI`) → **LangGraph** (state machine) → **Deep Agents** (planner + filesystem + subagents).
- **Patients** — `itsdangerous` `timed.py` + its tests; PyTorch MNIST; six real GitHub issues.
- **Detectors** — [PyExamine](https://github.com/KarthikShivasankar/python_smells_detector) (MSR 2025) · [MLScent](https://github.com/KarthikShivasankar/ml_smells_detector) (CAIN 2025).

## Failure patterns

| Pattern | Mitigation |
|---|---|
| Plausible-but-wrong patch | gate 2 — real tests |
| Contract drift | `extract_json` / `extract_code_block` + retry |
| Reward hacking | gates 2 and 3 |
| Runaway loops | `max_iterations` |
| Unverifiable claims | no LLM in QA |

## Take home

```bash
pip install -e ./debtbuster
export OPENROUTER_API_KEY=sk-or-...
export LLM_MODEL=openai/gpt-4o-mini
debtbuster audit  path/to/module.py
debtbuster fix    path/to/module.py --tests path/to/test_module.py
```

`fix` exits 1 and writes nothing when the gate rejects.

## Remember

1. Tools measure; the LLM interprets; a gate decides.
2. The thing that can hallucinate must not certify that it did not.
3. Capability grows through tools and verification, not bigger models.

Questions: karthik13sankar@outlook.com
