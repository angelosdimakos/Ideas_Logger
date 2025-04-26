from unittest.mock import patch
from scripts.ci_analyzer import ci_trends
import argparse


def test_load_audit_reads_valid_file(tmp_path):
    dummy = tmp_path / "audit.json"
    dummy.write_text('{"score": 10}')
    result = ci_trends.load_audit(dummy)
    assert result == {"score": 10}


def test_extract_metrics_returns_dict():
    dummy_data = {"complexity": {"func": {"score": 5}}}
    result = ci_trends.extract_metrics(dummy_data)  # ✅ pass just 1 arg
    assert isinstance(result, dict)


def test_compare_metrics_detects_diff():
    previous = {"score": 5}
    current = {"score": 7}
    delta = ci_trends.compare_metrics(current, previous)  # ✅ correct order
    assert delta["score"] == 2


def test_print_comparison_shows_signs(capsys):
    current = {"tests": 10, "risky": 5}
    delta = {"tests": 3, "risky": -2}
    ci_trends.print_comparison(current, delta)
    captured = capsys.readouterr()
    assert "🔺" in captured.out
    assert "🔻" in captured.out


@patch("scripts.ci_analyzer.ci_trends.load_audit")
@patch("scripts.ci_analyzer.ci_trends.load_previous_metrics")
@patch("scripts.ci_analyzer.ci_trends.save_metrics")
@patch(
    "argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(audit="mock_path.json")
)
def test_main_runs_end_to_end(mock_args, mock_save, mock_prev, mock_load):
    mock_load.return_value = {
        "some_file.py": {
            "complexity": {"func_a": {"score": 5, "coverage": 0, "cyclomatic": 11}},
            "missing_tests": ["func_a"],
        }
    }
    mock_prev.return_value = {"files": 1, "methods": 1, "missing_tests": 0, "risky": 0}
    ci_trends.main()
    mock_save.assert_called_once()


def test_save_metrics_creates_file(tmp_path):
    metrics = {"tests": 42}
    output_file = tmp_path / "metrics.json"
    ci_trends.save_metrics(metrics, output_file)
    assert output_file.exists()
    assert '"tests": 42' in output_file.read_text()


def test_load_previous_metrics_handles_missing(tmp_path):
    result = ci_trends.load_previous_metrics(tmp_path / "not_found.json")
    assert result == {}
