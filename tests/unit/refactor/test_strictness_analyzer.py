import json
from pathlib import Path
import pytest
from scripts.refactor.strictness_analyzer import (
    load_test_report,
    load_audit_report,
    generate_module_report,
    StrictnessReport
)

# -------------------- Fixtures --------------------

@pytest.fixture
def test_report_path(tmp_path):
    test_data = {
        "tests": [
            {
                "name": "test_paths_config",
                "file": "tests/unit/test_paths.py",
                "start": 9,
                "end": 32,
                "asserts": 0,
                "mocks": 1,
                "raises": 0,
                "branches": 1,
                "length": 24,
                "strictness_score": 0.03
            },
            {
                "name": "test_paths_in_test_mode",
                "file": "tests/unit/test_paths.py",
                "start": 35,
                "end": 48,
                "asserts": 4,
                "mocks": 1,
                "raises": 0,
                "branches": 1,
                "length": 14,
                "strictness_score": 0.49
            }
        ],
        "imports": {
            "test_paths": ["paths"]
        }
    }
    path = tmp_path / "test_report.json"
    path.write_text(json.dumps(test_data), encoding="utf-8")
    return path


@pytest.fixture
def audit_report_path(tmp_path):
    audit_data = {
        "paths.py": {
            "complexity": {
                "ZephyrusPaths._resolve_path": {
                    "complexity": 1,
                    "coverage": 1.0,
                    "hits": 10,
                    "lines": 5,
                    "covered_lines": [1, 2, 3, 4, 5],
                    "missing_lines": []
                }
            }
        }
    }
    path = tmp_path / "refactor_audit.json"
    path.write_text(json.dumps(audit_data), encoding="utf-8")
    return path

# -------------------- Tests --------------------

def test_module_report_generation(test_report_path, audit_report_path):
    strictness_report = StrictnessReport.parse_obj(json.loads(Path(test_report_path).read_text(encoding="utf-8")))
    test_entries = strictness_report.tests
    test_imports = strictness_report.imports

    audit_model = load_audit_report(str(audit_report_path))

    report = generate_module_report(audit_model, test_entries, test_imports)

    # Assertions
    assert "paths.py" in report, "Expected 'paths.py' module in report."
    module_data = report["paths.py"]

    assert "module_coverage" in module_data
    assert module_data["module_coverage"] == 1.0, "Coverage should be exactly 1.0"

    assert "methods" in module_data
    assert isinstance(module_data["methods"], list)
    assert any(m["name"] == "ZephyrusPaths._resolve_path" for m in module_data["methods"]), "Expected method not found."

    assert "tests" in module_data
    tests = module_data["tests"]
    print(f"DEBUG: Detected test names: {[t['test_name'] for t in tests]}")
    print(f"DEBUG: Production file being analyzed: 'paths.py'")
    assert isinstance(tests, list)
    assert any(t["test_name"] == "test_paths_config" for t in tests), "Expected 'test_paths_config' test case in results."

    for test in tests:
        assert 0.0 <= test["strictness"] <= 1.0, "Strictness out of expected bounds."
        assert 0.0 <= test["severity"] <= 1.0, "Severity out of expected bounds."