# debtbuster

A lean LLM-agent harness: **audit, refactor and gate Python code**.
Built live in [LLMA4SE 2026 Workshop 4](../README.md) — five source files, its own tests, one CLI.

The source here is extracted verbatim from `LLMA4SE_Workshop4_Colab.ipynb` §4.3, so the package and the
notebook cannot drift apart.

## Install

```bash
pip install "git+https://github.com/KarthikShivasankar/LLMA4SE.git#subdirectory=debtbuster"
```

Or, from a clone:

```bash
pip install -e ./debtbuster
```

## Use

```bash
export OPENAI_API_KEY=sk-...

debtbuster audit path/to/module.py

debtbuster fix path/to/module.py --tests path/to/test_module.py
```

`fix` exits **non-zero when the QA gate rejects the patch**, so it drops straight into CI:

```yaml
- run: debtbuster fix src/module.py --tests tests/test_module.py
```

## How it works

`auditor → refactorer ⇄ QA gates`, wired as a LangGraph `StateGraph` with a conditional retry edge.

The three gates are deliberately **LLM-free**:

| Gate | Checks |
|---|---|
| 1 · `ast.parse` | the candidate is syntactically valid Python |
| 2 · `pytest` in a sandbox | behaviour is unchanged (skipped when `--tests` is omitted) |
| 3 · `radon` | average cyclomatic complexity did not get worse |

Change the model in one place: `src/debtbuster/config.py`.

## Layout

| File | Role |
|---|---|
| `config.py` | model, temperature, iteration budget |
| `brain.py` | the only file that talks to a model |
| `tools.py` | deterministic eyes (radon, PyExamine) — no LLM |
| `gates.py` | the QA gate — no LLM |
| `graph.py` | the LangGraph team |
| `cli.py` | `audit` / `fix` |
