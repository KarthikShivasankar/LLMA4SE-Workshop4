"""Shared OpenRouter + openai-client helpers for Workshop 4.

The notebook imports this module so Colab and local Jupyter share one brain.
Students never paste a key into a cell: credentials come from os.environ, a
.env file (this folder or parents), Colab Secrets, or a hidden prompt.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
from typing import Any

OPENROUTER_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openai/gpt-4o-mini"
USAGE: dict[str, int] = {"calls": 0, "in": 0, "out": 0}

_CLIENT = None


def dotenv_paths() -> list[pathlib.Path]:
    """Places a student might put OPENROUTER_API_KEY / LLM_MODEL.

    Works when this file is imported *and* when the same source is exec'd
    inside a notebook cell (no ``__file__``). Walks a few parents so a
    ``.env`` next to the repo or in Colab ``/content`` is still found after
    ``os.chdir(WORKDIR)``.
    """
    paths = [pathlib.Path("/content/.env")]
    cur = pathlib.Path.cwd().resolve()
    for _ in range(5):
        paths.append(cur / ".env")
        if cur.parent == cur:
            break
        cur = cur.parent
    try:
        here = pathlib.Path(__file__).resolve().parent
        paths.append(here / ".env")
        paths.append(here.parent / ".env")
    except NameError:
        pass
    seen: set[pathlib.Path] = set()
    out: list[pathlib.Path] = []
    for p in paths:
        try:
            p = p.resolve()
        except OSError:
            continue
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def load_dotenv() -> None:
    for candidate in dotenv_paths():
        if not candidate.is_file():
            continue
        for line in candidate.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            os.environ.setdefault(name.strip(), value.strip().strip("'\""))


def load_credentials() -> str:
    """os.environ / .env first, then Colab Secrets, then getpass."""
    load_dotenv()
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"]

    try:
        from google.colab import userdata  # type: ignore
        for name in ("OPENROUTER_API_KEY", "LLM_MODEL"):
            try:
                val = userdata.get(name)
                if val:
                    os.environ[name] = str(val).strip()
            except Exception:
                pass
        if os.environ.get("OPENROUTER_API_KEY"):
            return os.environ["OPENROUTER_API_KEY"]
    except Exception:
        pass

    import getpass
    key = getpass.getpass("OpenRouter API key (hidden): ").strip()
    os.environ["OPENROUTER_API_KEY"] = key
    return key


def model_name() -> str:
    load_dotenv()
    return os.environ.get("LLM_MODEL") or DEFAULT_MODEL


def is_reasoning_model(name: str | None = None) -> bool:
    n = (name or model_name()).lower()
    needles = ("o1", "o3", "o4", "gpt-5", "reasoner", ":thinking", "thinking")
    return any(tok in n for tok in needles)


def record_usage(usage: Any, meter: dict[str, int] | None = None) -> None:
    """OpenRouter often returns usage=None — never dereference blindly."""
    meter = meter if meter is not None else USAGE
    if usage is None:
        return
    meter["in"] += int(getattr(usage, "prompt_tokens", 0) or 0)
    meter["out"] += int(getattr(usage, "completion_tokens", 0) or 0)


def extract_json(text: str) -> list:
    """Always a list. Empty / {} / prose without JSON → []."""
    if not text or not str(text).strip():
        return []
    m = re.search(r"\[.*\]|\{.*\}", str(text), re.DOTALL)
    if not m:
        return []
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        findings = data.get("findings", data)
        if isinstance(findings, list):
            return [x for x in findings if isinstance(x, dict)]
        if isinstance(findings, dict) and findings.get("smell"):
            return [findings]
    return []


def snap_label(reply: str, labels: list[str], default: str = "code") -> str:
    if not reply or not str(reply).strip():
        return default
    token = str(reply).lower().strip().split()[0].strip(".,:;")
    return token if token in labels else default


def make_client(api_key: str | None = None):
    from openai import OpenAI
    key = api_key or os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set. Run load_credentials() first.")
    return OpenAI(
        base_url=os.environ.get("OPENROUTER_BASE_URL", OPENROUTER_URL),
        api_key=key,
        default_headers={
            "HTTP-Referer": "https://github.com/KarthikShivasankar/LLMA4SE-Workshop4",
            "X-Title": "LLMA4SE Workshop 4",
        },
    )


def get_client():
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = make_client()
    return _CLIENT


def reset_client() -> None:
    global _CLIENT
    _CLIENT = None


def _reply_text(resp: Any) -> str:
    choices = getattr(resp, "choices", None) or []
    if not choices:
        return ""
    msg = choices[0].message
    content = getattr(msg, "content", None)
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text") or "")
            elif hasattr(block, "text"):
                parts.append(block.text or "")
        return "".join(parts).strip()
    return (content or "").strip()


def llm(
    user_prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    max_new_tokens: int = 1024,
    temperature: float = 0.2,
    json_mode: bool = False,
    client=None,
    model: str | None = None,
) -> str:
    """One OpenRouter chat completion via the official openai client."""
    cli = client or get_client()
    name = model or model_name()
    kwargs: dict[str, Any] = {
        "model": name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    if is_reasoning_model(name):
        kwargs["max_completion_tokens"] = max(max_new_tokens * 4, 4000)
    else:
        kwargs["max_tokens"] = max_new_tokens
        kwargs["temperature"] = temperature
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        resp = cli.chat.completions.create(**kwargs)
    except Exception:
        kwargs.pop("temperature", None)
        kwargs.pop("response_format", None)
        if "max_tokens" in kwargs:
            kwargs["max_completion_tokens"] = max(int(kwargs.pop("max_tokens")) * 4, 4000)
        resp = cli.chat.completions.create(**kwargs)

    USAGE["calls"] += 1
    record_usage(getattr(resp, "usage", None))
    return _reply_text(resp)


def cost_report(meter: dict[str, int] | None = None) -> None:
    m = meter if meter is not None else USAGE
    print(f"📊 {m['calls']} calls · {m['in']:,} in / {m['out']:,} out tokens")


def resolve_patient_tests(itsd: str | pathlib.Path) -> pathlib.Path:
    """itsdangerous 2.2.0 nests tests; older trees used a flat test_timed.py."""
    itsd = pathlib.Path(itsd)
    for rel in (
        ("tests", "test_itsdangerous", "test_timed.py"),
        ("tests", "test_timed.py"),
    ):
        cand = itsd.joinpath(*rel)
        if cand.is_file():
            return cand
    raise FileNotFoundError(f"no test_timed.py under {itsd / 'tests'}")


def fetch_patients(root: str | pathlib.Path | None = None) -> dict[str, str]:
    """Clone pinned real GitHub trees used as workshop patients."""
    import subprocess
    import sys

    root = pathlib.Path(root or "patients").resolve()
    root.mkdir(parents=True, exist_ok=True)

    itsd = root / "itsdangerous"
    if not (itsd / ".git").exists():
        # Full single-branch clone: annotated tag 2.2.0 + --depth 1 can yield an empty tree.
        subprocess.run(
            ["git", "clone", "--branch", "2.2.0", "--single-branch",
             "https://github.com/pallets/itsdangerous.git", str(itsd)],
            check=True,
        )
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "-e", str(itsd), "freezegun"],
        check=True,
    )

    examples = root / "pytorch-examples"
    if not (examples / ".git").exists():
        subprocess.run(
            ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
             "https://github.com/pytorch/examples.git", str(examples)],
            check=True,
        )
        subprocess.run(["git", "-C", str(examples), "sparse-checkout", "set", "mnist"], check=True)

    patient_py = itsd / "src" / "itsdangerous" / "timed.py"
    patient_tests = resolve_patient_tests(itsd)
    ml_dir = examples / "mnist"
    if not patient_py.is_file():
        raise FileNotFoundError(f"missing {patient_py}")
    if not ml_dir.is_dir():
        raise FileNotFoundError(f"missing {ml_dir}")
    return {
        "PATIENT_PY": str(patient_py),
        "PATIENT_TESTS": str(patient_tests),
        "ML_PATIENT_DIR": str(ml_dir),
        "ITSD_ROOT": str(itsd),
    }


def openrouter_chat_model():
    """LangChain wrapper for Deep Agents only — still OpenRouter, same key."""
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=model_name(),
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url=os.environ.get("OPENROUTER_BASE_URL", OPENROUTER_URL),
    )
