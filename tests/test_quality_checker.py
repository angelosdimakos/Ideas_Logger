import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

import scripts.refactor.quality_checker as qc


@pytest.fixture
def dummy_result():
    mock_result = MagicMock()
    mock_result.stdout = "some output\n"
    mock_result.returncode = 0
    return mock_result


def test_run_command_writes_output(tmp_path, dummy_result):
    file = tmp_path / "out.txt"
    with patch("subprocess.run", return_value=dummy_result):
        ret = qc.run_command(["echo", "test"], str(file))
    assert file.read_text() == "some output"
    assert ret == 0


@patch("scripts.refactor.quality_checker.run_command")
def test_run_black(mock_run):
    qc.run_black()
    mock_run.assert_called_once_with(["black", "--check", "scripts"], qc.BLACK_REPORT)


@patch("scripts.refactor.quality_checker.run_command")
def test_run_flake8(mock_run):
    qc.run_flake8()
    mock_run.assert_called_once_with(["flake8", "--format=json", "scripts"], qc.FLAKE8_REPORT)


@patch("scripts.refactor.quality_checker.run_command")
def test_run_mypy(mock_run):
    qc.run_mypy()
    mock_run.assert_called_once_with(
        ["mypy", "--strict", "--no-color-output", "scripts"], qc.MYPY_REPORT
    )


@patch("scripts.refactor.quality_checker.Path.exists", return_value=False)
def test_merge_skips_if_audit_missing(mock_exists, capsys):
    qc.merge_into_refactor_guard("missing_audit.json")
    captured = capsys.readouterr()
    assert "Missing refactor audit JSON!" in captured.out


@patch("scripts.refactor.quality_checker.Path.read_text")
@patch("scripts.refactor.quality_checker.Path.exists", side_effect=lambda: True)
def test_merge_flake8_only(mock_exists, mock_read_text, tmp_path):
    audit_path = tmp_path / "audit.json"
    audit_path.write_text(json.dumps({"existing.py": {}}))

    flake_report = {"scripts/file1.py": [{"code": "E501", "message": "Line too long"}]}
    with patch("builtins.open", mock_open(read_data=json.dumps(flake_report))):
        qc.merge_into_refactor_guard(str(audit_path))

    result = json.loads(audit_path.read_text())
    assert "flake8" in result["scripts/file1.py"]


@patch("scripts.refactor.quality_checker.Path.read_text")
@patch("scripts.refactor.quality_checker.Path.exists", side_effect=lambda: True)
def test_merge_black_and_mypy(mock_exists, mock_read_text, tmp_path):
    audit_path = tmp_path / "audit.json"
    audit_path.write_text(json.dumps({}))

    def fake_read_text():
        return "would reformat scripts/file2.py\nscripts/file3.py: error: Something's wrong"

    mock_read_text.side_effect = [
        json.dumps({}),  # empty flake8
        fake_read_text(),  # black.txt
        fake_read_text(),  # mypy.txt
    ]

    with patch("builtins.open", mock_open(read_data="{}")):
        qc.merge_into_refactor_guard(str(audit_path))

    data = json.loads(audit_path.read_text())
    assert "file2.py" in next(iter(data))
    assert any("mypy" in v for v in data.values())
