import os
import shutil
import subprocess
from pathlib import Path
import json


def find_project_root(marker: str = "scripts") -> Path:
    """Climb up until a directory containing `marker` is found (used as root)."""
    cur = Path(__file__).resolve()
    while cur != cur.parent:
        if (cur / marker).is_dir():
            return cur
        cur = cur.parent
    raise RuntimeError(f"Could not find project root with marker '{marker}'")


def test_enrich_refactor_cli(tmp_path):
    # 🔍 Discover and copy enrich CLI into test space
    project_root = find_project_root()
    source_script = project_root / "scripts" / "utils" / "enrich_refactor.py"
    test_script = tmp_path / "enrich_refactor.py"
    shutil.copy(source_script, test_script)

    # 🧪 Simulate all expected report files
    reports_dir = tmp_path / "lint-reports"
    reports_dir.mkdir()
    (reports_dir / "black.txt").write_text("would reformat scripts/refactor/example.py")
    (reports_dir / "flake8.txt").write_text("scripts/refactor/example.py:10:5: E303 too many blank lines")
    (reports_dir / "mypy.txt").write_text("scripts/refactor/example.py:12: error: Incompatible return value type")
    (reports_dir / "pydocstyle.txt").write_text("scripts/refactor/example.py:1 in public module")

    (tmp_path / "coverage.xml").write_text("""
        <coverage>
          <packages>
            <package name="scripts.refactor">
              <classes>
                <class name="example" filename="scripts/refactor/example.py" line-rate="0.75"/>
              </classes>
            </package>
          </packages>
        </coverage>
    """)

    # 📝 Minimal audit
    audit_path = tmp_path / "refactor_audit.json"
    audit_path.write_text(json.dumps({"refactor/example.py": {}}))

    # 🧪 Run with correct PYTHONPATH and working directory
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root / "scripts")

    result = subprocess.run(
        ["python", str(test_script), "--audit", str(audit_path.name), "--reports", str(reports_dir.name)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True
    )

    # ✅ Check result
    assert result.returncode == 0, f"CLI failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    enriched = json.loads(audit_path.read_text())
    assert isinstance(enriched, dict)
    assert enriched, "Audit file is empty after CLI execution"

    key = next(iter(enriched))
    assert "quality" in enriched[key]
    for section in ["flake8", "black", "mypy", "pydocstyle", "coverage"]:
        assert section in enriched[key]["quality"], f"Missing {section} quality data"
