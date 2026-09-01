"""debtbuster: audit | fix -- the whole UX in ~40 lines."""
import argparse, pathlib, sys
from .graph import build
from .tools import radon_avg_cc, pyexamine

def main() -> int:
    ap = argparse.ArgumentParser(prog="debtbuster",
                                 description="LLM-agent code auditing & gated refactoring")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("audit", help="static + agent audit of a file")
    a.add_argument("path")
    f = sub.add_parser("fix", help="run the auditor->refactorer<->QA team on a file")
    f.add_argument("path")
    f.add_argument("--tests", default=None, help="pytest file pinning behaviour (enables gate 2)")
    args = ap.parse_args()

    src = pathlib.Path(args.path).read_text()
    if args.cmd == "audit":
        print(f"avg cyclomatic complexity: {radon_avg_cc(args.path)}")
        print(pyexamine(str(pathlib.Path(args.path).parent))[:1500] or "(no PyExamine findings)")
        return 0

    team = build()
    out = team.invoke({"path": args.path, "test_file": args.tests, "source": src,
                       "findings": "", "candidate": "", "verdict": "",
                       "accepted": False, "iteration": 0})
    if out["accepted"]:
        dst = pathlib.Path(args.path).with_suffix(".refactored.py")
        dst.write_text(out["candidate"])
        print(f"ACCEPTED after {out['iteration']} iteration(s): {out['verdict']}\n-> {dst}")
        return 0
    print(f"REJECTED: {out['verdict'][:300]}\n(the gate held - nothing unverified shipped)")
    return 1

if __name__ == "__main__":
    sys.exit(main())