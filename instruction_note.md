# Instruction Note — Workshop 4: Cooperative LLM Agent Workflows
### LLMA4SE 2026 · Day 3 · 15:00–18:00 · Karthik Shivashankar & Adela Nedisan Videsjorden

**The one-sentence thesis:** *deterministic tools measure, LLMs interpret, verification gates decide — and the architecture matters more than the model.* Every section returns to it. If a discussion drifts, steer back here.

**What changed from the previous edition:** one combined Colab notebook instead of four; the brain is now the **OpenAI API** instead of a local GPU model. Consequences you should say out loud at 15:00:
- **No GPU, no quota roulette, no 4-minute model download.** Setup is ~2 minutes.
- **The model is now genuinely strong**, so the pipeline accepts a patch on iteration 1 far more often. Rejections used to happen by accident; now you may have to *cause* one. The sabotage demo (§2.5) becomes the load-bearing failure lesson — do not skip it.
- **Students spend real money.** Roughly $0.05–0.25 each for the whole notebook. Say the number early; it removes anxiety and makes the cost meter interesting rather than scary.

---

## Before the session (day before, non-negotiable)

- [ ] Run the notebook end-to-end on a **fresh** Colab account. Package versions drift; `deepagents` in particular moves fast.
- [ ] Decide the key story and put it on a slide: **institutional keys you hand out**, or **students bring their own**. Do not leave this to 15:00.
  - Handing out keys? Create one key per table, set a **hard usage limit** in the OpenAI dashboard, and plan to revoke them at 18:00.
  - Students bring their own? Warn them **a week ahead** — a new account needs a payment method and can take a day to activate.
- [ ] Upload the notebook somewhere one-click (Drive or GitHub). **QR code on screen at 15:00.**
- [ ] Have `instruction_note.md` and the slides open side by side.
- [ ] Pre-run the notebook once yourself the same morning, so you can show a finished `TECH_DEBT_REPORT.md` if a student's run stalls.

**Co-teaching split:** one instructor drives slides and the live demo, the other roams during hands-on blocks. Swap at each Part boundary. While roaming, look at **screens, not faces** — the students who need help are the silent ones with a red traceback.

---

## Run of show

### Block 0 · Welcome & setup ramp (15:00–15:15)

| Min | Slide | What you do |
|---|---|---|
| 15:00 | 1 | Welcome. Immediately show the QR/link: "open the notebook, run Part 0 — **then** look back up here." The install runs while you talk. |
| 15:03 | 2 | Agenda + the promise: "at 18:00 you'll have a pipeline that audits, refactors, **verifies**, and writes a debt report." |
| 15:05 | 3 | Smell vs anti-pattern vs debt. Ask the room: *"who has knowingly shipped debt this year?"* All hands go up — good, it normalises the topic. |
| 15:08 | 4 | Debt economics: ~23–42% of dev time lost to debt. Frame the workshop as **agents as debt-servicing labour**. |
| 15:11 | 5 | The toolbox: radon, pylint, PyExamine, MLScent. "Two of these come from our own research group — you'll wire all four into agents today." |
| 15:13 | 6 | **The key slide.** Walk the room through §0.2/§0.3 live: `.env` vs Colab Secrets vs prompt. Then the smoke test. **Everyone must see a sentence come back from the model before you move on.** This is the only hard sync point of the day. |

> 🚨 **Watchpoint:** the most common failure of the whole workshop happens here — a key with no billing set up returns a 429/insufficient_quota. Have your backup key ready and move that student on; do not debug billing in front of 40 people.

### Block 1 · Part 1: The Code Auditor (15:15–16:05, slides 7–9)

| Min | What | Talking points / watchpoints |
|---|---|---|
| 15:15 | Slide 7 | Agent anatomy: role, brain, tools, contract. Hammer the split: **tools measure, LLM interprets**. Preempt the classic failure: *"ask a model to count complexity and it guesses; let radon count and the model explain, and it shines."* |
| 15:20 | Slide 8 → notebook §1.1–1.2 | Release them. Milestones to call out: "patient's 7 tests green?" (~15:24), "PyExamine report visible?" (~15:32 — remind them findings land in the **report file**, not stdout). |
| 15:38 | §1.3–1.4 | The `Agent` class and the first audit. When the JSON comes back, say: *"that JSON is the whole point. The next agent doesn't read English."* |
| 15:45 | §1.5 ML Auditor | Regroup for 3 min first: "same skeleton, we change only role + tools." Then run the discussion prompt: the `== np.nan` branch **never executes**, yet the script trains and prints an accuracy. *"Would your CI catch this?"* (No — it is semantically wrong, not syntactically.) **The best minute in Part 1. Do not skip it.** |
| 15:53 | §1.6 Exercise 1 | Magic-number AST detector. Struggling students: the solution is in a collapsed `<details>` — tell them it's allowed. Fast students: ask them to make the auditor *rank* by severity. |
| 16:03 | Bridge | *"An auditor that only complains is a linter with opinions. Next: agents that fix — and an agent that stops them from lying about it."* **Break 16:05–16:10.** |

### Block 2 · Part 2: The Refactoring Team (16:10–17:15, slides 10–14)

| Min | What | Talking points / watchpoints |
|---|---|---|
| 16:10 | Slide 10 | The team diagram. Trace the loop with your hand: Auditor → Refactorer → QA → (reject) → back **with feedback**. "The orchestrator is 30 lines of plain Python. You don't need a framework to understand this — you need one later to scale it." |
| 16:14 | Slide 11 | Blackboard vs message passing. Poll the room before revealing why we chose blackboard: **auditability** — `state.history` is a flight recorder. |
| 16:17 | Slide 12 | The verification-gate funnel. **The most important slide of the day.** Say it explicitly: *"the QA agent contains no LLM, on purpose. Never let the fox audit the henhouse."* |
| 16:20 | notebook §2.1–2.4 | Milestone: workflow accepts a patch (~16:35). With a frontier model this usually happens on **iteration 1** — tell them beforehand, so a clean run doesn't read as "nothing happened". Point them at `state.history` and the diff: *that* is the deliverable. |
| 16:42 | Slide 13 + §2.5 failure lab | Five failure patterns, then the sabotage: VAT 0.25 → 0.20. A plausible-looking patch that gate 2 kills in one second. Punchline: *"the diff looks fine in review; only the pinned tests catch it. This is why LLM-as-judge alone is not QA."* |
| 16:52 | Discussion | *"What sabotage would slip past our seven tests?"* (`add_item`'s unused params; float edge cases; refund of an unknown item.) Land it: **test debt silently lowers the ceiling on everything an agent is allowed to do.** |
| 16:58 | §2.6 Exercise 2 | A (Documenter agent), B (add an MI gate), C (delete a HARD RULE and see which was load-bearing). C produces the best share-outs. |
| 17:12 | Regroup | 2-minute share-out of one exercise result. **Break 17:15–17:20.** |

### Block 3 · Part 3: The Debt Pipeline + capstone (17:20–17:55, slides 15–16)

| Min | What | Talking points |
|---|---|---|
| 17:20 | Slide 15 | Principal vs interest; BEACon-TD (JSS 2025); the triage quadrant (`priority = interest ÷ principal`). *"High interest, low principal = quick wins. Pay those first."* |
| 17:26 | §3.1–3.3 | Classifier on 10 gold-labelled issues. Accuracy is typically 60–90%. **Spend time on the errors, not the score** — issue 110 is genuinely `code`, `design` *and* a process problem. That ambiguity is why BEACon-TD is multi-label. |
| 17:34 | Discussion | *"When do you prompt, and when do you fine-tune?"* Answers to draw out: consistency, latency, cost, privacy, and *no drift with prompt wording*. |
| 17:38 | §3.4 capstone | `full_pipeline()` → `TECH_DEBT_REPORT.md`. Have one student screen-share their report if A/V allows. |
| 17:46 | §3.5 BYO-code | *"Paste 30–80 lines of your own code, write two tests for it, run the pipeline."* **This is where the workshop becomes theirs.** Circulate hard here. |
| 17:55 | Slide 17 | Wrap-up: the thesis once more; the cost meter (`cost_report()`) as the closing number; tool links; contact. Close at 18:00 sharp. |

### Bonus block · Part 4 (take-home, or 17:30+ for fast rooms)

Assign as homework unless the room is flying. If you do demo it live, demo **§4.1 LangGraph only** — the rendered graph diagram next to Part 2's hand-rolled loop is a 90-second payoff. §4.2 (Deep Agents) and §4.3 (`debtbuster`) read better self-paced.

---

## Discussion prompts that reliably work

1. **"Why must the tests exist before the refactoring agent runs?"** (§1.1) — Because tests written *after* encode whatever the agent produced, including its bugs. The contract must predate the negotiation.
2. **"Would a code review catch `== np.nan`?"** (§1.5) — Almost never. It is a *semantic* bug in a line that reads correctly.
3. **"What sabotage slips past our seven tests?"** (§2.5) — Leads to: your gate's strength is exactly your test suite's strength.
4. **"Would you let this triage ranking drive sprint planning?"** (§3.3) — No consensus answer. The point is *where* the human checkpoint goes, and why there.
5. **"Why is the QA gate identical in all three framework versions?"** (§4.5) — Because verification is a property of the **task**, not of the framework.
6. **"What breaks when the agent picks its own tool arguments?"** (§4.2) — Use the bug recorded in the notebook: the first draft of `radon_report` had no path guard, the agent audited `/`, and one tool call returned **6.8 MB**. In Parts 1–3 *you* chose every argument, so it could not happen. Autonomy moves that choice to the model, and every tool then needs a bounded input **and** a bounded output.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `AuthenticationError` / 401 | key typo, or a `.env` with quotes/spaces | re-run §0.2; the loader strips quotes but not stray characters |
| `RateLimitError` / `insufficient_quota` | no billing on the account | hand them a backup key; do not debug billing live |
| `429` mid-run | tier-1 rate limits with 40 people on one key | stagger the room, or issue one key per table |
| Refactorer output has no code block | model returned prose | it is *already handled* — `extract_code_block` raises, the loop retries. Point at this as designed behaviour. |
| PyExamine "no report" | it writes to `pyexamine_report.txt`, doesn't print | read the file; the notebook already does |
| MLScent "no report" | writes to `output/analysis_report.txt` | same |
| `deepagents` import error | it needs the LangChain OpenAI binding | §4.2 installs `langchain-openai` in its own cell — run that cell |
| Empty reply from a `gpt-5.x` model | reasoning tokens consumed the budget | `llm()` already quadruples the budget for reasoning models; raise `max_new_tokens` if it recurs |
| Everything is slow | reasoning model in `.env` | set `MODEL_NAME = "gpt-4.1-mini"` in §0.3 for the live session |
| §4.2 deep agent runs for many minutes | autonomous agents plan, and reasoning models plan slowly | expected — it is a take-home section. On a reasoning model a single run can exceed 15 minutes. Demo §4.1 live instead. |

## If you are running short on time

Cut in this order:
1. Part 4 entirely (assign as take-home) — it is designed for that.
2. §3.5 bring-your-own-code (assign as take-home).
3. Exercise 2 (§2.6) — demo option C from the front instead.

**Never cut:** the sabotage demo (§2.5) or the ML Auditor discussion (§1.5). They carry the workshop's argument.
