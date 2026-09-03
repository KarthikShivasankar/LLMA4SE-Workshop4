"""Regression tests for the OpenRouter + openai-client workshop runtime."""
from __future__ import annotations

import json
import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import workshop_lib as wl  # noqa: E402


def test_extract_json_empty_and_object_become_list():
    assert wl.extract_json("") == []
    assert wl.extract_json("   ") == []
    assert wl.extract_json("no json here") == []
    assert wl.extract_json("{}") == []
    assert wl.extract_json('{"findings": []}') == []


def test_extract_json_findings_wrapper_and_bare_list():
    wrapped = '{"findings": [{"smell": "god class", "location": "timed.py"}]}'
    assert wl.extract_json(wrapped)[0]["smell"] == "god class"
    bare = 'Here you go:\n[{"smell": "magic number"}]\n'
    assert wl.extract_json(bare)[0]["smell"] == "magic number"


def test_record_usage_none_is_safe():
    meter = {"calls": 0, "in": 0, "out": 0}
    wl.record_usage(None, meter)
    assert meter == {"calls": 0, "in": 0, "out": 0}
    wl.record_usage(SimpleNamespace(prompt_tokens=11, completion_tokens=3), meter)
    assert meter["in"] == 11 and meter["out"] == 3


def test_llm_survives_usage_none_and_empty_content():
    resp = SimpleNamespace(
        usage=None,
        choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))],
    )
    client = MagicMock()
    client.chat.completions.create.return_value = resp
    assert wl.llm("hi", client=client, model="openai/gpt-4o-mini") == "ok"

    empty = SimpleNamespace(usage=None, choices=[])
    client.chat.completions.create.return_value = empty
    assert wl.llm("hi", client=client, model="openai/gpt-4o-mini") == ""


def test_llm_retries_without_json_mode_on_error():
    good = SimpleNamespace(
        usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
        choices=[SimpleNamespace(message=SimpleNamespace(content='{"a":1}'))],
    )
    client = MagicMock()
    client.chat.completions.create.side_effect = [RuntimeError("no json_object"), good]
    text = wl.llm("x", json_mode=True, client=client, model="openai/gpt-4o-mini")
    assert text == '{"a":1}'
    second_kwargs = client.chat.completions.create.call_args_list[1].kwargs
    assert "response_format" not in second_kwargs


def test_snap_label_empty_does_not_indexerror():
    labels = ["design", "code", "test"]
    assert wl.snap_label("", labels) == "code"
    assert wl.snap_label("design please", labels) == "design"
    assert wl.snap_label("architecture-debt", labels) == "code"


def test_load_credentials_prefers_os_environ(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    assert wl.load_credentials() == "sk-or-test"


def test_dotenv_paths_works_without_dunder_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("OPENROUTER_API_KEY=x\n", encoding="utf-8")
    paths = wl.dotenv_paths()
    assert any(p.resolve() == (tmp_path / ".env").resolve() for p in paths)


def test_load_dotenv_reads_parent_env_without_overwriting(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("OPENROUTER_API_KEY=from-file\nLLM_MODEL=openai/gpt-4o-mini\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.setattr(wl, "dotenv_paths", lambda: [env])
    wl.load_dotenv()
    assert os.environ["OPENROUTER_API_KEY"] == "from-file"
    assert os.environ["LLM_MODEL"] == "openai/gpt-4o-mini"


def test_is_reasoning_detects_slug_not_hardcoded_true():
    assert wl.is_reasoning_model("openai/gpt-4o-mini") is False
    assert wl.is_reasoning_model("openai/o3") is True
    assert wl.is_reasoning_model("nvidia/nemotron-3-ultra-550b-a55b:free") is False


def test_make_client_uses_openrouter_base_url(monkeypatch):
    pytest.importorskip("openai")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    client = wl.make_client()
    assert "openrouter.ai" in str(client.base_url)


def test_resolve_patient_tests_prefers_nested_2_2_0_layout(tmp_path):
    nested = tmp_path / "tests" / "test_itsdangerous" / "test_timed.py"
    nested.parent.mkdir(parents=True)
    nested.write_text("# nested\n", encoding="utf-8")
    (tmp_path / "tests" / "test_timed.py").write_text("# flat\n", encoding="utf-8")
    assert wl.resolve_patient_tests(tmp_path) == nested


def test_qa_sandbox_writes_source_basename_not_inventory(tmp_path):
    pytest.importorskip("radon")
    """The gate must overlay the real module name (e.g. timed.py), not inventory.py."""
    sys.path.insert(0, os.path.join(ROOT, "debtbuster", "src"))
    from debtbuster.gates import verify

    src = tmp_path / "timed.py"
    src.write_text("def sign(x):\n    return x\n", encoding="utf-8")
    tests = tmp_path / "test_timed.py"
    tests.write_text(
        "from timed import sign\n\ndef test_sign():\n    assert sign(1) == 1\n",
        encoding="utf-8",
    )
    v = verify(str(src), "def sign(x):\n    return x\n", test_file=str(tests))
    assert v["ok"]
