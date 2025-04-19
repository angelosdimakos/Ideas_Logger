# tests/unit/utils/test_enrich_refactor.py
import json
import subprocess
import shutil
from pathlib import Path


def test_enrich_refactor_cli(tmp_path):
    # Setup: Copy CLI script into tmp test directory
    project_root = Path(__file__).resolve().parent.parent.parent
    source_script = project_root / "scripts" / "utils" / "enrich_refactor.py"
    test_script = tmp_path / "enrich_refactor.py"
    shutil.copy(source_script, test_script)

    # Create minimal fake audit file
    audit_path = tmp_path / "refactor_audit.json"
    audit_path.write_text(json.dumps({
        "refactor/example.py": {"complexity": {}}
    }, indent=2))

    # Create dummy lint reports directory
    reports_dir = tmp_path / "lint-reports"
    reports_dir.mkdir()
    (reports_dir / "black.txt").write_text("would reformat scripts/refactor/example.py")
    (reports_dir / "flake8.txt").write_text("scripts/refactor/example.py:10:1: E302 expected 2 blank lines")
    (reports_dir / "mypy.txt").write_text("scripts/refactor/example.py:12: error: Incompatible return value")
    (reports_dir / "pydocstyle.txt").write_text("scripts/refactor/example.py:1 in public module")

    # Create dummy coverage.xml
    (tmp_path / "coverage.xml").write_text("""
    <coverage>
      <packages>
        <package name="scripts.refactor">
          <classes>
            <class name="example" filename="scripts/refactor/example.py" line-rate="0.8"/>
          </classes>
        </package>
      </packages>
    </coverage>
    """)

    # Run CLI enrichment
    result = subprocess.run(
        [
            "python", str(test_script),
            "--audit", str(audit_path),
            "--reports", str(reports_dir)
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    enriched = json.loads(audit_path.read_text())
    quality = enriched["refactor/example.py"]["quality"]

    assert "black" in quality
    assert "flake8" in quality
    assert "mypy" in quality
    assert "pydocstyle" in quality
    assert "coverage" in quality
