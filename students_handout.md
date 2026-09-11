# Student Handout — Workshop 4
**Hands-on — Building Cooperative LLM Agent Workflows for Anti-pattern detection, Code Smell and Technical Debt Resolution**

**LLMA4SE 2026** · 3 hours · Karthik Shivashankar & Adela Nedisan Videsjorden

Deterministic tools *measure*, LLMs *interpret*, gates *decide*.

## Setup (60 s)

1. Open `LLMA4SE_Workshop4_Colab.ipynb` (Colab CPU or local Jupyter). You do **not** `git clone` the workshop repo in Colab.
2. Local: create a `.env` with `OPENROUTER_API_KEY=sk-or-...`. Or provide the key via Colab Secrets, `os.environ`, or the hidden prompt.
3. Optional: `LLM_MODEL=<openrouter-slug>`. If you stay on OpenAI, use only `openai/gpt-5.6-luna`. Change provider later with `switch_model("anthropic/…")`.
4. Run Part 0 through §0.4. A one-sentence definition of a code smell means you are ready.

Never paste a key into a code cell. The key lives in `os.environ`.

Markers: **Try it** · **Discuss** · **Pit stop**. Every tool and LLM call prints a TRACE block (command, exit code, raw reply). Silence (`reply: 0 chars`) is a *model* problem — switch back to luna.

## 3-hour map

| Time | Part | You should see |
|---|---|---|
| 0:00–0:25 | 0 Setup + basics | key loaded; `llm()` returns a sentence; PayFlow + churn files written |
| 0:25–1:10 | 1 Parse then measure | `ast` walk; PyExamine CSV; MLScent on the trainer; radon vs the model |
| 1:10–1:50 | 2 Cooperative team | auditor → planner → refactorer → QA; sabotage caught by pytest |
| 1:50–2:30 | 3 Frameworks | LangGraph live graph; Deep Agents writes `COOP_AUDIT.md` (or instructor copy) |
| 2:30–2:55 | 4 Debt and ship | six issues ranked; `TECH_DEBT_REPORT.md`; `python -m debtbuster` |
| 2:55–3:00 | Wrap | three takeaways |

## Concepts

- **Smell / anti-pattern / debt** — works, but costs interest until you pay principal. Triage: `priority = interest ÷ principal`.
- **AST** — source is a string; smells are queries on a tree (`FunctionDef`, `If`, `Call`). Grep lies. Gate 1 is `ast.parse`.
- **Tree-sitter** — incremental, error-tolerant, many languages (editors, Semgrep). PyExamine and MLScent use **astroid** / CPython `ast` instead (Python-aware scopes). We explain it; we do not depend on a Colab install.
- **Agent** — four slots: role (system prompt) · brain (`llm()` → OpenRouter via `openai.OpenAI`) · tools · contract (JSON or one code fence).
- **Team** — auditor (tools first) · planner (≤3 smells) · refactorer (one `python` fence, keep the PayFlow public API) · QA. Shared **blackboard**. If it is not on the board, it did not happen.
- **Gates** — `ast.parse` · sandbox pytest · radon CC must not rise. No LLM in the verifier. A held patch is a success of the gates.
- **Sabotage** — one character in `apply_refund`: `>` → `<`. File still parses; `test_apply_refund_rejects_over_refund` must fail.
- **Stack** — `openai` client (HTTP) → **LangChain** (`ChatOpenAI` via `openrouter_chat_model()`) → **LangGraph** (state machine) → **Deep Agents** (planner + filesystem + subagents). Never pass `openai:{slug}` to Deep Agents.
- **Case study** — written on disk, no clone: PayFlow `checkout.py` (invoices / refunds) + sklearn churn trainer (leakage, no seed); six real GitHub issues.
- **Detectors** — [PyExamine](https://github.com/KarthikShivasankar/python_smells_detector) (MSR 2025, `analyze_code_quality`) · [MLScent](https://github.com/KarthikShivasankar/ml_smells_detector) (CAIN 2025, `ml_smell_detector`). Both are static — they never train a model and never run your tests.

## Failure patterns

| Pattern | Mitigation |
|---|---|
| Plausible-but-wrong patch | gate 2 — real tests (the refund-cap flip) |
| Contract drift | `extract_json` / `extract_code_block` + retry |
| Reward hacking | gates 2 and 3 (CC must not get worse) |
| Runaway loops | `max_iterations` / Deep Agents `recursion_limit` |
| Empty / 0 findings | free model returned prose — `switch_model("openai/gpt-5.6-luna")` |
| Unverifiable claims | no LLM in QA |

## Remember

1. Tools measure; the LLM interprets; a gate decides.
2. The thing that can hallucinate must not certify that it did not.
3. Capability grows through tools and verification, not bigger models.

Questions: karthik13sankar@outlook.com
