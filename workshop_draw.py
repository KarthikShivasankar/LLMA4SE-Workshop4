"""Excalidraw scenes for the workshop — diagrams instead of lecture text.

`show("pipeline")` renders an interactive Excalidraw canvas (official editor via
CDN). If the iframe is blocked, the same scene is drawn as SVG underneath.
`sketch()` opens a blank board for discuss prompts.
"""
from __future__ import annotations

import html
import json
import uuid
from typing import Any

# Compact scene language → official Excalidraw element dicts.
# Colours match the Excalidraw default palette.


def _id() -> str:
    return uuid.uuid4().hex[:12]


def _base(**kw: Any) -> dict:
    el = {
        "id": _id(),
        "x": 0,
        "y": 0,
        "width": 0,
        "height": 0,
        "angle": 0,
        "strokeColor": "#1e1e1e",
        "backgroundColor": "transparent",
        "fillStyle": "hachure",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": {"type": 3},
        "seed": abs(hash(str(kw))) % 10_000_000,
        "version": 1,
        "versionNonce": 1,
        "isDeleted": False,
        "boundElements": None,
        "updated": 1,
        "link": None,
        "locked": False,
    }
    el.update(kw)
    return el


def box(x, y, w, h, text, fill="#a5d8ff", color="#1e1e1e") -> list[dict]:
    rid = _id()
    tid = _id()
    lines = text.split("\n")
    size = 14 if len(lines) > 2 else 16
    line_h = size + 5
    block_h = line_h * len(lines)
    ty = y + max((h - block_h) / 2, 8)
    rect = _base(
        id=rid, type="rectangle", x=x, y=y, width=w, height=h,
        backgroundColor=fill, strokeColor=color,
        boundElements=[{"id": tid, "type": "text"}],
    )
    label = _base(
        id=tid, type="text", x=x + 8, y=ty, width=w - 16, height=block_h,
        text=text, originalText=text, fontSize=size, fontFamily=1,
        textAlign="center", verticalAlign="middle", baseline=size,
        containerId=rid, backgroundColor="transparent", roundness=None,
        strokeColor=color, lineHeight=1.25,
    )
    return [rect, label]


def caption(x, y, text, size=18, color="#1e1e1e") -> dict:
    return _base(
        type="text", x=x, y=y, width=max(24 * len(text) // 2, 80), height=size + 8,
        text=text, originalText=text, fontSize=size, fontFamily=1,
        textAlign="left", verticalAlign="top", baseline=size,
        backgroundColor="transparent", roundness=None, strokeColor=color,
        lineHeight=1.25,
    )


def arrow(x1, y1, x2, y2, label="") -> list[dict]:
    aid = _id()
    els = [_base(
        id=aid, type="arrow", x=x1, y=y1,
        width=x2 - x1, height=y2 - y1,
        points=[[0, 0], [x2 - x1, y2 - y1]],
        lastArrowhead="arrow", startArrowhead=None,
        roundness={"type": 2},
    )]
    if label:
        els.append(caption((x1 + x2) / 2 - 20, (y1 + y2) / 2 - 22, label, size=14, color="#868e96"))
    return els


def scene(name: str, elements: list[dict], w=920, h=360) -> dict:
    return {
        "name": name,
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "viewBackgroundColor": "#fffef6",
            "gridSize": None,
            "width": w,
            "height": h,
        },
        "files": {},
    }


def _flat(parts: list) -> list[dict]:
    out: list[dict] = []
    for p in parts:
        if isinstance(p, list):
            out.extend(p)
        else:
            out.append(p)
    return out


SCENES: dict[str, dict] = {
    "map": scene("map", _flat([
        caption(24, 16, "Today — six agents, one loop", 22),
        box(24, 70, 150, 70, "0  key + llm", "#fff3bf"),
        box(200, 70, 150, 70, "1  auditor", "#a5d8ff"),
        box(376, 70, 150, 70, "2  refactor", "#b2f2bb"),
        box(552, 70, 150, 70, "3  triage", "#ffd8a8"),
        box(728, 70, 150, 70, "4  ship CLI", "#eebefa"),
        *arrow(174, 105, 200, 105),
        *arrow(350, 105, 376, 105),
        *arrow(526, 105, 552, 105),
        *arrow(702, 105, 728, 105),
        caption(24, 170, "tools measure   ·   LLM interprets   ·   a gate decides", 16, "#495057"),
        caption(24, 210, "Fall behind? skip the exercise, run the Part's last cell.", 14, "#868e96"),
    ]), h=280),
    "keys": scene("keys", _flat([
        caption(24, 16, "Where the key lives — never in a code cell", 20),
        box(40, 80, 200, 80, "1  os.environ / .env", "#b2f2bb"),
        box(300, 80, 200, 80, "2  Colab Secrets", "#a5d8ff"),
        box(560, 80, 200, 80, "3  hidden prompt", "#ffd8a8"),
        *arrow(240, 120, 300, 120),
        *arrow(500, 120, 560, 120),
        caption(40, 190, "First hit wins. Copied into os.environ so !debtbuster inherits it.", 15, "#495057"),
        caption(40, 230, "LLM_MODEL = any OpenRouter slug   e.g. openai/gpt-4o-mini", 15, "#868e96"),
    ]), h=300),
    "brain": scene("brain", _flat([
        caption(24, 16, "One client. OpenRouter underneath.", 20),
        box(40, 80, 220, 90, "your notebook\nllm() / debtbuster", "#fff3bf"),
        box(340, 80, 240, 90, "openai.OpenAI\nbase_url = openrouter", "#a5d8ff"),
        box(660, 80, 200, 90, "any model slug", "#b2f2bb"),
        *arrow(260, 125, 340, 125),
        *arrow(580, 125, 660, 125),
        caption(40, 200, "usage=None is normal. We ignore it. Never userdata.get() here.", 15, "#495057"),
    ]), h=280),
    "agent": scene("agent", _flat([
        caption(24, 16, "An agent is four things", 22),
        box(40, 80, 180, 90, "ROLE\nsystem prompt", "#fff3bf"),
        box(260, 80, 180, 90, "BRAIN\nllm()", "#a5d8ff"),
        box(480, 80, 180, 90, "TOOLS\nradon · pylint", "#b2f2bb"),
        box(700, 80, 180, 90, "CONTRACT\nJSON / code", "#ffd8a8"),
        caption(40, 200, "Change role + tools, keep the skeleton → ML Auditor in one cell.", 16, "#495057"),
    ]), h=280),
    "measure": scene("measure", _flat([
        caption(24, 16, "Why tools exist", 22),
        box(60, 80, 280, 110, "ask the model\nfor complexity\n→ guesses, off by 1", "#ffc9c9"),
        box(480, 80, 280, 110, "radon counts\nLLM explains\n→ you can gate on it", "#b2f2bb"),
        *arrow(340, 135, 480, 135, "don't"),
        caption(60, 220, "A metric you cannot trust to ±1 is a metric you cannot gate on.", 15, "#495057"),
    ]), h=300),
    "pipeline": scene("pipeline", _flat([
        caption(24, 16, "The team — reject loops back with the reason", 20),
        box(40, 90, 170, 80, "Auditor", "#a5d8ff"),
        box(300, 90, 170, 80, "Refactorer", "#fff3bf"),
        box(560, 90, 170, 80, "QA  (no LLM)", "#b2f2bb"),
        box(780, 90, 120, 80, "ship", "#eebefa"),
        *arrow(210, 130, 300, 130, "findings"),
        *arrow(470, 130, 560, 130, "patch"),
        *arrow(730, 130, 780, 130, "ok"),
        *arrow(645, 90, 385, 90, "reject + why"),
    ]), h=260),
    "gates": scene("gates", _flat([
        caption(24, 16, "Three gates. Cheapest first. No model inside.", 20),
        box(40, 80, 240, 90, "1  ast.parse\nµs  ·  broken syntax", "#a5d8ff"),
        box(320, 80, 260, 90, "2  pytest (upstream)\n~1s  ·  behaviour", "#fff3bf"),
        box(620, 80, 260, 90, "3  radon Δ CC\n~1s  ·  got worse?", "#ffd8a8"),
        caption(40, 200, "Fox cannot audit the henhouse. Sabotage: invert max_age — tests must die.", 15, "#495057"),
    ]), h=280),
    "quadrant": scene("quadrant", _flat([
        caption(24, 16, "priority = interest  ÷  principal", 22),
        box(80, 70, 300, 100, "HIGH interest\nLOW principal\n→ do these first", "#b2f2bb"),
        box(420, 70, 300, 100, "HIGH interest\nHIGH principal\n→ plan a sprint", "#ffd8a8"),
        box(80, 190, 300, 100, "LOW interest\nLOW principal\n→ later", "#e9ecef"),
        box(420, 190, 300, 100, "LOW interest\nHIGH principal\n→ don't", "#ffc9c9"),
    ]), h=330),
    "stack": scene("stack", _flat([
        caption(24, 16, "Same gates. Three wrappers.", 22),
        box(40, 80, 240, 100, "hand-rolled\nrun_workflow()", "#fff3bf"),
        box(320, 80, 240, 100, "LangGraph\ntyped state", "#a5d8ff"),
        box(600, 80, 260, 100, "debtbuster CLI\nexit 0 / 1", "#b2f2bb"),
        caption(40, 210, "Verification is a property of the task, not of the framework.", 16, "#495057"),
    ]), h=280),
    "tokens": scene("tokens", _flat([
        caption(24, 16, "What you send ≠ what you pay", 22),
        box(40, 80, 260, 100, "chars in the file\n(easy to count)", "#e9ecef"),
        box(360, 80, 260, 100, "tokens in / out\n(model's units)", "#a5d8ff"),
        box(680, 80, 200, 100, "usage=None\njust ignore", "#fff3bf"),
        *arrow(300, 130, 360, 130),
        caption(40, 210, "Reasoning slugs need max_completion_tokens. Chat slugs use max_tokens + temperature.", 15, "#495057"),
    ]), h=280),
    "patients": scene("patients", _flat([
        caption(24, 16, "Two real GitHub patients — pinned, not toys", 20),
        box(40, 80, 400, 120, "pallets/itsdangerous@2.2.0\ntimed.py + nested tests\nTimestampSigner public API", "#a5d8ff"),
        box(500, 80, 380, 120, "pytorch/examples  mnist/\nreal training loop\nMLScent's home turf", "#ffd8a8"),
        caption(40, 220, "QA copies the itsdangerous package tree and overlays timed.py so imports still work.", 15, "#495057"),
    ]), h=290),
    "tools": scene("tools", _flat([
        caption(24, 16, "Deterministic eyes — no LLM in these boxes", 20),
        box(24, 80, 200, 100, "radon\nMcCabe CC", "#a5d8ff"),
        box(248, 80, 200, 100, "pylint\nlints as JSON", "#fff3bf"),
        box(472, 80, 200, 100, "PyExamine\nquality report", "#b2f2bb"),
        box(696, 80, 200, 100, "MLScent\nML smells", "#ffd8a8"),
        caption(24, 210, "Wire any of these into Agent.tools. The model only reads the dump.", 15, "#495057"),
    ]), h=280),
    "contract": scene("contract", _flat([
        caption(24, 16, "extract_json — always a list, never a crash", 20),
        box(40, 80, 200, 90, "prose / empty", "#ffc9c9"),
        box(280, 80, 200, 90, "{ }  object", "#fff3bf"),
        box(520, 80, 200, 90, "{findings:[…]}", "#a5d8ff"),
        box(760, 80, 140, 90, "[…]", "#b2f2bb"),
        *arrow(240, 125, 280, 125),
        *arrow(480, 125, 520, 125),
        *arrow(720, 125, 760, 125),
        caption(40, 200, "All four become list[dict]. {} and missing JSON → []. Part 2 can still start.", 15, "#495057"),
    ]), h=270),
    "blackboard": scene("blackboard", _flat([
        caption(24, 16, "One dataclass everyone reads and writes", 20),
        box(40, 70, 200, 80, "original_code\nfindings", "#a5d8ff"),
        box(280, 70, 200, 80, "candidate_code", "#fff3bf"),
        box(520, 70, 200, 80, "verdict\nsyntax/tests/CC", "#b2f2bb"),
        box(760, 70, 140, 80, "history", "#eebefa"),
        caption(40, 180, "Agents never pass secret side-channels. If it is not on the board, it did not happen.", 15, "#495057"),
        caption(40, 215, "record() prints a timeline — that log is the demo, not a slide.", 14, "#868e96"),
    ]), h=280),
    "sandbox": scene("sandbox", _flat([
        caption(24, 16, "Gate 2 sandbox — overlay, don't invent a filename", 18),
        box(40, 70, 260, 110, "src/itsdangerous/\n  __init__.py\n  timed.py   ← overlay", "#a5d8ff"),
        box(360, 70, 240, 110, "temp dir\nPYTHONPATH=tmp\npytest test_timed.py", "#fff3bf"),
        box(660, 70, 220, 110, "import itsdangerous\nstill works", "#b2f2bb"),
        *arrow(300, 125, 360, 125),
        *arrow(600, 125, 660, 125),
        caption(40, 205, "Writing inventory.py here would make the suite import the untouched original. That's a false pass.", 14, "#495057"),
    ]), h=270),
    "sabotage": scene("sabotage", _flat([
        caption(24, 16, "One flipped operator. Tests must die.", 22),
        box(60, 80, 360, 110, "healthy\nif age > max_age:\n    raise BadTimeSignature", "#b2f2bb"),
        box(500, 80, 360, 110, "sabotage\nif age < max_age:\n    raise BadTimeSignature", "#ffc9c9"),
        *arrow(420, 135, 500, 135, "invert"),
        caption(60, 220, "Looks like a refactor. Behaviour is wrong. Gate 2 is the only honest witness.", 15, "#495057"),
    ]), h=290),
    "classify": scene("classify", _flat([
        caption(24, 16, "Closed label set + snap_label", 22),
        box(40, 80, 280, 100, "model reply\n'documentation debt'", "#fff3bf"),
        box(380, 80, 240, 100, "first token\n.lower().strip()", "#a5d8ff"),
        box(680, 80, 200, 100, "in LABELS?\nelse → code", "#b2f2bb"),
        *arrow(320, 130, 380, 130),
        *arrow(620, 130, 680, 130),
        caption(40, 210, "Empty reply → 'code'. Never split()[0] on ''.", 15, "#495057"),
    ]), h=270),
    "fullpipe": scene("fullpipe", _flat([
        caption(24, 16, "One report from four jobs", 22),
        box(24, 80, 190, 90, "1 classify\n8 labels", "#fff3bf"),
        box(246, 80, 190, 90, "2 triage\nI ÷ P", "#ffd8a8"),
        box(468, 80, 190, 90, "3 audit\n+ refactor", "#a5d8ff"),
        box(690, 80, 190, 90, "4 write\nTECH_DEBT_REPORT", "#b2f2bb"),
        *arrow(214, 125, 246, 125),
        *arrow(436, 125, 468, 125),
        *arrow(658, 125, 690, 125),
        caption(24, 200, "Backlog is real GitHub issues. Code patient is still timed.py + upstream tests.", 15, "#495057"),
    ]), h=270),
    "langgraph": scene("langgraph", _flat([
        caption(24, 16, "LangGraph = the same team, typed", 20),
        box(40, 80, 160, 80, "START", "#e9ecef"),
        box(240, 80, 160, 80, "auditor", "#a5d8ff"),
        box(440, 80, 160, 80, "refactorer", "#fff3bf"),
        box(640, 80, 160, 80, "qa", "#b2f2bb"),
        *arrow(200, 120, 240, 120),
        *arrow(400, 120, 440, 120),
        *arrow(600, 120, 640, 120),
        *arrow(720, 80, 520, 80, "retry"),
        caption(40, 190, "Conditional edge: accepted → END, else retry until MAX_ITERATIONS, then give_up.", 15, "#495057"),
    ]), h=260),
    "deep": scene("deep", _flat([
        caption(24, 16, "Deep Agents still talks to OpenRouter", 20),
        box(40, 80, 240, 100, "create_deep_agent\nwants a LangChain model", "#fff3bf"),
        box(340, 80, 280, 100, "ChatOpenAI\nbase_url = openrouter\nsame key", "#a5d8ff"),
        box(680, 80, 200, 100, "NOT\nopenai:{slug}", "#ffc9c9"),
        *arrow(280, 130, 340, 130),
        caption(40, 210, "openai:{slug} looks up OPENAI_API_KEY and api.openai.com. We never do that.", 15, "#495057"),
    ]), h=280),
    "debtpkg": scene("debtpkg", _flat([
        caption(24, 16, "pip install -e ./debtbuster  — this folder, this brain", 18),
        box(40, 70, 200, 90, "brain.py\nOpenRouter client", "#fff3bf"),
        box(260, 70, 200, 90, "config.py\nLLM_MODEL", "#a5d8ff"),
        box(480, 70, 200, 90, "gates.py\nno LLM", "#b2f2bb"),
        box(700, 70, 180, 90, "cli.py\nexit 0 / 1", "#eebefa"),
        caption(40, 185, "graph.py wires auditor → refactorer ↔ qa. Same loop you just built by hand.", 15, "#495057"),
        caption(40, 220, "Do not pip install the public GitHub package here — it still expects OPENAI_API_KEY.", 14, "#868e96"),
    ]), h=280),
}


def scene_to_svg(data: dict, width: int | None = None, height: int | None = None) -> str:
    """Always-on fallback so Colab still shows the picture if the iframe is blocked."""
    app = data.get("appState") or {}
    width = width or int(app.get("width") or 920)
    height = height or int(app.get("height") or 320)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="100%" style="max-width:{width}px;background:#fffef6;border:1px solid #e9ecef;'
        f'border-radius:12px;font-family:Virgil,Segoe UI,sans-serif">'
    ]
    for el in data.get("elements") or []:
        t = el.get("type")
        if t == "rectangle":
            parts.append(
                f'<rect x="{el["x"]}" y="{el["y"]}" width="{el["width"]}" height="{el["height"]}" '
                f'rx="10" fill="{el.get("backgroundColor", "#fff")}" stroke="{el.get("strokeColor", "#111")}" '
                f'stroke-width="2"/>'
            )
        elif t == "text":
            text = html.escape(el.get("text") or "")
            lines = text.split("\n")
            size = int(el.get("fontSize") or 16)
            x = el["x"] + (el.get("width") or 0) / 2
            y = el["y"] + size
            anchor = "middle" if el.get("textAlign") == "center" else "start"
            if anchor == "start":
                x = el["x"]
            for i, line in enumerate(lines):
                parts.append(
                    f'<text x="{x}" y="{y + i * (size + 4)}" text-anchor="{anchor}" '
                    f'font-size="{size}" fill="{el.get("strokeColor", "#111")}">{line}</text>'
                )
        elif t == "arrow":
            x, y = el["x"], el["y"]
            pts = el.get("points") or [[0, 0], [80, 0]]
            x2, y2 = x + pts[-1][0], y + pts[-1][1]
            mid = (x + x2) / 2
            wobble = y - 8 if abs(y2 - y) < 4 else (y + y2) / 2
            parts.append(
                f'<path d="M {x} {y} Q {mid} {wobble} {x2} {y2}" fill="none" '
                f'stroke="#1e1e1e" stroke-width="2" marker-end="url(#arr)"/>'
            )
    parts.insert(1, (
        '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#1e1e1e"/></marker></defs>'
    ))
    parts.append("</svg>")
    return "".join(parts)


def _editor_html(data: dict, height: int) -> str:
    payload = json.dumps(data)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<style>html,body,#root{{margin:0;height:100%;background:#fffef6}}</style>
</head><body>
<div id="root"></div>
<script type="module">
try {{
  const React = (await import("https://esm.sh/react@18.2.0")).default;
  const {{ createRoot }} = await import("https://esm.sh/react-dom@18.2.0/client");
  const {{ Excalidraw }} = await import("https://esm.sh/@excalidraw/excalidraw@0.17.6");
  const scene = {payload};
  createRoot(document.getElementById("root")).render(
    React.createElement(Excalidraw, {{
      initialData: scene,
      UIOptions: {{ canvasActions: {{ loadScene: false, export: true, saveToActiveFile: false }} }},
    }})
  );
}} catch (e) {{
  document.body.innerHTML = "<p style='font:14px sans-serif;padding:12px;color:#868e96'>Excalidraw CDN blocked — SVG below is the same scene.</p>";
}}
</script>
</body></html>"""


def show(name: str, height: int = 380):
    """Render a named scene in the notebook (Excalidraw + SVG fallback)."""
    import base64
    if name not in SCENES:
        raise KeyError(f"unknown scene {name!r}. Try: {', '.join(scene_names())}")
    data = SCENES[name]
    h = int((data.get("appState") or {}).get("height") or height)
    svg = scene_to_svg(data)
    try:
        from IPython.display import HTML, display
    except ImportError:
        print(svg)
        return svg
    b64 = base64.b64encode(_editor_html(data, h).encode("utf-8")).decode("ascii")
    display(HTML(
        f"<div style='margin:8px 0 4px;font:600 14px/1.3 Segoe UI,sans-serif;color:#1e1e1e'>"
        f"Excalidraw · {html.escape(name)} — pan, zoom, doodle</div>"
        f"<iframe src='data:text/html;base64,{b64}' style='width:100%;height:{h + 40}px;border:1px solid #dee2e6;"
        f"border-radius:12px;background:#fffef6'></iframe>"
        f"<details style='margin-top:6px'><summary style='cursor:pointer;color:#868e96;font:13px sans-serif'>"
        f"Static copy (always works)</summary>{svg}</details>"
    ))
    return name


def sketch(prompt: str = "Sketch with your neighbour — 90 seconds.", height: int = 420):
    """Blank Excalidraw board for discuss / predict beats."""
    blank = scene("scratch", [caption(24, 16, prompt, 18, "#868e96")], h=height)
    return show_scene(blank, height)


def show_scene(data: dict, height: int = 380):
    name = data.get("name") or "scene"
    SCENES["_tmp"] = data
    try:
        return show("_tmp", height=height)
    finally:
        SCENES.pop("_tmp", None)


def scene_names() -> list[str]:
    return [k for k in SCENES if not k.startswith("_")]


def mermaid_ink_url(diagram: str) -> str:
    """Static SVG URL (works when the mermaid JS CDN is blocked)."""
    import base64
    payload = base64.urlsafe_b64encode(diagram.strip().encode("utf-8")).decode("ascii")
    return f"https://mermaid.ink/svg/{payload}"


def mermaid(diagram: str, height: int = 360):
    """Render a mermaid flowchart in Colab / local Jupyter.

    Uses mermaid.ink as an image (always works with network) and a live
    mermaid.js pass when the CDN is allowed.
    """
    url = mermaid_ink_url(diagram)
    src = diagram.strip()
    try:
        from IPython.display import HTML, display
    except ImportError:
        print(url)
        return url
    safe = html.escape(src)
    uid = _id()
    display(HTML(
        f"<div style='margin:8px 0 4px;font:600 14px/1.3 Segoe UI,sans-serif;color:#1e1e1e'>"
        f"Mermaid — flowchart</div>"
        f"<div class='mermaid' id='mmd-{uid}' style='background:#fffef6;border:1px solid #e9ecef;"
        f"border-radius:12px;padding:12px'>{safe}</div>"
        f"<img src='{html.escape(url)}' alt='mermaid' style='max-width:100%;margin-top:8px;"
        f"background:#fffef6;border:1px solid #e9ecef;border-radius:12px'/>"
        f"<script type='module'>"
        f"try {{ const m = await import('https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs');"
        f" m.default.initialize({{startOnLoad:false, theme:'neutral'}});"
        f" await m.default.run({{querySelector:'#mmd-{uid}'}}); }} catch (e) {{}}"
        f"</script>"
    ))
    return url
