"""
Module for testing complexity analysis functions.

This module contains unit tests for the `run_analysis` and `analyze_complexity` functions
from the `scripts.utils.complexity_summary` module. It verifies that these functions behave
as expected under various scenarios.
"""

import pytest
import sys
import json
import tempfile
from scripts.refactor.complexity.complexity_summary import run_analysis, analyze_complexity

# ────────────────────────────────
# 🧪 run_analysis() — Core Logic
# ────────────────────────────────


def test_run_analysis_no_violations(capfd) -> None:
    """
    Test case for `run_analysis` with no complexity violations.

    This test verifies that when the complexity of functions is below the threshold,
    no warnings are produced.
    """
    data = {
        "core.py": {
            "complexity": {"clean_function": {"complexity": 3}, "safe_function": {"complexity": 6}}
        }
    }
    run_analysis(data, max_complexity=10, use_emoji=False)
    out = capfd.readouterr().out
    assert "No complexity warnings." in out


def test_run_analysis_with_violations_plain(capfd) -> None:
    """
    Test case for `run_analysis` with complexity violations.

    This test verifies that when the complexity of a function exceeds the threshold,
    a SystemExit is raised and the appropriate warning message is output.
    """
    data = {
        "core.py": {
            "complexity": {
                "risky_function": {"complexity": 13},
            }
        }
    }
    with pytest.raises(SystemExit):
        run_analysis(data, max_complexity=10, use_emoji=False)
    out = capfd.readouterr().out
    assert "[COMPLEXITY WARNINGS]" in out
    assert "risky_function" in out


def test_run_analysis_with_violations_emoji(capfd) -> None:
    """
    Test case for `run_analysis` with complexity violations and emoji output.

    This test verifies that when the complexity of a function exceeds the threshold,
    a SystemExit is raised and the appropriate warning message with emoji is output.
    """
    data = {"core.py": {"complexity": {"bad": {"complexity": 15}}}}
    run_analysis(data, max_complexity=10, use_emoji=True)
    out = capfd.readouterr().out
    assert "🚨 Complexity Warnings" in out
    assert "bad" in out
    assert "⚠️" in out


# ────────────────────────────────
# 🧪 analyze_complexity() — Full CLI
# ────────────────────────────────


def test_analyze_complexity_valid_json(monkeypatch, capfd) -> None:
    """
    Test case for `analyze_complexity` with valid JSON input.

    This test verifies that the function processes valid JSON correctly and outputs
    the expected results.
    """
    content = {"file.py": {"complexity": {"foo": {"complexity": 4}}}}
    with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
        json.dump(content, tmp)
        tmp.flush()

        monkeypatch.setattr(sys, "argv", ["script", tmp.name])
        monkeypatch.setattr("sys.exit", lambda x: (_ for _ in ()).throw(SystemExit(x)))

        analyze_complexity(tmp.name)
        out = capfd.readouterr().out
        assert "🧠 Methods analyzed" in out or "Methods analyzed" in out


def test_analyze_complexity_missing_file(monkeypatch) -> None:
    """
    Test case for `analyze_complexity` when the input file is missing.

    This test verifies that the function handles missing files gracefully.
    """
    monkeypatch.setattr(sys, "exit", lambda code=1: (_ for _ in ()).throw(SystemExit(code)))
    with pytest.raises(SystemExit):
        analyze_complexity("nonexistent.json")


def test_analyze_complexity_empty_file(monkeypatch) -> None:
    """
    Test case for `analyze_complexity` with an empty input file.

    This test verifies that the function can handle empty files without errors.
    """
    with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
        tmp.write("  ")
        tmp.flush()

        monkeypatch.setattr(sys, "exit", lambda code=1: (_ for _ in ()).throw(SystemExit(code)))
        with pytest.raises(SystemExit):
            analyze_complexity(tmp.name)


def test_analyze_complexity_invalid_json(monkeypatch, capfd) -> None:
    """
    Test case for `analyze_complexity` with invalid JSON input.

    This test verifies that the function raises an appropriate error when the JSON is invalid.
    """
    with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
        tmp.write("{not: valid, json")
        tmp.flush()

        monkeypatch.setattr(sys, "exit", lambda code=1: (_ for _ in ()).throw(SystemExit(code)))
        with pytest.raises(SystemExit):
            analyze_complexity(tmp.name)

        out = capfd.readouterr().out
        assert "Invalid JSON" in out or "❌" in out


def test_analyze_complexity_error(monkeypatch) -> None:
    """
    Test case for `analyze_complexity` when an unexpected error occurs.

    This test verifies that the function handles unexpected errors gracefully.
    """
    # Simulate unexpected error (e.g. permission error)
    monkeypatch.setattr("os.path.exists", lambda _: True)
    monkeypatch.setattr("builtins.open", lambda *_: (_ for _ in ()).throw(Exception("Simulated")))
    monkeypatch.setattr(sys, "exit", lambda code=1: (_ for _ in ()).throw(SystemExit(code)))

    with pytest.raises(SystemExit):
        analyze_complexity("whatever.json")
