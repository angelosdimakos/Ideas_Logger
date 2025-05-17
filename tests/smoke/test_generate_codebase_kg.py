# tests/test_generate_codebase_kg.py
import sys
import json
import pytest

import scripts.kg.generate_codebase_kg as generate_codebase_kg

class DummyAnalyzer:
    def __init__(self, json_path, focus):
        # record what was passed in
        self.json_path = json_path
        self.focus = focus
        self.analyze_called = False
        self.visualize_called = False
        self.export_called = False

    def analyze(self):
        self.analyze_called = True
        # return a dummy graph and a report dict
        return ("<graph-obj>", {"complexity_score": 42.0})

    def visualize(self, graph, density_report):
        assert graph == "<graph-obj>"
        assert density_report["complexity_score"] == 42.0
        self.visualize_called = True

    def export_graph(self, graph, fmt):
        assert graph == "<graph-obj>"
        assert fmt in ("graphml", "gexf")
        self.export_called = True
        return f"out.{fmt}"

@pytest.fixture(autouse=True)
def stub_analyzer(monkeypatch):
    """
    Replace the real CodebaseAnalyzer with our DummyAnalyzer for all tests.
    """
    monkeypatch.setattr(
        generate_codebase_kg,
        "CodebaseAnalyzer",
        DummyAnalyzer
    )
    yield

def run_script(args, tmp_path, capsys):
    """
    Helper to invoke generate_codebase_kg.main() with sys.argv = args,
    using a temporary JSON file at tmp_path / "summary.json".
    """
    # prepare a minimal JSON file
    summary = {}
    json_file = tmp_path / "summary.json"
    json_file.write_text(json.dumps(summary))

    # patch sys.argv
    old_argv = sys.argv
    sys.argv = ["generate_codebase_kg.py", "--json", str(json_file)] + args

    try:
        # run the main entrypoint
        generate_codebase_kg.main()
    finally:
        sys.argv = old_argv

    return capsys.readouterr()

def test_main_without_export(tmp_path, capsys):
    # Run with default focus and no --export
    out = run_script([], tmp_path, capsys)
    # Should print complexity score only once
    assert "Complexity Score for scripts/refactor/: 42.00" in out.out
    # No export line
    assert "Graph exported as" not in out.out

def test_main_with_export(tmp_path, capsys):
    # Run with --export gexf
    out = run_script(["--export", "gexf"], tmp_path, capsys)
    assert "Complexity Score for scripts/refactor/: 42.00" in out.out
    # Should mention export
    assert "Graph exported as gexf file: out.gexf" in out.out

def test_custom_focus(tmp_path, capsys):
    # Run with a custom focus prefix
    custom_focus = "my/pkg/"
    out = run_script(["--focus", custom_focus], tmp_path, capsys)
    # DummyAnalyzer stored the focus; sniff it via printed output
    # (we know the default focus appears in the printed text)
    assert f"Complexity Score for {custom_focus}: 42.00" in out.out
