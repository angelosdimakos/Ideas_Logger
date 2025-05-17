import json
import subprocess
from pathlib import Path
import tempfile
import pytest

from scripts.refactor.lint_report_pkg.quality_checker import merge_into_refactor_guard


def test_merge_into_refactor_guard_unit(tmp_path):
    """
    Unit test that verifies quality data is added to a minimal audit file
    by calling the merge_into_refactor_guard function directly.
    """
    audit_path = tmp_path / "refactor_audit.json"
    reports_dir = tmp_path

    target_file = "example.py"
    audit_data = {target_file: {"complexity": {}}}
    audit_path.write_text(json.dumps(audit_data), encoding="utf-8")

    # Write dummy reports that will be detected and parsed
    (reports_dir / "flake8.txt").write_text(f"{target_file}:1:1: Dummy warning\n", encoding="utf-8")
    (reports_dir / "black.txt").write_text(f"{target_file}: reformatted\n", encoding="utf-8")
    (reports_dir / "mypy.txt").write_text(f"{target_file}: error: Dummy error\n", encoding="utf-8")
    (reports_dir / "pydocstyle.txt").write_text(f"{target_file}:1: D100: Missing docstring\n", encoding="utf-8")

    # Now run the enrichment process
    merge_into_refactor_guard(str(audit_path))

    enriched = json.loads(audit_path.read_text(encoding="utf-8"))
    matched_key = next((k for k in enriched if k.endswith("example.py")), None)
    assert matched_key, "Could not find 'example.py' in audit keys"
    assert "quality" in enriched[matched_key]
    assert isinstance(enriched[matched_key]["quality"], dict)
    assert any(enriched[matched_key]["quality"].values()), "No quality tool output merged"


@pytest.mark.slow
def test_enrich_refactor_cli_integration():
    """
    Integration test that calls the lint_report_pkg CLI via subprocess,
    simulating an audit file and dummy reports to verify full enrichment behavior.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        audit_path = tmpdir / "refactor_audit.json"

        target_file = Path("Ideas_Logger/example.py").as_posix()
        audit_data = {target_file: {"complexity": {"dummy": 1}}}
        audit_path.write_text(json.dumps(audit_data), encoding="utf-8")

        # Dummy lint reports that mention the file
        for name in ["flake8.txt", "black.txt", "mypy.txt", "pydocstyle.txt"]:
            (tmpdir / name).write_text(f"{target_file}:1:1: Dummy warning\n", encoding="utf-8")

        # Dynamically resolve the CLI script path
        project_root = Path(__file__).resolve().parents[4]
        cli_script = project_root / "scripts" / "refactor" / "lint_report_pkg" / "lint_report_cli.py"
        assert cli_script.exists(), f"CLI script not found at expected path: {cli_script}"

        result = subprocess.run(
            ["python", str(cli_script), "--audit", str(audit_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            f"CLI failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )

        enriched = json.loads(audit_path.read_text(encoding="utf-8"))
        matched_key = next(
            (k for k in enriched if k.replace("\\", "/").endswith("example.py")), None
        )

        assert matched_key, f"Could not find a matching key for 'example.py' in {enriched.keys()}"
        assert "quality" in enriched[matched_key], f"Expected 'quality' key in enriched['{matched_key}']"
