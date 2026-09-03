# Instruction Note — Workshop 4
**Hands-on — Building Cooperative LLM Agent Workflows for Anti-pattern detection, Code Smell and Technical Debt Resolution**

**LLMA4SE 2026** · 15:00–18:00 · Karthik Shivashankar & Adela Nedisan Videsjorden

Thesis: *tools measure, LLMs interpret, gates decide.*

This edition uses **OpenRouter** through the official **`openai` Python client**. No GPU. Students need an OpenRouter key, not an OpenAI platform key.

Detectors (PyPI packages of the GitHub repos — do not clone them live):

- [PyExamine](https://github.com/KarthikShivasankar/python_smells_detector) → `code-quality-analyzer`
- [MLScent](https://github.com/KarthikShivasankar/ml_smells_detector) → `ml-code-smell-detector`

## Day before

- [ ] Run the notebook on a **fresh** Colab *and* once locally with a `.env` (copy `.env.example`; `OPENROUTER_API_KEY`, optional `LLM_MODEL`).
- [ ] Keys: institutional OpenRouter keys per table **or** students bring their own. Set spend limits; revoke at 18:00.
- [ ] Confirm `debtbuster/` sits next to the notebook (open the GitHub folder, not the `.ipynb` alone).
- [ ] Pre-run so you have a `TECH_DEBT_REPORT.md` and a `COOP_AUDIT.md` if someone's model stalls.
- [ ] Confirm `analyze_code_quality` and `ml_smell_detector` are on PATH after the Part 0 pip cell (same interpreter as the notebook).

## Live notes

- Sync point: everyone must see a sentence back from `llm()` before you leave Part 0. Teach the six-word map (LLM / tokens / tool / agent / gate / workflow) *after* that call, not as a 40-minute lecture.
- Default slug `openai/gpt-4o-mini` is cheap. Free slugs (e.g. Nemotron) often return `usage=None` — that is handled; they can still be slow or empty.
- **Never cut:** AST demo (§1.1), PyExamine on `itsdangerous`, MLScent on MNIST, sabotage (§2.6).
- Tree-sitter is *explained*, not installed. If late, skip the optional import cell; keep the contrast table.
- Deep Agents uses `ChatOpenAI(base_url=OpenRouter)`. Do **not** demo `openai:{MODEL}` — that looks up `OPENAI_API_KEY`.
- Deep Agents: two subagents + truncated tools. If it hangs, show your pre-run `COOP_AUDIT.md` and move on.
- Part 4 is `pip install -e ./debtbuster` (workshop copy, OpenRouter-aware). `tools.py` already calls PyExamine.
- Patients are `itsdangerous@2.2.0` `timed.py` and PyTorch MNIST. Sabotage inverts `if age > max_age`.
- Pit stops (minutes elapsed): Part 0/25, 1/70, 2/110, 3/150, 4/175.

## Cuts if late

1. Tree-sitter optional cell. 2. BYO-code (already a one-liner). 3. `debtbuster` CLI (homework). 4. LangGraph *compile/invoke* (keep the LangChain/LangGraph explanation and Deep Agents).

## Troubleshooting

| Symptom | Fix |
|---|---|
| 401 | Re-run §0.2. Strip quotes in `.env`. |
| Colab Secrets fail | `os.environ["OPENROUTER_API_KEY"] = "..."` or upload `.env`. |
| `usage` / `prompt_tokens` crash | You are on an old notebook — use this edition (runtime is inside the `.ipynb`). |
| Empty reply | Free/reasoning model ate the budget. Switch `LLM_MODEL` to `openai/gpt-4o-mini`. |
| Deep Agents missing key | Must pass `openrouter_chat_model()`, not `openai:{slug}`. |
| Deep Agents stall | Recursion / tool loops. Show pre-run `COOP_AUDIT.md`. |
| `analyze_code_quality` not found | Re-run the Part 0 pip cell; re-run the §0.6 PATH cell. |
| `debtbuster` missing key | Workshop package reads `OPENROUTER_API_KEY`. Re-run §0.2, then `pip install -e ./debtbuster`. |
| `debtbuster` traceback | Not a gate verdict. Re-install `-e ./debtbuster`. |
| Patient clone fails | Venue blocks GitHub. USB a pre-cloned `patients/` folder. |
| `radon` not on PATH | Re-run the §0.6 PATH cell. |
