"""Generate the self-contained Workshop 4 notebook.

Runtime is inlined. Part 4 installs the local OpenRouter-aware package
with ``pip install -e ./debtbuster``.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "LLMA4SE_Workshop4_Colab.ipynb"
LIB_SRC = (ROOT / "workshop_lib.py").read_text(encoding="utf-8")


def md(src: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": [line + "\n" for line in src.strip("\n").split("\n")]}


def hint_sol(hint: str, solution: str) -> dict:
    return md(
        "<details>\n<summary>💡 Hint — peek if stuck</summary>\n\n"
        + hint.strip()
        + "\n\n</details>\n\n<details>\n<summary>✅ Solution — try first</summary>\n\n"
        + solution.strip()
        + "\n\n</details>"
    )


def code(src: str) -> dict:
    lines = src.strip("\n").split("\n")
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [ln + "\n" for ln in lines[:-1]] + ([lines[-1]] if lines else []),
    }


RUNTIME = (
    "# Self-contained runtime — OpenRouter via openai.\n"
    "# This cell is the whole toolbox. No workshop_lib.py required.\n"
    + LIB_SRC
    + """

key = load_credentials()
print("key loaded, ends with …" + key[-4:])
print("model:", model_name())
"""
)


cells: list[dict] = []

cells += [
    md("""# Workshop 4: Hands-on — Building Cooperative LLM Agent Workflows for Anti-pattern detection, Code Smell and Technical Debt Resolution
**LLMA4SE 2026** · 3 hours · CPU · OpenRouter + official `openai` client.

Thesis: **tools measure · the LLM interprets · a gate decides.**

**Picture this.** A junior engineer pastes a function into ChatGPT and asks “is this complex?”
The model says “cyclomatic complexity 4.” radon says **7**. If you had gated a merge on that
number, you would have shipped a lie. Today we build a *team* that cannot certify itself:
PyExamine and MLScent measure, the LLM names the smell, pytest decides whether a patch ships.

| Word | Meaning today |
|---|---|
| **Smell** | Legal code that costs interest — a 40-line `unsign`, a magic `3600` ([PyExamine](https://github.com/KarthikShivasankar/python_smells_detector), MSR 2025). |
| **Anti-pattern** | A recurring *wrong solution* — missing `manual_seed`, training in eval mode ([MLScent](https://github.com/KarthikShivasankar/ml_smells_detector), CAIN 2025). |
| **Debt** | The bill. **priority = interest ÷ principal**. High pain, cheap fix → do first. |

**Today you will build**

1. Talk to an LLM safely (OpenRouter). Copy `.env.example` → `.env` if you run locally.
2. Parse code with an AST so smells are *queries on a tree*, not vibes.
3. Measure with PyExamine and MLScent; let the model interpret the dump.
4. A cooperative team: planner → auditor → refactorer → QA gates (no LLM in QA).
5. The same team as **LangGraph**, then as **Deep Agents** with two detector subagents.
6. Triage a real backlog and ship `TECH_DEBT_REPORT.md` — or a gated patch.

Keep `debtbuster/` next to this notebook. Markers: **Predict** (`MY_GUESS_…`) · **Try it** · **Discuss** · **Exercise** (hints hide below)."""),
    md("""# Part 0 · Setup + beginner basics  ·  0:00–0:25
## 0.1 · Install
Ignore Colab *Restart session* and the `google-auth` warning — they are noise.
`code-quality-analyzer` is [PyExamine](https://github.com/KarthikShivasankar/python_smells_detector).
`ml-code-smell-detector` is [MLScent](https://github.com/KarthikShivasankar/ml_smells_detector)."""),
    code("""%pip install -q openai radon pylint pytest pandas langgraph deepagents langchain-openai code-quality-analyzer ml-code-smell-detector freezegun
print("toolbox installed")"""),
    md("""## 0.2 · Key + runtime
`OPENROUTER_API_KEY` + optional `LLM_MODEL` (any [OpenRouter slug](https://openrouter.ai/models)).
Load order: `os.environ` / `.env` → Colab Secrets → hidden prompt. Never paste a key into a cell.
Local: copy `.env.example` to `.env`. This cell *is* the library (`llm`, `extract_json`, …)."""),
    code(RUNTIME),
    md("""## 0.3 · Your first LLM call
`make_client()` is `OpenAI(base_url=https://openrouter.ai/api/v1, api_key=OPENROUTER_API_KEY)`.
That object is a **client**, not “ChatGPT.” The slug in `LLM_MODEL` picks the brain.
`llm()` then calls `chat.completions.create`. Reasoning slugs (`o1`, `o3`, `:thinking`) get
`max_completion_tokens`; everyone else gets `max_tokens` + `temperature`.
If the first call fails (JSON mode, temperature), we retry without those extras.

**Try it.** A sentence back means the key, the URL, and the slug all work.
Silence is a *model* problem, not a Python crash."""),
    code("""print(llm("In one sentence: what is a code smell?"))
cost_report()"""),
    md("""## 0.4 · Beginner map — six words we will keep using

| Idea | Walk away with |
|---|---|
| **LLM call** | Text in, tokens out. `openai.OpenAI(base_url=OpenRouter)` is a client. `LLM_MODEL` picks the brain. |
| **Tokens** | Characters ≠ tokens. OpenRouter may omit `usage`. Temperature is a *sampling* knob, not intelligence. |
| **Tool** | A deterministic function the model did *not* write (radon, PyExamine, pytest). Tools measure. |
| **Agent** | Four slots: **role** (system prompt) · **brain** (`llm`) · **tools** · **contract** (JSON / one code fence / exit code). |
| **Gate** | A check with **no LLM**. If the gate fails, the patch did not happen. |
| **Workflow** | Several agents sharing a **blackboard**. If it is not on the board, it did not happen. |

**Kitchen.** The thermometer (tools) reads 47 °C. The critic (LLM) says “over-reduced.”
The health inspector (gate) stamps the plate — or sends it back. The critic does not stamp the plate.

## 0.5 · Tokens
The string `unsign` is 6 chars and usually 1–2 tokens. `usage is None` is normal, not a bug.

> 🧪 A refactorer wants **reproducible** patches. `temperature=0.0` or `1.2`?"""),
    code("""probe = "def unsign(self, signed_value, max_age=None):"
kwargs = {"model": model_name(), "messages": [{"role": "user", "content": f"Repeat exactly: {probe}"}]}
kwargs["max_completion_tokens" if is_reasoning_model() else "max_tokens"] = 80
r = make_client().chat.completions.create(**kwargs)
u = r.usage
print("chars sent", len(probe))
if u is None:
    print("usage: None (OpenRouter omitted it — fine)")
else:
    print("tokens in/out", u.prompt_tokens, u.completion_tokens)
print("reply:", (r.choices[0].message.content or "")[:80])"""),
    hint_sol(
        "Temperature is a *sampling* knob. High = more surprise. A refactorer must keep `TimestampSigner.unsign` identical.",
        "Use **low** temperature (`0.0`–`0.2`). `1.2` is for brainstorming names, not for rewriting a signed-cookie library.",
    ),
    md("""## 0.6 · Workspace + clock
We `chdir` into a workshop folder so clones and reports do not clutter your home directory.
`WORKSHOP_ROOT` remembers where `debtbuster/` lives *before* that chdir."""),
    code("""import os, pathlib, sys, time, json, re, ast, subprocess

os.environ["PATH"] = str(pathlib.Path(sys.executable).parent) + os.pathsep + os.environ["PATH"]
WORKSHOP_ROOT = pathlib.Path.cwd().resolve()
for p in (pathlib.Path.cwd(), pathlib.Path.cwd().parent, pathlib.Path("/content/LLMA4SE-Workshop4")):
    if (p / "debtbuster" / "pyproject.toml").is_file():
        WORKSHOP_ROOT = p.resolve()
        break
WORKDIR = (pathlib.Path("/content/workshop") if pathlib.Path("/content").exists()
           else pathlib.Path("./workshop")).resolve()
WORKDIR.mkdir(exist_ok=True)
os.chdir(WORKDIR)
print("working in", os.getcwd())
print("workshop root", WORKSHOP_ROOT)

T0 = time.time()
SCHEDULE = {"Part 0": 25, "Part 1": 70, "Part 2": 110, "Part 3": 150, "Part 4": 175}

def pit_stop(part: str) -> None:
    mins = (time.time() - T0) / 60
    drift = SCHEDULE[part] - mins
    mood = ("ahead" if drift > 5 else "on time" if drift > -5 else "behind — skip the exercise")
    print(f"{mins:5.0f} min elapsed | {part} budget {SCHEDULE[part]} | {mood}")

SCORE = {"asked": 0, "right": 0}

def quiz(question, your_answer, correct, explain=""):
    ok = bool(correct(your_answer)) if callable(correct) else your_answer == correct
    SCORE["asked"] += 1
    SCORE["right"] += int(ok)
    print(f"Q: {question}\\n  you: {your_answer!r}  {'OK' if ok else 'no'}")
    if explain:
        print(" ", explain)

def scoreboard():
    n, r = SCORE["asked"], SCORE["right"]
    print(f"prediction score: {r}/{n}" if n else "no predictions")

pit_stop("Part 0")"""),
    md("""## 0.7 · Patients
Pinned clones — not toy snippets. `itsdangerous` is the library Flask uses to sign cookies.
We will *sabotage* `if age > max_age` later; the real `test_max_age` must catch it.

`fetch_patients()` clones `pallets/itsdangerous@2.2.0` and sparse-checks `pytorch/examples/mnist`.
Tests live at `tests/test_itsdangerous/test_timed.py` (nested). The QA gate copies the **package tree**
and overlays `timed.py`, so `import itsdangerous` still resolves."""),
    code("""paths = fetch_patients(WORKDIR / "patients")
PATIENT_PY = paths["PATIENT_PY"]
PATIENT_TESTS = paths["PATIENT_TESTS"]
ML_PATIENT_DIR = paths["ML_PATIENT_DIR"]
ITSD_ROOT = paths.get("ITSD_ROOT") or str(pathlib.Path(PATIENT_PY).parents[2])
print(PATIENT_PY)
print(PATIENT_TESTS)
print(ML_PATIENT_DIR)
print(ITSD_ROOT)
r = subprocess.run([sys.executable, "-m", "pytest", PATIENT_TESTS, "-q"], capture_output=True, text=True)
print(r.stdout[-400:] or r.stderr[-400:])
print("pytest exit", r.returncode)"""),
]

cells += [
    md("""# Part 1 · Parse, then measure  ·  0:25–1:10
A **bug** makes tests fail. A **smell** is legal code that costs interest. An **anti-pattern** is a
recurring wrong solution (especially in training loops). Detectors do not “read code like a human.”
They **parse** it. If you skip this, the CSV looks like magic.

## 1.1 · Why parsers exist
Source is a string. A parser turns it into a tree of nodes (`FunctionDef`, `If`, `Call`).
Smells are *queries on that tree*: “any function with more than N `If` nodes,” “any `iterrows` Call.”
Without a tree you are grepping, and grepping lies — `# if age > max_age` is a comment.

**What you just learned in Part 0.** Gate 1 later is `ast.parse` (syntax). Cyclomatic complexity
*starts* as “count decision nodes.” The magic-number exercise is `ast.walk` + `ast.Constant`."""),
    code("""src = '''
def expire(age, max_age):
    if age is None:
        return False
    if age > max_age:
        if max_age > 0:
            raise TimeoutError("expired")
    return True
'''
tree = ast.parse(src)
print(ast.dump(tree, indent=2)[:800])
print("If nodes:", sum(isinstance(n, ast.If) for n in ast.walk(tree)))
print("FunctionDef nodes:", sum(isinstance(n, ast.FunctionDef) for n in ast.walk(tree)))"""),
    md("""## 1.2 · Tree-sitter (explain — do not depend on a Colab install)
CPython `ast` / **astroid** know Python *semantics* (scopes, what a name refers to).
That is why PyExamine and MLScent chose them.

**Tree-sitter** is the incremental, error-tolerant, multi-language sibling. Editors and GitHub
use it so a file you have not finished typing still highlights. Semgrep uses it to search many languages.
A broken file still gets a *partial* tree. `ast.parse` raises `SyntaxError` instead.

| | CPython `ast` / astroid | Tree-sitter |
|---|---|---|
| Job | Exact Python semantics | Incremental, error-tolerant, many languages |
| Who uses it here | PyExamine + MLScent | Editors, GitHub, Semgrep, other linters |
| Broken file | `SyntaxError` — skip / fail | Still builds a partial tree |
| Workshop | We **run** this | Prerequisite knowledge |

Instructor one-liner: *Tree-sitter is why VS Code still highlights a file you have not finished typing.
Our detectors chose astroid because they need Python-aware scopes, not a generic CST.*

Optional cell — skip if late. It does **not** `pip install` anything."""),
    code("""print("CPython ast / astroid: exact Python semantics (what PyExamine and MLScent run).")
print("Tree-sitter: incremental CST — editors, GitHub, Semgrep.")
try:
    import tree_sitter_python as tspy  # optional extra; not in Part 0 install
    from tree_sitter import Language, Parser
    parser = Parser(Language(tspy.language()))
    tree = parser.parse(src.encode())
    print("tree-sitter root:", tree.root_node.type, "has_error", tree.root_node.has_error)
except Exception as e:
    print("tree-sitter not installed — that is fine. Prerequisite, not a dependency.")
    print(" ", type(e).__name__)"""),
    md("""## 1.3 · Three eyes — what each tool cannot do
Both smell detectors **walk an AST**. They do not run your tests and they do not need a GPU.

| Tool | Measures | Cannot |
|---|---|---|
| **PyExamine** (`analyze_code_quality`) | Fowler-style code / architectural / structural smells | Run tests; decide a merge |
| **MLScent** (`ml_smell_detector`) | ML anti-patterns (seed, leakage, eval mode, …). No PyTorch install needed. | Prove the model trained correctly |
| **radon** | Cheap cyclomatic complexity — our later **gate 3** thermometer | Name a smell in English |
| **pylint** | Style / bug-adjacent messages | Be the merge gate by itself |

Pipeline: **1** parse (`ast`) → **2** measure (PyExamine / MLScent / radon) → **3** interpret (`llm`) → **4** decide (gates).

## 1.4 · PyExamine on `itsdangerous`
[PyExamine](https://github.com/KarthikShivasankar/python_smells_detector) (MSR 2025) — 18 code smells + cross-file + architectural + structural.
We run `--type code` on the package directory and ignore `tests` / `venv`.

Look for names you can say out loud: *Long Method*, *High Cyclomatic Complexity*, *Large Class*.
> 🎯 Edit `MY_GUESS_SMELLS` *before* you run — will the report mention a long / complex method?"""),
    code("""def run_radon(path: str) -> str:
    return subprocess.run(["radon", "cc", "-s", path], capture_output=True, text=True).stdout or "n/a"

def run_pylint(path: str, max_findings: int = 15) -> str:
    raw = subprocess.run(["pylint", path, "-f", "json", "--score", "n"],
                         capture_output=True, text=True).stdout
    try:
        issues = json.loads(raw or "[]")[:max_findings]
    except json.JSONDecodeError:
        return raw[:1500]
    return "\\n".join(f"L{i['line']}: [{i['symbol']}] {i['message']}" for i in issues) or "no findings"

def run_pyexamine(directory: str, smell_type: str = "code") -> str:
    subprocess.run(
        ["analyze_code_quality", directory, "--type", smell_type, "--output", "pyx",
         "--ignore", "tests", "venv", ".git", "__pycache__"],
        capture_output=True, text=True, timeout=600,
    )
    p = pathlib.Path("pyx.txt")
    return p.read_text()[:2500] if p.exists() else "no report (check pyx.txt)"

def run_pyexamine_for_file(path: str) -> str:
    '''Auditor tools all take a file path; PyExamine wants a directory.'''
    return run_pyexamine(str(pathlib.Path(path).parent))

print(run_pyexamine(ITSD_ROOT)[:2200])"""),
    hint_sol(
        "Skim the printed report for 'Long Method', 'Cyclomatic', or `unsign`. You are predicting a *name*, not inventing a number.",
        "`MY_GUESS_SMELLS = True` is the usual outcome on `timed.py` — PyExamine flags complexity / length on the timestamp path. The point is the *tool* said it.",
    ),
    code("""MY_GUESS_SMELLS = True  # will PyExamine mention a long or complex method?
pyx = pathlib.Path("pyx.txt").read_text() if pathlib.Path("pyx.txt").exists() else ""
hit = any(tok in pyx.lower() for tok in ("long method", "cyclomatic", "unsign", "large"))
print("report mentions long/complex?", hit)
quiz("PyExamine flags a long or complex method", MY_GUESS_SMELLS, hit,
     "Tools measure. The LLM will interpret this dump, not invent the smells.")"""),
    md("""## 1.5 · radon — the cheap thermometer we will gate on
PyExamine is the rich report. radon is the number gate 3 will compare before vs after.
> 🎯 Edit `MY_GUESS_HARD` *before* you run — how many radon **C+** blocks in `timed.py`?"""),
    code("""print(run_radon(PATIENT_PY))
print(run_pylint(PATIENT_PY)[:800])"""),
    hint_sol(
        "Rank A is simplest. C and above means “this block is getting hard to test.” Count names in the radon JSON where `rank >= 'C'`.",
        "`MY_GUESS_HARD` is whatever `len(hard)` prints. On `itsdangerous` 2.2.0 `timed.py` you typically see **1** C+ block (`unsign` / timestamp path).",
    ),
    code("""MY_GUESS_HARD = 1  # how many blocks with rank C or worse?

raw = subprocess.run(["radon", "cc", "-j", PATIENT_PY], capture_output=True, text=True).stdout
data = json.loads(raw or "{}")
hard = [(b["name"], b["complexity"], b.get("rank"))
        for blocks in data.values() for b in blocks if b.get("rank", "A") >= "C"]
print("hard blocks:", hard)
quiz("radon C+ count", MY_GUESS_HARD, len(hard),
     "radon is the thermometer. PyExamine named the smell. The LLM still has not been asked to count.")"""),
    md("""## 1.6 · Model vs radon
Same file, two complexity numbers. radon is the ground truth. The model is guessing from text.
`extract_json` always returns a `list` — `{}`, empty, or prose become `[]`, not a crash.
> 🎯 How many complexity numbers will the model get wrong?"""),
    code("""MY_GUESS_WRONG = 2
src = open(PATIENT_PY, encoding="utf-8").read()
guessed = extract_json(llm(
    f"```python\\n{src}\\n```\\nReturn JSON {{'findings':[{{'name': fn, 'complexity': int}}]}} for each function.",
    system_prompt="Compute McCabe cyclomatic complexity. Reply JSON only.",
    max_new_tokens=400, temperature=0.0,
))
radon_json = json.loads(subprocess.run(["radon", "cc", "-j", PATIENT_PY],
                                      capture_output=True, text=True).stdout or "{}")
truth = {b["name"]: b["complexity"] for blocks in radon_json.values() for b in blocks}
wrong = 0
for g in guessed:
    name = (g.get("name") or "").split(".")[-1]
    if name in truth and g.get("complexity") != truth[name]:
        wrong += 1
        print(f"miss {name}: model={g.get('complexity')} radon={truth[name]}")
print("wrong:", wrong, "of", len(truth))
quiz("zero-shot complexity misses", MY_GUESS_WRONG, lambda g: abs(g - wrong) <= 2,
     "A metric you cannot trust to ±1 is a metric you cannot gate on.")"""),
    hint_sol(
        "The model is doing arithmetic in English. Expect misses. A good guess is “a couple,” not zero.",
        "Any `MY_GUESS_WRONG` within ±2 of the printed `wrong` count is fine. If the model returns empty JSON, `extract_json` gives `[]` and `wrong` stays 0 — that is a *contract* miss, still a reason not to gate on the model.",
    ),
    md("""## 1.7 · MLScent on [pytorch/examples mnist](https://github.com/pytorch/examples/blob/main/mnist/main.py)
[MLScent](https://github.com/KarthikShivasankar/ml_smells_detector) (CAIN 2025) walks an AST for
*training-loop* anti-patterns. It does **not** import PyTorch. Typical hits to look for:

1. **Missing random seed** — `torch.manual_seed` / `numpy` seed absent → irreproducible runs.
2. **Missing eval mode** — dropout / batch-norm stay in train mode at test time.
3. **Magic batch size / learning rate** — a bare `64` or `0.01` with no name.

Different eyes, same idea: the tool measures, the model will interpret."""),
    code("""def run_mlscent(project_dir: str) -> str:
    subprocess.run(["ml_smell_detector", "analyze", project_dir],
                   capture_output=True, text=True, timeout=600)
    p = pathlib.Path("output/analysis_report.txt")
    return p.read_text()[:2500] if p.exists() else "no MLScent report"

mls = run_mlscent(ML_PATIENT_DIR)
print(mls[:2000])
low = mls.lower()
for needle in ("seed", "eval", "magic", "dropout", "batch"):
    print(f"  mention {needle!r}:", needle in low)"""),
    md("""## 1.8 · Agent — four slots
**role** (system prompt) · **brain** (`llm`) · **tools** (PyExamine + radon) · **contract** (JSON findings).

**Example.** Change only the tools and you get an ML auditor. Change only the role and you get a documenter.
The `think()` / `use_tools()` skeleton stays. That is the move we reuse all afternoon.

`audit()` runs tools **first**, then the model. If `json_mode` comes back empty we retry without it."""),
    code("""class Agent:
    def __init__(self, name, system_prompt, tools=None):
        self.name, self.system_prompt, self.tools = name, system_prompt, tools or {}
    def use_tools(self, *args):
        bits = []
        for n, fn in self.tools.items():
            print(" tool", n)
            try:
                bits.append(f"=== {n} ===\\n{fn(*args)}")
            except Exception as e:
                bits.append(f"=== {n} FAILED: {e} ===")
        return "\\n\\n".join(bits)
    def think(self, prompt, **kw):
        return llm(prompt, system_prompt=self.system_prompt, **kw)

AUDITOR_PROMPT = '''You are a senior reviewer. Use ONLY the tool evidence plus the source.
Reply with JSON {"findings":[{"smell","location","severity","why","fix"}]} — at most 6.'''

auditor = Agent("Code Auditor", AUDITOR_PROMPT,
                {"pyexamine": run_pyexamine_for_file, "radon": run_radon})

def audit(path: str) -> list[dict]:
    evidence = auditor.use_tools(path)
    raw = auditor.think(
        f"SOURCE ({path}):\\n```python\\n{open(path, encoding='utf-8').read()}\\n```\\nEVIDENCE:\\n{evidence}\\nJSON now.",
        max_new_tokens=900, temperature=0.1, json_mode=True,
    )
    findings = extract_json(raw)
    if not findings:
        raw = auditor.think(
            f"SOURCE ({path}):\\n```python\\n{open(path, encoding='utf-8').read()[:4000]}\\n```\\nEVIDENCE:\\n{evidence}\\nJSON now.",
            max_new_tokens=900, temperature=0.1, json_mode=False,
        )
        findings = extract_json(raw)
    return findings

findings = audit(PATIENT_PY)
print(json.dumps(findings, indent=2)[:2000])"""),
    md("""## 1.9 · Same skeleton, MLScent eyes
Swap `tools={"mlscent": run_mlscent}`. Keep `AUDITOR_PROMPT`. That is the whole trick."""),
    code("""ml_auditor = Agent("ML Auditor", AUDITOR_PROMPT, {"mlscent": run_mlscent})

def ml_audit(project_dir: str) -> list[dict]:
    evidence = ml_auditor.use_tools(project_dir)
    raw = ml_auditor.think(f"MLSCENT:\\n{evidence}\\nJSON findings now.", max_new_tokens=700, json_mode=True)
    out = extract_json(raw)
    return out or extract_json(ml_auditor.think(f"MLSCENT:\\n{evidence}\\nJSON now.", json_mode=False))

ml_findings = ml_audit(ML_PATIENT_DIR)
print(json.dumps(ml_findings, indent=2)[:1500])"""),
    md("""## 1.10 · Exercise
Add a tool, don't rewrite the agent. Walk the AST for magic numbers (you already did this by hand in 1.1),
hang it on `auditor.tools`, then optionally re-run `audit(PATIENT_PY)`."""),
    hint_sol(
        "You already have `find_magic_numbers` below. The missing step is treating it like PyExamine: put it in `auditor.tools` and call `audit()` again so the model *sees* the dump.",
        """```python
auditor.tools["magic_numbers"] = find_magic_numbers
print(find_magic_numbers(PATIENT_PY))
findings = audit(PATIENT_PY)   # tools now include magic_numbers
```
Skip `0`, `1`, `-1`, and bools — those are idiomatic, not smells. A hit like `3600` on a timeout *is*.""",
    ),
    code("""def find_magic_numbers(path: str) -> str:
    tree = ast.parse(open(path, encoding="utf-8").read())
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \\
                and node.value not in (0, 1, -1) and not isinstance(node.value, bool):
            hits.append(f"L{node.lineno}: {node.value}")
    return "\\n".join(hits) or "none"

auditor.tools["magic_numbers"] = find_magic_numbers
print(find_magic_numbers(PATIENT_PY)[:500])"""),
    code("""json.dump(findings, open("findings.json", "w"), indent=2)
print("saved", len(findings), "findings")
cost_report()
pit_stop("Part 1")
if not findings:
    print("warning: empty audit — re-run the auditor cell; Part 2 can still start")
else:
    print("Part 1 ready")"""),
]

cells += [
    md("""# Part 2 · Cooperative team  ·  1:10–1:50
Think of a hospital: triage (planner), nurse (auditor), surgeon (refactorer), lab (QA).
The lab does not take the surgeon's word. If the blood work fails, the reason goes back on the **blackboard**.

| Role | Slot | Contract |
|---|---|---|
| **Auditor** | tools then `llm` | JSON findings (≤6) |
| **Planner** | `llm` on those findings | JSON — at most 3 smells to fix *now* |
| **Refactorer** | `llm` + HARD RULES | one ```python``` fence, full module |
| **QA** | **no LLM** | `ast.parse` → pytest → Δ CC |
| **Orchestrator** | a `for` loop | `accepted` only if all three gates pass |
| **Deep Agent coordinator** | Part 3 | plans, writes files, hires subagents |

Do **not** add a second LLM “critic” before QA. That doubles cost and lets the thing that hallucinates certify itself.

## 2.1 · Blackboard
`WorkflowState` is the only shared memory. If it is not on the board, it did not happen.
`record()` prints a timeline — that log *is* the demo."""),
    code("""from dataclasses import dataclass, field
import shutil, tempfile

@dataclass
class WorkflowState:
    source_path: str
    test_file: str = ""
    original_code: str = ""
    candidate_code: str = ""
    findings: list = field(default_factory=list)
    verdict: dict = field(default_factory=dict)
    accepted: bool = False
    iteration: int = 0
    history: list = field(default_factory=list)
    def record(self, agent, event, detail=""):
        line = f"{agent:12} | {event:22} | {detail}"
        self.history.append(line)
        print(line)

state = WorkflowState(source_path=PATIENT_PY, test_file=PATIENT_TESTS)
state.original_code = open(PATIENT_PY, encoding="utf-8").read()
state.findings = findings if findings else (json.load(open("findings.json")) if pathlib.Path("findings.json").exists() else [])
state.record("system", "ready", f"{len(state.original_code)} chars")"""),
    md("""## 2.2 · Planner — pick three, not everything
A backlog of six smells is not a patch. The planner returns the same JSON shape as the auditor
(`{"findings":[...]}`) so `extract_json` stays the contract. At most three."""),
    code("""PLANNER_PROMPT = '''You are a tech-lead. Pick what to fix *this iteration*.
Reply JSON {"findings":[{"smell","location","why","fix"}]} — at most 3.
Prefer high-interest, low-principal items. Do not invent smells that are not in the list.'''

def plan(state: WorkflowState) -> WorkflowState:
    state.record("planner", "ranking", f"{len(state.findings)} findings")
    raw = llm(
        f"FINDINGS:\\n{json.dumps(state.findings, indent=1)}\\nPick at most 3.",
        system_prompt=PLANNER_PROMPT, max_new_tokens=400, temperature=0.1, json_mode=True,
    )
    focus = extract_json(raw)[:3]
    if focus:
        state.findings = focus
        state.record("planner", "focus", ", ".join(f.get("smell", "?") for f in focus))
    else:
        state.findings = state.findings[:3]
        state.record("planner", "focus", "first 3 (empty plan JSON)")
    return state

state = plan(state)
print(json.dumps(state.findings, indent=2)[:800])"""),
    md("""## 2.3 · Refactorer — keep `TimestampSigner` / `TimedSerializer` public API
HARD RULES are the contract. `extract_code_block` takes the **last** ```python``` fence (models love a preamble).
No fence → `ValueError` → orchestrator retries with that error as feedback."""),
    code("""REFACTORER_PROMPT = '''You refactor production Python.
HARD RULES:
1. Keep the public API (TimestampSigner, TimedSerializer and their methods/signatures).
2. Behaviour must stay identical — upstream tests are the contract.
3. Do not add third-party imports. Keep existing relative imports.
4. Reply with ONE ```python``` block containing the FULL module.
'''

def extract_code_block(text: str) -> str:
    blocks = re.findall(r"```(?:python)?\\s*\\n(.*?)```", text, re.DOTALL)
    if not blocks:
        raise ValueError("Refactorer produced no code block")
    return blocks[-1].strip() + "\\n"

def refactor(state: WorkflowState) -> WorkflowState:
    state.record("refactorer", "thinking", f"{len(state.findings)} findings")
    reply = llm(
        f"MODULE:\\n```python\\n{state.original_code}\\n```\\nFINDINGS:\\n{json.dumps(state.findings, indent=1)}\\nRewrite the full file.",
        system_prompt=REFACTORER_PROMPT, max_new_tokens=3500, temperature=0.1,
    )
    state.candidate_code = extract_code_block(reply)
    state.record("refactorer", "candidate", f"{len(state.candidate_code)} chars")
    return state
print("refactorer ready")"""),
    md("""## 2.4 · QA — no LLM
Cheapest gate first. Gate 1 is the `ast.parse` you ran in §1.1.

**Example.** Deleting `unsign` fails gate 1 in microseconds. Inverting `max_age` looks clean and dies on gate 2
(`test_max_age`). Adding nested `if`s fails gate 3 (CC went up).

Gate 2 copies `src/itsdangerous/` into a temp dir, overlays `timed.py`, and runs the nested upstream file."""),
    code("""def avg_complexity(path: str) -> float:
    raw = subprocess.run(["radon", "cc", "-j", path], capture_output=True, text=True).stdout
    data = json.loads(raw or "{}")
    scores = [b["complexity"] for blocks in data.values() for b in blocks]
    return sum(scores) / len(scores) if scores else 0.0

def qa_verify(state: WorkflowState) -> WorkflowState:
    v = {"syntax": False, "tests": False, "improved": False, "notes": []}
    try:
        ast.parse(state.candidate_code)
        v["syntax"] = True
    except SyntaxError as e:
        v["notes"].append(str(e)); state.verdict = v
        state.record("qa", "reject gate 1", str(e)[:80]); return state
    src = pathlib.Path(state.source_path)
    pkg = src.parent
    with tempfile.TemporaryDirectory() as tmp:
        sandbox_pkg = pathlib.Path(tmp) / pkg.name
        shutil.copytree(pkg, sandbox_pkg)
        (sandbox_pkg / src.name).write_text(state.candidate_code, encoding="utf-8")
        if state.test_file:
            tpath = pathlib.Path(state.test_file).resolve()
            env = os.environ.copy()
            extra = [tmp]
            cwd = tmp
            target = tpath.name
            if tpath.parent.name == "test_itsdangerous":
                extra.append(str(tpath.parent.parent))
                cwd = str(tpath.parents[2])
                target = str(tpath)
            else:
                shutil.copy(tpath, pathlib.Path(tmp) / tpath.name)
            env["PYTHONPATH"] = os.pathsep.join(extra + [str(pkg.parent), env.get("PYTHONPATH", "")])
            r = subprocess.run([sys.executable, "-m", "pytest", "-q", target],
                               cwd=cwd, capture_output=True, text=True, timeout=180, env=env)
            v["tests"] = r.returncode == 0
            if not v["tests"]:
                v["notes"].append(r.stdout[-600:] or r.stderr[-400:])
                state.verdict = v; state.record("qa", "reject gate 2", "tests failed"); return state
        else:
            v["tests"] = True
        v["cc_before"] = round(avg_complexity(state.source_path), 2)
        v["cc_after"] = round(avg_complexity(str(sandbox_pkg / src.name)), 2)
        v["improved"] = v["cc_after"] <= v["cc_before"]
        if not v["improved"]:
            v["notes"].append(f"CC {v['cc_before']} -> {v['cc_after']}")
            state.verdict = v; state.record("qa", "reject gate 3", v["notes"][-1]); return state
    state.verdict = v
    state.record("qa", "accept", f"CC {v['cc_before']} -> {v['cc_after']}")
    return state
print("QA ready — no LLM")"""),
    md("""## 2.5 · Orchestrator
`audit → plan → refactor → qa`. Failures are appended as `QA FAILED` so the next rewrite sees *why*.
`accepted` only if syntax **and** tests **and** CC did not get worse.

**Example.** Iteration 1: missing code fence → `ValueError` → feedback string → iteration 2 gets that error in the prompt."""),
    code("""def run_workflow(source_path: str, test_file: str, max_iterations: int = 3) -> WorkflowState:
    st = WorkflowState(source_path=source_path, test_file=test_file)
    st.original_code = open(source_path, encoding="utf-8").read()
    st.record("orch", "audit")
    st.findings = audit(source_path)
    st = plan(st)
    feedback = ""
    for st.iteration in range(1, max_iterations + 1):
        if feedback:
            st.findings = st.findings + [{"smell": "QA FAILED", "why": feedback[:400], "fix": "fix the module"}]
        try:
            st = refactor(st)
        except ValueError as e:
            feedback = str(e); continue
        st = qa_verify(st)
        v = st.verdict
        if v.get("syntax") and v.get("tests") and v.get("improved"):
            st.accepted = True; break
        feedback = " | ".join(v.get("notes", []))[:400]
    st.record("orch", "done", "ACCEPTED" if st.accepted else "held")
    return st

state = run_workflow(PATIENT_PY, PATIENT_TESTS, max_iterations=2)
if state.accepted:
    open("timed_refactored.py", "w", encoding="utf-8").write(state.candidate_code)
    print("saved timed_refactored.py")
cost_report()"""),
    md("""## 2.6 · Sabotage
Imagine a PR titled “simplify expiry check.” The diff is one character: `>` → `<`.
Signed cookies would expire immediately — or never. Reviewers miss one-character diffs. Tests do not.
> 🎯 Set `MY_GUESS_CAUGHT` before you run. Will gate 2 catch it?"""),
    hint_sol(
        "Gate 2 runs *upstream* `test_max_age`. That test freezes time and expects `age > max_age` to raise `SignatureExpired`.",
        "`MY_GUESS_CAUGHT = True`. After the cell, `caught` should be True and the notes mention `test_max_age`. If it is False, the overlay path is wrong — check `PATIENT_TESTS` is the nested file.",
    ),
    code("""MY_GUESS_CAUGHT = True
evil = open(PATIENT_PY, encoding="utf-8").read().replace("if age > max_age:", "if age < max_age:")
assert evil != open(PATIENT_PY, encoding="utf-8").read(), "pattern not found — inspect timed.py"
demo = WorkflowState(source_path=PATIENT_PY, test_file=PATIENT_TESTS)
demo.original_code = open(PATIENT_PY, encoding="utf-8").read()
demo.candidate_code = evil
demo = qa_verify(demo)
caught = not demo.verdict.get("tests")
print("caught" if caught else "MISSED", demo.verdict.get("notes", [""])[0][:400])
quiz("gate 2 catches max_age sabotage", MY_GUESS_CAUGHT, caught,
     "Never let the model certify itself. The real test suite is the gate.")"""),
    md("""## 2.7 · Exercise
Pick one: **A** write a Documenter agent · **B** add a maintainability-index gate · **C** delete one HARD RULE and predict the failure."""),
    hint_sol(
        "**A** clone `Agent` with a different system prompt and no tools (or only `radon`). **B** `radon mi -j` returns a score; reject if it drops. **C** drop rule 1 (public API) and watch `test_timed.py` ImportError / AttributeError.",
        """**A Documenter**
```python
doc = Agent("Documenter", "Write a 8-line module docstring from the source. No code.", {})
print(doc.think(open(PATIENT_PY, encoding="utf-8").read()[:3000], max_new_tokens=300))
```
**B MI gate** (inside `qa_verify`, after CC):
```python
def mi(path):
    data = json.loads(subprocess.run(["radon", "mi", "-j", path], capture_output=True, text=True).stdout or "{}")
    return next(iter(data.values())).get("mi", 0)
if mi(str(sandbox_pkg / src.name)) < mi(state.source_path) - 1:
    v["notes"].append("MI dropped"); ...
```
**C** Delete HARD RULE 1 and re-run `run_workflow`. Expected: gate 2 fails (`TimestampSigner` renamed or removed). That rule is load-bearing.""",
    ),
    code("""pit_stop("Part 2")
print("Part 2 checkpoint")"""),
]

cells += [
    md("""# Part 3 · Frameworks — LangChain, LangGraph, Deep Agents  ·  1:50–2:30
You already built the team by hand. Frameworks are *the same loop with less glue* — not a different religion.

## 3.1 · The stack (read this before you import anything)

| Layer | What it is | What we use it for today |
|---|---|---|
| `openai` client | HTTP to OpenRouter. Messages in, text out. | Parts 0–2. You already wrote `llm()`. |
| **LangChain** | Wrappers around that client: `ChatOpenAI`, message objects, tool-calling. One model object you can hand to a framework. | `openrouter_chat_model()` — same key, same slug, LangChain-shaped. |
| **LangGraph** | A **state machine** on top of LangChain. You declare nodes (functions), edges, and a `TypedDict` blackboard. Conditional edges retry. | The *same* auditor → refactorer → qa loop, typed. |
| **Deep Agents** | A batteries-included LangGraph harness: planner (todo list), filesystem tools, `task` to spawn **subagents**. | Coordinator + PyExamine subagent + MLScent subagent. |

**Mental model.** LangChain = “talk to a model + tools.” LangGraph = “that talk is a node in a graph with memory.”
Deep Agents = “here is a pre-built graph that can plan and hire helpers.”

| Word | Meaning |
|---|---|
| *Message* | A `{role, content}` turn. We already passed these to `chat.completions.create`. |
| *Tool / function calling* | The model returns “call `radon` with this path”; the runtime runs it; the result comes back as a message. |
| *State* | The blackboard. Part 2: `WorkflowState`. LangGraph: `TeamState(TypedDict)`. |
| *Node* | A function `state → delta`. It returns fields to merge; it does not rewrite the world. |
| *Edge* | What runs next. `accepted` → END, else → refactorer. |
| *Subagent* | A specialist the coordinator starts via `task`, with its own prompt and tools, so context stays clean. |

**Do not** pass `model="openai:{slug}"` to Deep Agents — that looks up `OPENAI_API_KEY` and api.openai.com.
Always `openrouter_chat_model()`.

## 3.2 · LangGraph — the same loop, typed
`StateGraph` + `TypedDict`. Nodes return **deltas**. A conditional edge on `accepted` retries the refactorer."""),
    code("""from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class TeamState(TypedDict):
    source: str
    findings: str
    candidate: str
    verdict: str
    accepted: bool
    iteration: int

def auditor_node(s: TeamState) -> dict:
    return {"findings": llm(s["source"][:4000], system_prompt=AUDITOR_PROMPT, max_new_tokens=400)}

def refactorer_node(s: TeamState) -> dict:
    try:
        code = extract_code_block(llm(
            f"MODULE:\\n```python\\n{s['source']}\\n```\\nSMELLS:\\n{s['findings']}",
            system_prompt=REFACTORER_PROMPT, max_new_tokens=3500))
        return {"candidate": code, "iteration": s["iteration"] + 1}
    except ValueError as e:
        return {"candidate": "", "verdict": str(e), "iteration": s["iteration"] + 1}

def qa_node(s: TeamState) -> dict:
    if not s["candidate"]:
        return {"accepted": False}
    tmp = WorkflowState(source_path=PATIENT_PY, test_file=PATIENT_TESTS,
                        original_code=s["source"], candidate_code=s["candidate"])
    tmp = qa_verify(tmp)
    v = tmp.verdict
    ok = bool(v.get("syntax") and v.get("tests") and v.get("improved"))
    return {"accepted": ok, "verdict": str(v.get("notes") or "ok")}

def _route(s: TeamState) -> str:
    if s["accepted"]:
        return "done"
    return "give_up" if s["iteration"] >= 2 else "retry"

g = StateGraph(TeamState)
g.add_node("auditor", auditor_node); g.add_node("refactorer", refactorer_node); g.add_node("qa", qa_node)
g.add_edge(START, "auditor"); g.add_edge("auditor", "refactorer"); g.add_edge("refactorer", "qa")
g.add_conditional_edges("qa", _route, {"done": END, "retry": "refactorer", "give_up": END})
team = g.compile()
print("langgraph ready — auditor → refactorer → qa (retry or end)")"""),
    code("""lg = team.invoke({"source": open(PATIENT_PY, encoding="utf-8").read(),
                  "findings": "", "candidate": "", "verdict": "",
                  "accepted": False, "iteration": 0})
print("accepted", lg["accepted"], "iter", lg["iteration"])
cost_report()"""),
    md("""## 3.3 · Deep Agents — coordinator + two detector subagents
Built-ins you do not want to hand-roll: a **todo-list planner**, **filesystem** tools
(`ls` / `read_file` / `write_file`), and `task` to spawn specialists.

- `pyexamine_auditor` — wraps `analyze_code_quality` (truncated).
- `mlscent_auditor` — wraps `ml_smell_detector` (truncated).
- Main coordinator writes `COOP_AUDIT.md`. That file *is* the cooperative artifact.

Guardrails: tool stdout capped at ~2k chars, 120 s timeout, `recursion_limit` capped,
prompt says “at most 6 tool calls.” If this stalls, skip to reading a neighbour’s `COOP_AUDIT.md`."""),
    code("""from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

def _safe(path: str) -> str:
    p = pathlib.Path(path)
    p = (p if p.is_absolute() else WORKDIR / p).resolve()
    return str(p) if p == WORKDIR or WORKDIR in p.parents else str(WORKDIR)

def pyexamine_tool(path: str) -> str:
    '''PyExamine on a file or directory. Truncated so the context window survives.'''
    target = _safe(path)
    d = target if pathlib.Path(target).is_dir() else str(pathlib.Path(target).parent)
    return run_pyexamine(d)[:2000]

def mlscent_tool(path: str) -> str:
    '''MLScent on an ML project directory. Truncated.'''
    return run_mlscent(_safe(path))[:2000]

_subs = [
    {
        "name": "pyexamine_auditor",
        "description": "Run PyExamine on a Python package directory and list code smells.",
        "system_prompt": "You only call pyexamine_tool. Return at most 8 smells. Do not refactor.",
        "prompt": "You only call pyexamine_tool. Return at most 8 smells. Do not refactor.",
    },
    {
        "name": "mlscent_auditor",
        "description": "Run MLScent on an ML training directory and list anti-patterns.",
        "system_prompt": "You only call mlscent_tool. Call out seed, eval mode, magic numbers. Do not refactor.",
        "prompt": "You only call mlscent_tool. Call out seed, eval mode, magic numbers. Do not refactor.",
    },
]
_kw = dict(
    model=openrouter_chat_model(),
    tools=[pyexamine_tool, mlscent_tool],
    backend=FilesystemBackend(root_dir=str(WORKDIR)),
    system_prompt=(
        "You coordinate two specialists. At most 6 tool or task calls. "
        "Delegate Python smells to pyexamine_auditor and ML anti-patterns to mlscent_auditor. "
        "Write COOP_AUDIT.md (max 30 lines) with both summaries. Do not patch source files."
    ),
)
try:
    deep_team = create_deep_agent(**_kw, subagents=_subs)
except TypeError:
    deep_team = create_deep_agent(**_kw)
    print("note: this deepagents version ignored subagents — coordinator still has both tools")
print("deep agent ready")"""),
    code("""run = deep_team.invoke(
    {"messages": [(
        "user",
        f"Audit Python package {ITSD_ROOT} (file {PATIENT_PY}) with PyExamine "
        f"and ML project {ML_PATIENT_DIR} with MLScent. Write COOP_AUDIT.md.",
    )]},
    config={"recursion_limit": 30},
)
final = run["messages"][-1].content
if isinstance(final, list):
    final = "\\n".join(b.get("text", "") for b in final if isinstance(b, dict))
print(str(final)[:800])
for name in ("COOP_AUDIT.md", "AUDIT.md"):
    p = pathlib.Path(name)
    if p.exists():
        print("----", name, "----")
        print(p.read_text()[:800])
cost_report()
pit_stop("Part 3")"""),
]

cells += [
    md("""# Part 4 · Debt resolution and ship  ·  2:30–2:55
Interest = pain you feel this week. Principal = cost to fix. **priority = interest ÷ principal**.

**Worked example.** A stale Flask docstring (interest 8, principal 2) scores **4.0** — fix this afternoon.
A year-long HTTPX transport rewrite (interest 6, principal 9) scores **0.67** — don't start it in this workshop.

## 4.1 · Six real GitHub issues
Public tickets, not invented stories. Gold labels are our teaching key — the model does not see them."""),
    code("""ISSUES = [
  {"id": "pallets/flask#5214", "url": "https://github.com/pallets/flask/issues/5214",
   "gold": "documentation",
   "text": "Application Dispatching docs still call werkzeug.wsgi.peek_path_info and pop_path_info. Those were removed in Werkzeug 2.3. The documented example ImportErrors on current Flask."},
  {"id": "psf/requests#7016", "url": "https://github.com/psf/requests/issues/7016",
   "gold": "test",
   "text": "pytest reports 'recursive dependency involving fixture httpbin'. The suite does not run until pytest-httpbin is installed; contributing docs never say to pip install -r requirements-dev.txt."},
  {"id": "psf/requests#6637", "url": "https://github.com/psf/requests/issues/6637",
   "gold": "dependency",
   "text": "Dev extra pulls Werkzeug 3, but pytest-httpbin still imports parse_authorization_header, removed in Werkzeug 3. Tests only pass on Python 3.7 or if you pin Werkzeug<2.3."},
  {"id": "encode/httpx#3071", "url": "https://github.com/encode/httpx/issues/3071",
   "gold": "design",
   "text": "Client / AsyncClient share a large surface and transport stack. Adding HTTP/2 and SOCKS options keeps landing in the same classes. Changes in one area regress unrelated transports."},
  {"id": "pylint-dev/pylint#9670", "url": "https://github.com/pylint-dev/pylint/issues/9670",
   "gold": "code",
   "text": "Checker names and message IDs drifted; several checkers still use abbreviations only the original author remembers. Reviewing a new checker takes extra time just to decode identifiers."},
  {"id": "django/django#35091", "url": "https://github.com/django/django/issues/35091",
   "gold": "build",
   "text": "Release docs still describe a multi-step manual process around translations and wheels. A missed step in the last cycle delayed the upload. CI does not gate the checklist."},
]
print(len(ISSUES), "real issues")"""),
    md("""## 4.2 · Classifier  > 🎯 `MY_GUESS_ACCURACY`
Closed set of 8 labels. `snap_label` keeps the first token if it is in the set; anything else (including empty) becomes `code`.

**Example.** Model replies `documentation debt.` → first token `documentation` → hit.
Model replies `this is really a docs issue` → first token `this` → snap to `code`."""),
    hint_sol(
        "Zero-shot on 6 real issues is noisy. Guess a band (60–80%), not a precise 73%.",
        "`MY_GUESS_ACCURACY = 70` is a fair prior. The quiz accepts ±20 points. Empty model replies become `code`, which *hurts* accuracy — another reason for `snap_label`.",
    ),
    code("""MY_GUESS_ACCURACY = 70
LABELS = ["design", "code", "test", "documentation", "dependency", "build", "defect", "requirement"]
CLASSIFIER_PROMPT = f"Classify the issue. Reply with ONE word from: {', '.join(LABELS)}."

def classify_issue(text: str) -> str:
    reply = llm(f"ISSUE:\\n{text}\\nLabel:", system_prompt=CLASSIFIER_PROMPT,
                max_new_tokens=16, temperature=0.0)
    return snap_label(reply, LABELS)

import pandas as pd
rows = []
for issue in ISSUES:
    pred = classify_issue(issue["text"])
    rows.append({"id": issue["id"], "gold": issue["gold"], "pred": pred,
                 "ok": pred == issue["gold"], "url": issue["url"]})
df = pd.DataFrame(rows)
acc = float(df["ok"].mean())
print(f"accuracy {acc:.0%}")
quiz("zero-shot accuracy %", MY_GUESS_ACCURACY, lambda g: abs(g - acc * 100) <= 20,
     "Closed label set + snap_label. Empty model replies become 'code', not a crash.")
df"""),
    md("""## 4.3 · Triage
JSON `interest` / `principal`. We coerce bad numbers to 5, and `principal` is at least 1 so we never divide by zero."""),
    code("""TRIAGE_PROMPT = '''Score technical debt. Reply JSON {"interest":1-10,"principal":1-10,"rationale":"..."}.'''

def triage(issue) -> dict:
    raw = llm(f"ISSUE:\\n{issue['text']}", system_prompt=TRIAGE_PROMPT, max_new_tokens=120, json_mode=True)
    data = extract_json(raw)
    row = data[0] if data else {}
    try:
        interest = float(row.get("interest", 5)); principal = max(float(row.get("principal", 5)), 1)
    except (TypeError, ValueError):
        interest, principal = 5.0, 5.0
    return {"interest": interest, "principal": principal, "priority": round(interest / principal, 2),
            "rationale": row.get("rationale", "")}

ranked = [{**i, **triage(i), "type": classify_issue(i["text"])} for i in ISSUES]
ranked.sort(key=lambda r: -r["priority"])
pd.DataFrame(ranked)[["id", "type", "interest", "principal", "priority"]]"""),
    md("""## 4.4 · Full pipeline → `TECH_DEBT_REPORT.md`
Classify + triage the backlog, audit `timed.py`, optionally ship a gated patch, write one markdown file.
Point `run_workflow` at your own module later — use *that* repo’s tests, not `test_timed.py`."""),
    code("""def full_pipeline(code_path: str, test_file: str, issues: list, max_iterations: int = 2) -> str:
    print("classify + triage")
    ranked = []
    for it in issues:
        s = triage(it)
        ranked.append({**it, "type": classify_issue(it["text"]), **s})
    ranked.sort(key=lambda r: -r["priority"])
    print("audit")
    code_findings = audit(code_path)
    print("refactor/QA")
    st = run_workflow(code_path, test_file, max_iterations=max_iterations)
    lines = ["# Technical Debt Report", "", f"model: {model_name()}", "",
             "## Backlog", ""]
    for r in ranked[:6]:
        lines.append(f"- [{r['id']}]({r['url']}) · {r['type']} · priority {r['priority']}: {r['text'][:140]}")
    lines += ["", "## Code findings", ""]
    for f in code_findings:
        lines.append(f"- **{f.get('smell','?')}** ({f.get('location','?')}): {f.get('why','')}")
    lines += ["", "## Refactor", "",
              f"- accepted={st.accepted} after {st.iteration} iteration(s)"]
    if st.accepted:
        open("timed_refactored.py", "w", encoding="utf-8").write(st.candidate_code)
        lines.append("- wrote timed_refactored.py")
    report = "\\n".join(lines)
    open("TECH_DEBT_REPORT.md", "w", encoding="utf-8").write(report)
    return report

report = full_pipeline(PATIENT_PY, PATIENT_TESTS, ISSUES, max_iterations=2)
print(report[:1500])
cost_report()"""),
    md("""## 4.5 · `debtbuster` — the packaged version of Parts 1–2
This is the **workshop folder**. `brain.py` talks to OpenRouter. `tools.py` already calls **PyExamine**.
`pip install -e ./debtbuster` so edits in `brain.py` / `gates.py` are live.

| file | job |
|---|---|
| `brain.py` | only file that calls a model |
| `config.py` | `LLM_MODEL`, temperature, max iterations |
| `tools.py` | radon + PyExamine (no LLM) |
| `gates.py` | syntax → pytest → Δ CC |
| `graph.py` | auditor → refactorer ↔ qa |
| `cli.py` | `audit` / `fix`, exit 0 or 1 |

> 🎯 `MY_GUESS_EXIT` — 0 accepted or 1 gate held. A traceback is a bug, not a verdict."""),
    hint_sol(
        "The CLI is the same loop you built. A held gate is a *success of the design*. Only a Python traceback is a harness bug.",
        "`MY_GUESS_EXIT` is **0** if the model produces a patch that passes all three gates, else **1**. Either is a valid workshop outcome. `crashed=True` means re-install `-e ./debtbuster` and check `OPENROUTER_API_KEY` is still in `os.environ`.",
    ),
    code("""MY_GUESS_EXIT = 0
pkg = None
for cand in (WORKSHOP_ROOT / "debtbuster",
             pathlib.Path.cwd().parent / "debtbuster",
             pathlib.Path("/content/LLMA4SE-Workshop4/debtbuster")):
    if (cand / "pyproject.toml").is_file():
        pkg = cand.resolve(); break
if pkg is None:
    dest = (pathlib.Path("/content/LLMA4SE-Workshop4") if pathlib.Path("/content").exists()
            else WORKDIR.parent / "LLMA4SE-Workshop4")
    if not (dest / "debtbuster" / "pyproject.toml").is_file():
        subprocess.run(["git", "clone", "--depth", "1",
                        "https://github.com/KarthikShivasankar/LLMA4SE-Workshop4.git",
                        str(dest)], check=True)
    pkg = (dest / "debtbuster").resolve()
print("installing", pkg)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-e", str(pkg)], check=True)
print(subprocess.run(["debtbuster", "--help"], capture_output=True, text=True).stdout)"""),
    code("""print("audit")
a = subprocess.run(["debtbuster", "audit", PATIENT_PY], capture_output=True, text=True)
print(a.stdout[:800], a.stderr[:400])
print("fix")
f = subprocess.run(["debtbuster", "fix", PATIENT_PY, "--tests", PATIENT_TESTS],
                   capture_output=True, text=True)
print(f.stdout[-800:] or f.stderr[-800:])
exit_code = f.returncode
crashed = "Traceback" in (f.stderr + f.stdout)
print("exit", exit_code, "crashed" if crashed else "")
if crashed:
    print("harness bug — not a gate verdict")
else:
    quiz("debtbuster exit", MY_GUESS_EXIT, exit_code,
         "0 = accepted patch; 1 = gate held. Only if stderr is clean.")
pit_stop("Part 4")"""),
    md("""# Wrap-up
**The restaurant.** The thermometer (tools) reads 47 °C. The critic (LLM) says “over-reduced.”
The health inspector (gate) stamps the plate — or sends it back. The critic does not stamp the plate.

1. Tools measure; the LLM interprets; a gate decides.
2. The thing that can hallucinate must not certify that it did not.
3. Capability grows through tools and verification, not bigger models.

| When you want… | Use |
|---|---|
| To *understand* the loop | Hand-rolled `Agent` + blackboard (Part 2) |
| The same loop, typed retries | **LangGraph** (`StateGraph` + `TypedDict`) |
| Planning, files, specialist helpers | **Deep Agents** (coordinator + subagents) |
| A CLI you can take home | `debtbuster audit` / `fix` |

The OpenRouter key stays in `os.environ`. The client is `openai.OpenAI(base_url=https://openrouter.ai/api/v1)`.
Detectors: [PyExamine](https://github.com/KarthikShivasankar/python_smells_detector) · [MLScent](https://github.com/KarthikShivasankar/ml_smells_detector).
Take-home: `pip install -e ./debtbuster` then `debtbuster fix path.py --tests tests.py`."""),
    code("""cost_report()
scoreboard()
print("done")"""),
]

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        "colab": {"provenance": [], "toc_visible": True},
    },
    "cells": cells,
}

NB.write_text(json.dumps(nb, indent=2), encoding="utf-8")
print("wrote", NB, "cells", len(cells), "bytes", NB.stat().st_size)
