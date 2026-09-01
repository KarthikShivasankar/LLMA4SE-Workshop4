"""The QA gate. Deliberately boring, deliberately LLM-free."""
import ast, pathlib, shutil, subprocess, sys, tempfile
from .tools import radon_avg_cc

def verify(original: str, candidate: str, test_file: str | None) -> dict:
    try:
        ast.parse(candidate)                                        # gate 1: syntax
    except SyntaxError as e:
        return {"ok": False, "why": f"gate 1 (syntax): {e}"}
    if test_file:                                                   # gate 2: behaviour
        with tempfile.TemporaryDirectory() as tmp:
            tgt = pathlib.Path(tmp, pathlib.Path(original).name)
            tgt.write_text(candidate)
            shutil.copy(test_file, tmp)
            r = subprocess.run([sys.executable, "-m", "pytest", "-q", pathlib.Path(test_file).name],
                               cwd=tmp, capture_output=True, text=True, timeout=180)
            if r.returncode != 0:
                return {"ok": False, "why": "gate 2 (behaviour): " + r.stdout[-300:]}
    with tempfile.TemporaryDirectory() as tmp:                      # gate 3: quality
        p = pathlib.Path(tmp, "cand.py"); p.write_text(candidate)
        before, after = radon_avg_cc(original), radon_avg_cc(str(p))
    if after > before:
        return {"ok": False, "why": f"gate 3 (quality): CC {before} -> {after}"}
    return {"ok": True, "why": f"gates passed - CC {before} -> {after}"}