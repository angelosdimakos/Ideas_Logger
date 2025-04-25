import json
from scripts.refactor.complexity.complexity_summary import analyze_complexity


def test_generate_complexity_summary(tmp_path):
    """
    Unit tests for the analyze_complexity function, verifying summary output and warning detection
    for various audit JSON scenarios, including normal, empty, and multiple violation cases.
    """
    fake_data = {
        "scripts/foo.py": {
            "complexity": {"method1": {"complexity": 4}, "method2": {"complexity": 11}}
        },
        "scripts/bar.py": {
            "complexity": {
                "methodA": {"complexity": 6},
            }
        },
    }
    fake_path = tmp_path / "refactor_audit.json"
    fake_path.write_text(json.dumps(fake_data), encoding="utf-8")

    from io import StringIO
    import sys

    out = StringIO()
    sys.stdout = out
    try:
        analyze_complexity(str(fake_path))
    finally:
        sys.stdout = sys.__stdout__

    output = out.getvalue()
    assert "📊 Summary:" in output
    assert "🧠 Methods analyzed:" in output
    assert "🔧 Files analyzed:" in output
    assert "method2" in output
    assert "scripts/foo.py" in output
    assert "Complexity Warnings" in output


def test_empty_complexity_data(tmp_path):
    """
    Unit tests for the analyze_complexity function, ensuring correct summary output and warning detection
    for various audit JSON scenarios, including normal data, empty files, multiple violations,
    and empty complexity dictionaries.
    """
    fake_data = {"scripts/empty.py": {"no_complexity_here": True}}
    path = tmp_path / "refactor_audit.json"
    path.write_text(json.dumps(fake_data), encoding="utf-8")

    from io import StringIO
    import sys

    out = StringIO()
    sys.stdout = out
    try:
        analyze_complexity(str(path))
    finally:
        sys.stdout = sys.__stdout__

    output = out.getvalue()
    assert "📊 Summary:" in output
    assert "Methods analyzed: 0" in output
    assert "Files analyzed: 1" in output


def test_multiple_violations_summary(tmp_path):
    """
    Unit tests for the analyze_complexity function, verifying correct summary output,
    warning detection, and handling of various audit JSON scenarios including normal data,
    empty files, multiple violations, and empty complexity dictionaries.
    """
    fake_data = {
        "scripts/alpha.py": {
            "complexity": {
                "one": {"complexity": 15},
                "two": {"complexity": 20},
            }
        },
        "scripts/beta.py": {"complexity": {"ok": {"complexity": 3}}},
    }
    path = tmp_path / "refactor_audit.json"
    path.write_text(json.dumps(fake_data), encoding="utf-8")

    from io import StringIO
    import sys

    out = StringIO()
    sys.stdout = out
    try:
        analyze_complexity(str(path))
    finally:
        sys.stdout = sys.__stdout__

    output = out.getvalue()
    assert "one" in output
    assert "two" in output
    assert "scripts/alpha.py" in output
    assert "Complexity Warnings (2)" in output


def test_empty_complexity_dict(tmp_path):
    """
    Unit tests for the analyze_complexity function, covering
    summary output and warning detection for various audit JSON scenarios,
    including normal data, empty files, multiple violations, and empty complexity dictionaries.
    """
    fake_data = {"scripts/nothing.py": {"complexity": {}}}
    path = tmp_path / "refactor_audit.json"
    path.write_text(json.dumps(fake_data), encoding="utf-8")

    from io import StringIO
    import sys

    out = StringIO()
    sys.stdout = out
    try:
        analyze_complexity(str(path))
    finally:
        sys.stdout = sys.__stdout__

    output = out.getvalue()
    assert "Methods analyzed: 0" in output
    assert "Files analyzed: 1" in output
    assert "Complexity Warnings" not in output
