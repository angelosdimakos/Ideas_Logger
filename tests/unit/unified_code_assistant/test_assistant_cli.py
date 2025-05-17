# tests/unit/ai/unified_code_assistant/test_assistant_cli.py
import tempfile
import json
from scripts.unified_code_assistant.assistant_cli import main
import sys
from unittest import mock
import pytest
from types import SimpleNamespace

@pytest.fixture(autouse=True)
def patch_mock_config(monkeypatch):
    mock_config = SimpleNamespace(
        persona="test",
        prompts_by_subcategory={"_default": "Summarize the function briefly."}
    )
    monkeypatch.setattr("scripts.config.config_manager.ConfigManager.load_config", lambda: mock_config)



def make_temp_report(data):
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8")
    json.dump(data, f)
    f.close()
    return f.name


def test_analyze_mode_prints_output(capsys):
    data = {
        "example.py": {
            "mypy": {"errors": []},
            "lint": {"issues": []},
            "complexity": {"functions": []},
            "coverage": {
                "complexity": {
                    "foo": {"complexity": 4}
                }
            }
        }
    }
    path = make_temp_report(data)
    test_args = ["prog", path, "--mode", "analyze"]
    with mock.patch.object(sys, 'argv', test_args):
        main()
    out, err = capsys.readouterr()
    assert "example.py" in out


def test_strategic_mode_prints_summary(capsys):
    data = {
        "mod.py": {
            "mypy": {"errors": ["x"]},
            "lint": {"issues": []},
            "complexity": {"functions": []},
            "coverage": {
                "complexity": {
                    "thing": {"complexity": 9}
                }
            }
        }
    }
    path = make_temp_report(data)
    test_args = ["prog", path, "--mode", "strategic"]
    with mock.patch.object(sys, 'argv', test_args):
        main()
    out, _ = capsys.readouterr()
    assert "Mock summary" in out


def test_summaries_mode_outputs_module(capsys):
    data = {
        "utils.py": {
            "docstrings": {
                "functions": [{"name": "parse", "docstring": "Parse things"}]
            },
            "mypy": {}, "lint": {}, "complexity": {},
            "coverage": {"complexity": {"f": {"complexity": 2}}}
        }
    }
    path = make_temp_report(data)
    test_args = ["prog", path, "--mode", "summaries"]
    with mock.patch.object(sys, 'argv', test_args):
        main()
    out, _ = capsys.readouterr()
    assert "## utils.py" in out
