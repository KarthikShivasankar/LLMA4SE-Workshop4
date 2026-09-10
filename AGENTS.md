## Learned User Preferences
- Prefer explanation-heavy workshop notebooks: more comments and teaching text, no Exercise / Hint / Solution sections.
- Use real-world case studies instead of toy examples such as magic numbers, age-max, or patients.
- When an OpenAI model is used via OpenRouter, use only `openai/gpt-5.6-luna`; include a `switch_model("provider/slug")` example for changing LLMs.
- Keep tool-call / TRACE visibility so students see commands, exit codes, and raw replies when cells run.
- Show LangGraph agent logic as a live graph or flowchart and include explanatory images or infographics in the Colab notebook.
- Cover beginner prerequisites in the notebook: LangGraph, LangChain, AST, and tree-sitter.
- When verifying the Colab, run cells end to end so every cell has a meaningful output.
- Free OpenRouter slugs are fine for agent-side testing and should be rotated if rate-limited; do not make free slugs the student-facing default.

## Learned Workspace Facts
- This repo is LLMA4SE Workshop 4 (2026): a 3-hour hands-on on cooperative LLM agent workflows for anti-pattern detection, code smell, and technical debt. Thesis: tools measure, the LLM interprets, a gate decides.
- Student-facing ship set is `LLMA4SE_Workshop4_Colab.ipynb` (runtime and a `debtbuster/` snapshot inlined), `LLMA4SE_Workshop4_Slides.pptx`, `README.md`, `instruction_note.md`, and `students_handout.md`.
- Smell detectors are PyExamine (`code-quality-analyzer` / CLI `analyze_code_quality`) and MLScent (`ml-code-smell-detector` / CLI `ml_smell_detector`); install from PyPI and do not git-clone those detector repos live.
- LLM access is OpenRouter only via the official `openai` client (`base_url=https://openrouter.ai/api/v1`). Default `LLM_MODEL=openai/gpt-5.6-luna` needs `max_completion_tokens` and `reasoning_effort="low"`. Never use `openai:{slug}` (that looks up `OPENAI_API_KEY`).
- Do not `git clone` this repo into `/content/LLMA4SE-Workshop4` on Colab (that caused exit 128). The case study is written by `write_case_study()`.
- Case study is PayFlow checkout/refund (`cases/payflow/`) plus a churn trainer (`cases/churn/`); Part 4 triages six public issues from Flask, Requests, HTTPX, Pylint, and Django.
- Cooperative team order is auditor → planner (≤3 actions) → refactorer → QA (QA has no LLM). Gates: `ast.parse` → sandbox pytest → radon CC must not rise.
- Use the embedded `debtbuster/` snapshot (`python -m debtbuster`); do not `pip install` the public GitHub `debtbuster` package (it still expects `OPENAI_API_KEY`).
- Empty audit / 0 findings usually means a free or reasoning model returned prose or no visible tokens — switch to `openai/gpt-5.6-luna`.
- Key load order is `os.environ` / `.env` → Colab Secrets → hidden prompt; never paste a key into a code cell. Keep a `.env.example`.
- Tree-sitter is explained as a contrast, not installed. LangGraph's compiled graph omits the planner on purpose.
