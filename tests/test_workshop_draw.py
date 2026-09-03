from workshop_draw import SCENES, scene_to_svg, scene_names, show, mermaid_ink_url


def test_all_scenes_render_svg():
    assert "pipeline" in scene_names()
    for name in scene_names():
        svg = scene_to_svg(SCENES[name])
        assert svg.startswith("<svg")
        assert "</svg>" in svg
        assert "<rect" in svg or "<text" in svg


def test_pipeline_svg_has_the_loop():
    svg = scene_to_svg(SCENES["pipeline"])
    assert "Auditor" in svg
    assert "Refactorer" in svg
    assert "QA" in svg


def test_new_part_scenes_exist():
    needed = {
        "tokens", "patients", "tools", "contract", "blackboard", "sandbox",
        "sabotage", "classify", "fullpipe", "langgraph", "deep", "debtpkg",
    }
    assert needed <= set(scene_names())


def test_mermaid_ink_url_is_safe_and_encodes_graph():
    url = mermaid_ink_url("flowchart LR\n  A --> B")
    assert url.startswith("https://mermaid.ink/svg/")
    assert " " not in url


def test_show_unknown_scene_raises():
    try:
        show("not-a-scene")
        raise AssertionError("expected KeyError")
    except KeyError as e:
        assert "pipeline" in str(e)
