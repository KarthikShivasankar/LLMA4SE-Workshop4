"""The LangGraph team: auditor -> refactorer <-> gates. Mirrors the notebook 1:1."""
import pathlib, re
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from . import config
from .brain import chat
from .gates import verify
from .tools import pyexamine

AUDITOR_SYS = ("You are a strict senior code reviewer. List the module's worst code "
               "smells as max 6 short bullets. Name function + problem. No fixes, no intro.")
REFACTORER_SYS = ("You are a careful refactoring engineer. Rewrite the module fixing the "
                  "listed smells. HARD INVARIANTS: same public API and behaviour; stdlib only; "
                  "named constants for magic numbers; remove duplication and dead code. "
                  "Reply with ONE ```python``` block with the FULL module, nothing else.")

class State(TypedDict):
    path: str
    test_file: str | None
    source: str
    findings: str
    candidate: str
    verdict: str
    accepted: bool
    iteration: int

def _extract(text: str) -> str:
    m = re.findall(r"```(?:python)?\s*(.*?)```", text, re.S)
    if not m:
        raise ValueError("no code block in reply")
    return m[-1].strip() + "\n"

def auditor(state: State) -> dict:
    evidence = pyexamine(str(pathlib.Path(state["path"]).parent))
    return {"findings": chat(AUDITOR_SYS,
                             f"STATIC EVIDENCE:\n{evidence}\n\nMODULE:\n{state['source']}")}

def refactorer(state: State) -> dict:
    fb = f"\nPREVIOUS ATTEMPT REJECTED: {state['verdict']}" if state["verdict"] else ""
    reply = chat(REFACTORER_SYS,
                 f"MODULE:\n```python\n{state['source']}\n```\nSMELLS:\n{state['findings']}{fb}")
    try:
        return {"candidate": _extract(reply), "iteration": state["iteration"] + 1}
    except ValueError as e:
        return {"candidate": "", "verdict": str(e), "iteration": state["iteration"] + 1}

def qa(state: State) -> dict:
    if not state["candidate"]:
        return {"accepted": False}
    v = verify(state["path"], state["candidate"], state["test_file"])
    return {"accepted": v["ok"], "verdict": v["why"]}

def _route(state: State) -> str:
    if state["accepted"]:
        return "done"
    return "give_up" if state["iteration"] >= config.MAX_ITERATIONS else "retry"

def build():
    g = StateGraph(State)
    g.add_node("auditor", auditor); g.add_node("refactorer", refactorer); g.add_node("qa", qa)
    g.add_edge(START, "auditor"); g.add_edge("auditor", "refactorer"); g.add_edge("refactorer", "qa")
    g.add_conditional_edges("qa", _route, {"done": END, "retry": "refactorer", "give_up": END})
    return g.compile()