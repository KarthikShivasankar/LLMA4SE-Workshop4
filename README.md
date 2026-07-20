# Workshop 4 · Hands-on: Building Cooperative LLM Agent Workflows for Anti-pattern Detection, Code Smell and Technical Debt Resolution

**LLMA4SE 2026 — 2nd International Summer School on LLM-based Agents for Software Engineering**
Day 3 · Friday, September 11, 2026 · 15:00 – 18:00

Instructors: **Karthik Shivashankar** (SINTEF Digital / University of Oslo) & **Adela Nedisan Videsjorden** (University of Oslo)
Contact: karthik13sankar@outlook.com

---

## What's in this package

| File | What it is | Who it's for |
|---|---|---|
| `notebooks/Part1_The_Code_Auditor_Agent.ipynb` | Build one agent: static-analysis tools (radon, pylint, PyExamine, **MLScent**) + a local 1.5B LLM. Includes the **ML Auditor** hands-on. | Students, 15:00–16:00 |
| `notebooks/Part2_The_Refactoring_Team.ipynb` | Auditor → Refactorer → QA Verifier with a shared-state blackboard, verification gates, and the failure-pattern lab (incl. a sabotage demo). | Students, 16:05–17:15 |
| `notebooks/Part3_Technical_Debt_Pipeline.ipynb` | TD classifier + triage agents, the full capstone pipeline, a Markdown debt report (with an MLScent section), bring-your-own-code. | Students, 17:20–18:00 |
| `notebooks/Part4_Production_Frameworks.ipynb` | **Bonus / take-home:** Ollama model server, the team rebuilt in LangGraph, an autonomous Deep Agent, and `debtbuster` — a lean, pip-installable CLI harness. | Students, self-paced |
| `LLMA4SE_Workshop4_Slides.pptx` | 18 interactive lecture slides interleaved with the notebooks. | Instructors (projected) |
| `instructor_guide.md` | Minute-by-minute run of show, talking points, discussion prompts, Colab troubleshooting. | Instructors |
| `student_handout.md` | Concepts, glossary, exercise list, references — for students to keep. | Students (print or share) |
| `requirements.txt` | Pinned dependency list (the notebooks self-install on Colab; this is for local runs / reference). | Anyone running locally |

## Requirements (students)

- A Google account and **free** Google Colab. No API keys, no paid tiers, no local installs.
- Everything runs on a free **T4 GPU** with a local **Qwen2.5-Coder-1.5B-Instruct** model (~3 GB, fp16).

## How to run a notebook on Colab

1. Go to [colab.research.google.com](https://colab.research.google.com) → **File → Upload notebook** → pick the `.ipynb`.
   (Or upload the notebooks to Drive/GitHub and open from there.)
2. **Runtime → Change runtime type → T4 GPU → Save.**
3. Run cells top to bottom. The first cells install packages (~2 min) and download the model (~2 min).

Each notebook is **standalone**: its setup section recreates all files and reloads the model, so a student who joins late or loses a runtime can start any part fresh.

## Suggested run order (matches the slides)

1. Slides 1–7 (intro, smells & debt, agent anatomy) → **Notebook Part 1**
2. Slides 9–13 (team workflow, gates, failure patterns) → **Notebook Part 2**
3. Slides 14–15 (debt classification & triage) → **Notebook Part 3**
4. Slides 16–17 (bonus track) → **Notebook Part 4** (take-home if time runs out) → Slide 18 (wrap-up)

## Part 4 in one paragraph (bonus track)

Parts 1–3 build every pattern by hand so nothing is magic. Part 4 rebuilds the *same* pipeline with the production stack: **Ollama** serves a 4-bit `qwen2.5-coder:7b` locally on the T4 (a stronger brain than Parts 1–3, one server for all agents); **LangGraph** re-expresses the Auditor → Refactorer ⇄ QA loop as a typed `StateGraph` with conditional edges; **Deep Agents** (`deepagents`) adds autonomous planning (`write_todos`), file tools and sub-agents with real tool-calling; and everything is packaged as **`debtbuster`** — a lean coding harness (5 source files + config + its own pytest suite) installed with `pip install -e .` and driven by a CLI (`debtbuster audit <file>` / `debtbuster fix <file> --tests <tests>`) that exits non-zero when the QA gate rejects, so it drops straight into CI. The QA gates are byte-for-byte the same as Part 2 — the whole point.

## The two "patients" students operate on

- `inventory.py` — a working-but-smelly business module (mutable default arg, 7-param function, magic numbers, duplication, dead code) pinned by 7 behaviour tests.
- `ml_project/train_model.py` — an ML training script with silent ML-specific smells (`== np.nan`, missing `optimizer.zero_grad()`, no seeds, no early stopping) detected by **MLScent** (76 detectors, CAIN 2025).

## Research tools featured

- **PyExamine** — MSR 2025 · `pip install code-quality-analyzer` · [github.com/KarthikShivasankar/python_smells_detector](https://github.com/KarthikShivasankar/python_smells_detector)
- **MLScent** — CAIN 2025 · `pip install git+https://github.com/KarthikShivasankar/ml_smells_detector.git` · [arXiv:2502.18466](https://arxiv.org/abs/2502.18466)
- **BEACon-TD / TD-Suite** — JSS 2025 · [github.com/KarthikShivasankar/text_classification](https://github.com/KarthikShivasankar/text_classification)
