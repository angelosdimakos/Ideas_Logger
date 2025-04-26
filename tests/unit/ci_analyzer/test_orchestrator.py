from unittest.mock import patch
from scripts.ci_analyzer import orchestrator
import argparse


@patch("scripts.ci_analyzer.orchestrator.shutil.copy2")
@patch("scripts.ci_analyzer.orchestrator.Path.exists", return_value=True)
@patch("scripts.ci_analyzer.orchestrator.Path.mkdir")
def test_backup_audit_file_creates_backup(mock_mkdir, mock_exists, mock_copy):
    orchestrator.backup_audit_file("mock_audit.json")
    mock_copy.assert_called_once()
    mock_mkdir.assert_called_once()


def test_header_block_contains_sections():
    header = orchestrator.header_block()
    assert "CI Audit Summary" in header
    assert "Emoji Risk Indicators" in header


@patch("scripts.ci_analyzer.orchestrator.generate_overview_insights", return_value=["## Overview"])
@patch("scripts.ci_analyzer.orchestrator.generate_prime_insights", return_value=["## Prime"])
@patch(
    "scripts.ci_analyzer.orchestrator.generate_complexity_insights", return_value=["## Complexity"]
)
@patch("scripts.ci_analyzer.orchestrator.generate_testing_insights", return_value=["## Testing"])
@patch("scripts.ci_analyzer.orchestrator.generate_quality_insights", return_value=["## Quality"])
@patch("scripts.ci_analyzer.orchestrator.generate_diff_insights", return_value=["## Diff"])
def test_generate_ci_summary_aggregates_all_parts(*_):
    dummy_audit = {}
    markdown = orchestrator.generate_ci_summary(dummy_audit)
    assert "## Overview" in markdown
    assert "## Diff" in markdown


def test_save_summary_writes_file(tmp_path):
    out_file = tmp_path / "summary.md"
    orchestrator.save_summary("# Summary", str(out_file))
    assert out_file.exists()
    assert "# Summary" in out_file.read_text()


@patch("scripts.ci_analyzer.orchestrator.load_audit")
@patch("scripts.ci_analyzer.orchestrator.save_summary")
@patch("scripts.ci_analyzer.orchestrator.generate_ci_summary", return_value="# Dummy Summary")
@patch("argparse.ArgumentParser.parse_args")
def test_main_runs_all(mock_args, mock_summary, mock_save, mock_load):
    mock_args.return_value = argparse.Namespace(audit="dummy.json", output="out.md")
    orchestrator.main()
    mock_load.assert_called_once()
    mock_summary.assert_called_once()
    mock_save.assert_called_once()
