"""Deterministic eyes. No LLM in this file."""
import json, pathlib, subprocess

def radon_avg_cc(path: str) -> float:
    out = subprocess.run(["radon", "cc", "-s", "-j", path],
                         capture_output=True, text=True).stdout
    data = json.loads(out or "{}")
    scores = [b["complexity"] for blocks in data.values() for b in blocks]
    return round(sum(scores) / len(scores), 2) if scores else 0.0

def pyexamine(path: str) -> str:
    subprocess.run(["analyze_code_quality", path, "--type", "code", "--output", "pyx"],
                   capture_output=True, text=True, timeout=600)
    rpt = pathlib.Path("pyx.txt")
    return rpt.read_text()[:3000] if rpt.exists() else ""
