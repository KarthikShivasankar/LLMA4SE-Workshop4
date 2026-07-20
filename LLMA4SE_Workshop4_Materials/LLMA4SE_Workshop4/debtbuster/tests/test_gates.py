"""The harness tests ITS OWN gates — the most load-bearing code gets the tests."""
from debtbuster.gates import verify

GOOD = "def f(x):\n    return x + 1\n"
BAD_SYNTAX = "def f(x:\n    return"

def test_gate1_rejects_broken_syntax(tmp_path):
    orig = tmp_path / "m.py"; orig.write_text(GOOD)
    v = verify(str(orig), BAD_SYNTAX, test_file=None)
    assert not v["ok"] and "gate 1" in v["why"]

def test_gates_accept_identical_code(tmp_path):
    orig = tmp_path / "m.py"; orig.write_text(GOOD)
    v = verify(str(orig), GOOD, test_file=None)
    assert v["ok"]

def test_gate3_rejects_complexity_regression(tmp_path):
    orig = tmp_path / "m.py"; orig.write_text(GOOD)
    worse = ("def f(x):\n"
             "    if x > 0:\n"
             "        if x > 1:\n"
             "            if x > 2:\n"
             "                return x\n"
             "    return x + 1\n")
    v = verify(str(orig), worse, test_file=None)
    assert not v["ok"] and "gate 3" in v["why"]
