# Instructor Guide — Workshop 4: Cooperative LLM Agent Workflows
### LLMA4SE 2026 · Day 3 · Fri Sep 11 · 15:00–18:00 · Karthik Shivashankar & Adela Nedisan Videsjorden

**The one-sentence thesis of the workshop:** *deterministic tools measure, LLMs interpret, verification gates decide — and the architecture matters more than the model size.* Every section returns to it. If a discussion drifts, steer back here.

**Before the session (day before, non-negotiable):**
- [ ] Run all three notebooks end-to-end on a fresh free-tier Colab account (not your Pro account) — package versions drift.
- [ ] Upload the three notebooks somewhere one-click for students (Drive folder or GitHub repo; QR code on screen at 15:00).
- [ ] Have a second Google account ready as backup (free-tier GPU quota can run out).
- [ ] Open the pptx and this guide side-by-side.

**Co-teaching split (suggested):** one instructor drives slides/live demo, the other roams during hands-on blocks. Swap at each Part boundary. During roaming, look at *screens*, not faces — the students who need help are the silent ones with a red traceback.

---

## Run of show

### Block 0 · Welcome & setup ramp (15:00–15:12)

| Min | Slide | What you do |
|---|---|---|
| 15:00 | 1 | Welcome. Immediately show the QR/link and say: "open Part 1, switch runtime to T4 GPU, run the first four cells — *then* look back up here." Installs + model download run while you talk (~4 min of dead time absorbed). |
| 15:03 | 2 | Agenda. Promise: "at 18:00 you'll have a pipeline that audits, refactors, verifies, and writes a debt report — on a free GPU, with a 1.5B model." |
| 15:05 | 3 | Definitions: smell vs anti-pattern vs debt. Ask the room: "who has knowingly shipped debt this year?" (all hands go up — good, it normalizes the topic). |
| 15:08 | 4 | Debt economics. Key stat: ~23–42% of dev time wasted on debt. Frame the workshop as "agents as debt-servicing labor." |
| 15:10 | 5 | The detection toolbox: radon, pylint, PyExamine, MLScent. Talking point: "two of these tools come from our own research group — you'll wire all four into agents today." |

### Block 1 · Part 1: The Code Auditor (15:12–16:00, slides 6–8 + notebook)

| Min | What | Talking points / watchpoints |
|---|---|---|
| 15:12 | Slides 6–7 | Agent anatomy (role, brain, tools, contract). Hammer the split: **tools measure, LLM interprets**. Preempt the classic failure: "if you ask a 1.5B model to *count* complexity, it hallucinates. If radon counts and the model *explains*, it shines." |
| 15:18 | Slide 8 → notebook | Release them into sections 1.3–1.6. Milestones to call out loud: "patient's tests green?" (~15:22), "PyExamine report visible?" (~15:30 — remind them findings are in the *report file*, not stdout), "first audit JSON parsed?" (~15:38). |
| 15:40 | §1.7 ML Auditor | Regroup for 3 min before they run it: "same skeleton, we change only role + tools." After they run it, run the **discussion prompt in the notebook**: the `== np.nan` branch *never executes*, yet the script trains and prints an accuracy. Ask: "would your CI catch this?" (No — it's semantically wrong, not syntactically.) This is the single best minute in Part 1; don't skip it. |
| 15:47 | §1.8 Exercise 1 | Magic-number AST detector. Fast students: point to the ⭐ bonus (priority ordering via prompt). Struggling students: the solution is in a collapsed `<details>` tag — tell them it's allowed. |
| 15:57 | §1.9 checkpoint | Quiz answers aloud. Then the bridge line: "an auditor that only *complains* is a linter with opinions. Next: agents that *fix* — and an agent that stops them from lying about it." **Break 16:00–16:05.** |

### Block 2 · Part 2: The Refactoring Team (16:05–17:15, slides 9–13 + notebook)

| Min | What | Talking points / watchpoints |
|---|---|---|
| 16:05 | Slide 9 | The team diagram. Trace the loop with your hand: Auditor → Refactorer → QA → (reject) → back with feedback. "The orchestrator is 30 lines of plain Python. You do not need a framework to understand this — you need it later to *scale* it." |
| 16:10 | Slide 10 | Blackboard vs message-passing. Poll the room for a guess before revealing why we chose blackboard (auditability: `state.history` is a flight recorder). |
| 16:13 | Slide 11 | Verification gates funnel. **The most important slide of the day.** Say explicitly: "the QA agent has no LLM in it, *on purpose*. Never let the fox audit the henhouse." |
| 16:16 | notebook §2.0–2.4 | Setup re-runs (~4 min — remind: standalone by design). Milestones: workflow accepts a patch (~16:35 typical; 1–3 iterations is normal, rejections are *pedagogical*, say so before they happen or students think it's broken). |
| 16:40 | Slide 12 + failure lab | Six failure patterns. Then the sabotage demo: the notebook changes VAT 0.25→0.20 — a plausible-looking patch that gate 2 kills. Punchline: "the diff *looks* fine in review; only the pinned tests catch it. This is why 'LLM-as-judge' alone is not QA." |
| 16:55 | §2.6 Exercise 2 | Options A (docstring agent), B (MI gate), C (token budget), **D (ML refactoring team — no tests exist, so students must design a replacement gate from MLScent smell counts)**. D is the one to nudge ML-focused students toward; its closing questions ("what can a smell-count gate be fooled by?") make a great regroup discussion. |
| 17:12 | checkpoint | Regroup, 2-min share-out of one exercise result. **Break 17:15–17:20.** |

### Block 3 · Part 3: Debt Pipeline + capstone (17:20–17:55, slides 14–15 + notebook)

| Min | What | Talking points |
|---|---|---|
| 17:20 | Slide 14 | Principal/interest metaphor; BEACon-TD (JSS 2025) for classification; the triage quadrant (interest ÷ principal = priority). "High interest, low principal = quick wins — pay those first." |
| 17:26 | notebook §3.1–3.3 | Classifier on 10 labeled issues (accuracy vs gold — typically imperfect; discuss *why* constrained labels + temperature 0 still misfire), then triage agent. |
| 17:38 | §3.4 capstone | `full_pipeline()` — classify → triage → audit → refactor⇄QA → `TECH_DEBT_REPORT.md` (now with an MLScent section for the ML project). Have one student screen-share their report if A/V allows. |
| 17:48 | §3.5 BYO-code | "Paste 30–80 lines of your own code into `my_module.py` and run the pipeline." This is where the workshop becomes *theirs*. |
| 17:55 | Slide 18 | Wrap-up: the thesis one more time; where to go (LangGraph/AutoGen/CrewAI = same patterns, more plumbing); tool links; contact. Close at 18:00 sharp. |

### Bonus block · Part 4: Production frameworks (take-home, or 17:30+ for fast rooms)

Slides 16–17 + `Part4_Production_Frameworks.ipynb`. **Default stance: assign it as take-home** and spend 3 minutes on slide 16 only — the mapping table (hand-built → Ollama / LangGraph / Deep Agents / `debtbuster`) is the message; the notebook is self-contained. If ≥⅓ of the room finishes Part 3 by 17:35, offer it live instead of the BYO-code challenge.

Talking points for slide 16:
- "Everything you hand-built today has a production name. The **gates are byte-identical** across all versions — verification is a property of the task, not the framework."
- Ollama: "a model *server* — 7B at 4-bit is a stronger brain than this afternoon's 1.5B, in the same VRAM, loaded once for every agent."
- LangGraph: "your `run_workflow()` while-loop becomes conditional edges; you get the architecture diagram for free."
- Deep Agents: "planning + file tools + sub-agents. Honest framing: a local 7B is the *floor* of reliable tool-calling — variance is the lesson. Swap one line for a frontier model and reliability jumps."
- `debtbuster`: "5 files, its own tests, `pip install -e .`, exits 1 when the gate rejects — that's a CI job, not a demo."

Part 4 watchpoints: Ollama install + 7B pull ≈ 7 min (have them start it *before* reading §4.1); slow hotel Wi-Fi → `qwen2.5-coder:3b`; the deep-agent run occasionally skips `write_todos` or `AUDIT.md` — that's the scripted teachable moment, not a bug; `%pip install -e ./debtbuster` requires re-running the CLI cell if Colab caches the entry point (rare — restart runtime fixes it).

---

## Timing pressure valves

Running late? Cut in this order: (1) Exercise 1 bonus, (2) slide 10 poll, (3) shrink Exercise 2 to 8 min and demo option A yourself, (4) make §3.5 BYO-code "homework." Part 4 is take-home by default and never blocks the close. **Never cut:** the ML Auditor discussion, the sabotage demo, or the capstone run.

Running early? Extend: Exercise 2D discussion; ask students to break the refactorer's prompt invariants and watch gates catch it; or live-vary temperature on the classifier.

## Colab troubleshooting (the five things that will actually happen)

1. **"No GPU available."** Free quota exhausted (common late in the day). Fix: Runtime → change to CPU won't work for the model; instead have them switch the model string to `Qwen/Qwen2.5-Coder-0.5B-Instruct` (mentioned in the notebook) or pair up with a neighbor. Pairing is pedagogically fine.
2. **Model download feels stuck.** ~2 min is normal; the progress bar sometimes doesn't render. Tell them to wait for the ✅ print.
3. **Runtime disconnected / restarted.** Every notebook is standalone — re-run the setup section (~4 min). This is why setup cells are idempotent.
4. **PyExamine "prints nothing."** By design: findings go to `pyexamine_report.txt` (the wrapper reads the file). Students who call the CLI directly get confused here.
5. **Patch rejected 3× in Part 2.** Not a bug — the gate held. The notebook says so, but say it out loud too; then have them re-run (temperature>0 in the refactorer means the next attempt differs) or lower findings count.

MLScent-specific: it's a **git install** (`pip install git+https://…ml_smells_detector.git`); if a student's install cell failed, it's usually because they ran only the *first* pip line. Findings land in `output/analysis_report.txt`.

## Discussion prompt bank (use during roaming lulls)

- "Your QA gate is deterministic. What *can't* it ever catch?" (Requirements-level debt; smells that tests don't pin.)
- "Where would you add a human-in-the-loop in this pipeline, and where would that just be theater?"
- "The classifier hit X/10 on our gold labels. Would you trust it to *file* tickets? To *close* them?"
- "MLScent flagged 14 smells but the script 'works.' Which two would you fix before the paper deadline, and which before *deployment*?"
