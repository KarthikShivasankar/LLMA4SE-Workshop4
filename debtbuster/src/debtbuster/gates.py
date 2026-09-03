"""The QA gate. Deliberately boring, deliberately LLM-free."""
import ast, os, pathlib, shutil, subprocess, sys, tempfile
from .tools import radon_avg_cc


def _run_tests(original: str, candidate: str, test_file: str) -> dict:
    src = pathlib.Path(original)
    pkg = src.parent
    tpath = pathlib.Path(test_file).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        packaged = (pkg / "__init__.py").is_file()
        if packaged:
            sandbox = tmp / pkg.name
            shutil.copytree(pkg, sandbox)
            (sandbox / src.name).write_text(candidate, encoding="utf-8")
            pythonpath = [str(tmp)]
        else:
            (tmp / src.name).write_text(candidate, encoding="utf-8")
            pythonpath = [str(tmp)]

        if tpath.parent.name == "test_itsdangerous":
            pythonpath.append(str(tpath.parent.parent))
            cwd = str(tpath.parents[2])
            target = str(tpath)
        else:
            shutil.copy(tpath, tmp / tpath.name)
            cwd = str(tmp)
            target = tpath.name

        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(pythonpath + [env.get("PYTHONPATH", "")])
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", target],
            cwd=cwd, capture_output=True, text=True, timeout=180, env=env,
        )
        if r.returncode != 0:
            return {"ok": False, "why": "gate 2 (behaviour): " + (r.stdout or r.stderr)[-300:]}
    return {"ok": True, "why": ""}


def verify(original: str, candidate: str, test_file: str | None) -> dict:
    try:
        ast.parse(candidate)
    except SyntaxError as e:
        return {"ok": False, "why": f"gate 1 (syntax): {e}"}
    if test_file:
        out = _run_tests(original, candidate, test_file)
        if not out["ok"]:
            return out
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp, "cand.py"); p.write_text(candidate)
        before, after = radon_avg_cc(original), radon_avg_cc(str(p))
    if after > before:
        return {"ok": False, "why": f"gate 3 (quality): CC {before} -> {after}"}
    return {"ok": True, "why": f"gates passed - CC {before} -> {after}"}
