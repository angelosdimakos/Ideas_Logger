import json
from pathlib import Path
import sys
from textwrap import dedent
from types import SimpleNamespace
from unittest import mock

import pytest

from scripts.refactor.strictness_analyzer import (
    ComplexityMetrics,
    StrictnessEntry,
    StrictnessReport,
    weighted_coverage,
    get_test_severity,
    fuzzy_match,
    should_assign_test_to_module,
    validate_report_schema,
    load_audit_report,
    load_test_report,
    generate_module_report
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
    print("DEBUG: Production file being analyzed: 'paths.py'")
    assert isinstance(tests, list)
    assert any(t["test_name"] == "test_paths_config" for t in tests), "Expected 'test_paths_config' test case in results."

    for test in tests:
        assert 0.0 <= test["strictness"] <= 1.0, "Strictness out of expected bounds."
        assert 0.0 <= test["severity"] <= 1.0, "Severity out of expected bounds."

# ─────────────────────────────── weighted_coverage ───────────────────────────────
def test_weighted_coverage_varied_loc() -> None:
    funcs = {
        "a": ComplexityMetrics(coverage=0.0, complexity=1, hits=0, lines=10, covered_lines=[], missing_lines=list(range(10)), loc=10),
        "b": ComplexityMetrics(coverage=1.0, complexity=1, hits=1, lines=1,  covered_lines=[1], missing_lines=[], loc=1),
    }
    # Expected weighted = (0*10 + 1*1) / 11 ≈ 0.09
    assert round(weighted_coverage(funcs), 2) == 0.09


# ─────────────────────────────── get_test_severity ───────────────────────────────
def test_get_test_severity_no_coverage() -> None:
    entry = StrictnessEntry(name="t", file="x", strictness_score=0.8)
    assert get_test_severity(entry, coverage=None) == 0.8

def test_get_test_severity_blend() -> None:
    entry = StrictnessEntry(name="t", file="x", strictness_score=0.6)
    # High coverage should *lower* severity
    assert get_test_severity(entry, coverage=0.9, alpha=0.7) < 0.6
    # Low coverage should *raise* severity (up to cap)
    assert get_test_severity(entry, coverage=0.1, alpha=0.7) > 0.6


# ───────────────────────────────── fuzzy_match ───────────────────────────────────
def test_fuzzy_match_threshold() -> None:
    assert fuzzy_match("paths", "test_paths", threshold=80)
    assert not fuzzy_match("paths", "utilities", threshold=80)


# ───────────────────── should_assign_test_to_module branches ─────────────────────
@pytest.fixture
def dummy_entry():
    return lambda name, file="tests/unit/test_paths.py": StrictnessEntry(
        name=name, file=file, strictness_score=0.1
    )

def test_assign_by_filename_convention(dummy_entry):
    assert should_assign_test_to_module("paths", [], dummy_entry("test_paths_config"), {}, 90)

def test_assign_by_imports(dummy_entry):
    imports = {"test_paths": ["paths"]}
    assert should_assign_test_to_module("paths", [], dummy_entry("unrelated"), imports, 90)

def test_assign_by_class_name_fuzzy(dummy_entry):
    entry = dummy_entry("TestPaths.Test_case")
    assert should_assign_test_to_module("paths", [], entry, {}, 80)

def test_reject_without_any_match(dummy_entry):
    entry = dummy_entry("completely_unrelated",
                        file="tests/unit/test_misc.py")  # <-- no 'paths' in stem
    assert not should_assign_test_to_module("paths", [], entry, {}, 95)


# ───────────────────────────── validate_report_schema ────────────────────────────
def test_validate_audit_schema_ok() -> None:
    minimal = {"dummy.py": {"complexity": {}}}
    assert validate_report_schema(minimal, "audit")

def test_validate_final_schema_bad() -> None:
    # module_coverage expects a float; the string "bad" cannot be coerced
    invalid = {
        "modules": {
            "foo.py": {
                "module_coverage": "bad",   # <- forces ValidationError
                "methods": [],
                "tests": []
            }
        }
    }
    assert not validate_report_schema(invalid, "final")


# ─────────────────────── loader error handling (happy path) ───────────────────────
def test_loaders_error_branches(tmp_path, monkeypatch):
    # Make Path.exists return False → should exit(1)
    monkeypatch.setattr(Path, "exists", lambda self: False)
    with pytest.raises(SystemExit):
        load_audit_report("nope.json")
    with pytest.raises(SystemExit):
        load_test_report("nope.json")


# ───────────────────────── duplicate-test prevention ─────────────────────────────
def test_duplicate_test_assignment_is_prevented(tmp_path):
    from scripts.refactor.strictness_analyzer import generate_module_report, AuditReport

    audit_json = {"foo.py": {"complexity": {}}}
    audit = AuditReport.parse_obj(audit_json)
    # same test referenced twice (one with class prefix)
    tests = [
        StrictnessEntry(name="TestFoo.test_bar", file="tests/unit/test_foo.py", strictness_score=0.1),
        StrictnessEntry(name="test_bar",            file="tests/unit/test_foo.py", strictness_score=0.1),
    ]
    imports = {"test_foo": ["foo"]}

    rep = generate_module_report(audit, tests, imports)
    tests_out = rep["foo.py"]["tests"]
    assert len(tests_out) == 1    # ← duplicate pruned