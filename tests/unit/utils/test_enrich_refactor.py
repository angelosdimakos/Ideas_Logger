# tests/unit/utils/test_enrich_refactor.py

from pathlib import Path
import subprocess
import tempfile
import json


def test_enrich_refactor_cli():
    """
    Tests the enrich_refactor CLI script by simulating an audit file and dummy lint reports,
    running the CLI, and verifying that the audit file is enriched with quality data for the target file.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        audit_path = tmpdir / "refactor_audit.json"
        report_dir = tmpdir / "lint-reports"
        report_dir.mkdir(parents=True, exist_ok=True)

        target_file = Path("Ideas_Logger/example.py").as_posix()

        # Minimal fake audit with normalized path
        audit_data = {target_file: {"complexity": {"dummy": 1}}}
        audit_path.write_text(json.dumps(audit_data), encoding="utf-8")

        # Dummy lint reports that mention the file (simulate output)
        for name in ["flake8.txt", "black.txt", "mypy.txt", "pydocstyle.txt"]:
            (report_dir / name).write_text(f"{target_file}:1:1: Dummy warning\n", encoding="utf-8")

        result = subprocess.run(
            [
                "python",
                "scripts/utils/enrich_refactor.py",
                "--audit",
                str(audit_path),
                "--reports",
                str(report_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert (
            result.returncode == 0
        ), f"CLI failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

        enriched = json.loads(audit_path.read_text(encoding="utf-8"))

        # Normalize path slashes and look for key
        matched_key = next(
            (k for k in enriched if k.replace("\\", "/").endswith("example.py")), None
        )
        assert matched_key, f"Could not find a matching key for 'example.py' in {enriched.keys()}"
        assert (
            "quality" in enriched[matched_key]
        ), f"Expected 'quality' key in enriched['{matched_key}'], got: {enriched[matched_key]}"
