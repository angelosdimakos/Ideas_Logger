import pytest
import json
from pathlib import Path
from scripts.utils.complexity_summary import analyze_complexity

def test_generate_complexity_summary(tmp_path):
    # Create a fake audit JSON
    fake_data = {
        "scripts/foo.py": {
            "complexity": {
                "method1": {"complexity": 4},    # Below threshold
                "method2": {"complexity": 11}    # Above threshold
            }
        },
        "scripts/bar.py": {
            "complexity": {
                "methodA": {"complexity": 6},
            }
        }
    }
    fake_path = tmp_path / "refactor_audit.json"
    fake_path.write_text(json.dumps(fake_data), encoding="utf-8")

    # Capture stdout
    from io import StringIO
    import sys
    out = StringIO()
    sys.stdout = out

    try:
        analyze_complexity(str(fake_path))
    finally:
        sys.stdout = sys.__stdout__

    output = out.getvalue()

    # Only method2 will be flagged
    assert "📊 Summary:" in output
    assert "🧠 Methods analyzed:" in output
    assert "🔧 Files analyzed:" in output
    assert "method2" in output
    assert "scripts/foo.py" in output
    assert "Complexity Warnings" in output
