"""Deterministic eyes. No LLM in this file."""
import json, pathlib, subprocess, sys

_BIN = pathlib.Path(sys.executable).parent

def _exe(name: str) -> str:
    """Prefer the tool installed next to THIS interpreter, else trust PATH.

    Without this, `debtbuster` installed into a venv that is not on PATH cannot
    find its own dependencies -- the console script runs, radon does not.
    """
    candidate = _BIN / name
    return str(candidate) if candidate.exists() else name

def radon_avg_cc(path: str) -> float:
    out = subprocess.run([_exe("radon"), "cc", "-s", "-j", path],
                         capture_output=True, text=True).stdout
    data = json.loads(out or "{}")
    scores = [b["complexity"] for blocks in data.values() for b in blocks]
    return round(sum(scores) / len(scores), 2) if scores else 0.0

def pyexamine(path: str) -> str:
    subprocess.run([_exe("analyze_code_quality"), path, "--type", "code", "--output", "pyx"],
                   capture_output=True, text=True, timeout=600)
    rpt = pathlib.Path("pyx.txt")
    return rpt.read_text()[:3000] if rpt.exists() else ""