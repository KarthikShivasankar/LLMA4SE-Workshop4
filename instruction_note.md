# Instruction Note — Workshop 4
**Hands-on — Building Cooperative LLM Agent Workflows for Anti-pattern detection, Code Smell and Technical Debt Resolution**

**LLMA4SE 2026** · 15:00–18:00 · Karthik Shivashankar & Adela Nedisan Videsjorden

Thesis: *tools measure, LLMs interpret, gates decide.*

This edition uses **OpenRouter** through the official **`openai` Python client**. No GPU. Students need an OpenRouter key, not an OpenAI platform key.

Ship three student-facing files plus the slides:

- `LLMA4SE_Workshop4_Colab.ipynb` — the whole workshop (runtime + `debtbuster/` snapshot inlined)
- `LLMA4SE_Workshop4_Slides.pptx` — room slides
- `students_handout.md` — keep open
- this note

Detectors (PyPI packages of the GitHub repos — do not clone them live):

- [PyExamine](https://github.com/KarthikShivasankar/python_smells_detector) → `code-quality-analyzer` → `analyze_code_quality`
- [MLScent](https://github.com/KarthikShivasankar/ml_smells_detector) → `ml-code-smell-detector` → `ml_smell_detector`

## Day before

- [ ] Run the notebook on a **fresh** Colab *and* once locally with a `.env` (`OPENROUTER_API_KEY`, optional `LLM_MODEL=openai/gpt-5.6-luna`).
- [ ] Keys: institutional OpenRouter keys per table **or** students bring their own. Set spend limits; revoke at 18:00.
- [ ] Confirm the runtime cell printed `debtbuster snapshot files: N` (Part 4 writes the package if someone only opened the `.ipynb`).
- [ ] Pre-run so you have a `TECH_DEBT_REPORT.md` and a `COOP_AUDIT.md` if someone's model stalls.
- [ ] Confirm `analyze_code_quality` and `ml_smell_detector` are on PATH after the Part 0 pip cell (same interpreter as the notebook). §0.7 prepends that interpreter’s `bin` / `Scripts`.
- [ ] Probe `openai/gpt-5.6-luna` first. Do not start the room on a free slug.

## Live notes

- Sync point: everyone must see a sentence back from `llm()` (§0.4) before you leave Part 0. Teach the six-word map (LLM / tokens / tool / agent / gate / workflow) *after* that call, not as a 40-minute lecture.
- Default slug `openai/gpt-5.6-luna`. `llm()` already sends `max_completion_tokens` and `reasoning_effort="low"` so the visible reply is JSON, not an empty reasoning dump. Free slugs (e.g. Nemotron) often return unparseable prose — that is why an earlier run saved 0 findings. §0.3 probes luna first; tell latecomers not to uncomment a free line “to save money.”
- Change provider with `switch_model("anthropic/…")` / `switch_model("google/…")`. Same OpenRouter key. Never `openai:{slug}` — that looks up `OPENAI_API_KEY`.
- TRACE is on by default. Every tool and LLM call prints the command, exit code, and a raw-reply preview. Use that when a student says “nothing happened.”
- **Never cut:** AST demo (§1.1), PyExamine on PayFlow (§1.3 / 1.5), MLScent on the churn trainer (§1.8), sabotage (§2.6).
- Tree-sitter is *explained*, not installed. If late, skip the optional import cell; keep the contrast table (astroid vs incremental CST).
- Case study is written by `write_case_study()` — PayFlow `checkout.py` + `test_checkout.py`, churn `train_churn.py`. No `git clone`. Sabotage flips the refund-cap `>` to `<`; gate 2 (`test_apply_refund_rejects_over_refund`) must catch it.
- Team order is **auditor → planner (≤3) → refactorer → QA**. QA has no LLM. Gates: `ast.parse` → sandbox pytest → radon CC must not rise. `accepted` only if all three pass. A “held” run is a success of the gates.
- LangGraph (§3.2) is the same loop, typed, *drawn* (`get_graph().draw_mermaid()`). The compiled graph omits the planner on purpose. Same gates.
- Deep Agents (§3.3) uses `openrouter_chat_model()` (`ChatOpenAI(base_url=OpenRouter)`). Two subagents (`pyexamine_auditor`, `mlscent_auditor`) + truncated tools + `recursion_limit=12` + 180 s timeout. If it hangs or 502s, show your pre-run `COOP_AUDIT.md` and move on — Part 4 does not need that cell.
- Part 4: six public issues (Flask #5214, Requests #7016 / #6637, HTTPX #3071, Pylint #9670, Django #35091) → classify → triage (`priority = interest ÷ principal`) → `TECH_DEBT_REPORT.md`. Then `ensure_debtbuster()` writes the embedded package and students run `python -m debtbuster audit` / `fix`.
- Pit stops (minutes elapsed): Part 0/25, 1/70, 2/110, 3/150, 4/175. The clock cell will print `behind — skip Deep Agents if needed`.

## Cuts if late

1. Tree-sitter optional import cell (keep the table). 2. BYO-code (already a one-liner). 3. Deep Agents invoke (keep the stack slide + pre-run `COOP_AUDIT.md`). 4. LangGraph *invoke* (keep compile + live graph view). 5. `debtbuster` CLI (homework).

## Troubleshooting

| Symptom | Fix |
|---|---|
| 401 | Re-run §0.2. Strip quotes in `.env`. Key must start `sk-or-`. |
| Colab Secrets fail | `os.environ["OPENROUTER_API_KEY"] = "..."` in a scratch cell, or upload `.env`. |
| `usage` / `prompt_tokens` crash | Old notebook. This edition treats `usage is None` as normal. |
| Empty reply / 0 findings | Free or reasoning model returned prose / no visible tokens. `switch_model("openai/gpt-5.6-luna")` and re-run the auditor. |
| Deep Agents missing key | Must pass `openrouter_chat_model()`, not `openai:{slug}`. |
| Deep Agents stall / 502 / timeout | Recursion or provider hiccup. Show pre-run `COOP_AUDIT.md`. Continue to Part 4. |
| `analyze_code_quality` / `ml_smell_detector` not found | Re-run the Part 0 pip cell; re-run the §0.7 PATH cell. Same interpreter as the notebook. |
| `debtbuster` missing key | The written package reads `OPENROUTER_API_KEY`. Re-run §0.2, then `pip install -e` the path `ensure_debtbuster()` printed. |
| `debtbuster` traceback | Not a gate verdict. Re-install `-e` and use `python -m debtbuster` (not a bare `debtbuster` on PATH). |
| `git clone` / exit 128 | Old notebook. This edition writes `debtbuster/` — do not clone. |
| Case files missing | Re-run `write_case_study` — it does not need the network. |
| `radon` not on PATH | Re-run the §0.7 PATH cell. |
| Sabotage “MISSED” | Refund-cap needle not found, or tests not on the sandbox `PYTHONPATH`. Re-run §0.8 then §2.6. |
| Held refactor (`accepted=False`) | Success of the gates. Do not debug as a harness bug unless you see a traceback. |
