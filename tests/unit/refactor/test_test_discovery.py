import tempfile
import textwrap
import json
from pathlib import Path
from scripts.refactor.test_discovery import (
    parse_ast_tree,
    extract_test_functions_from_tree,
    extract_imports_from_tree,
    analyze_strictness,
    scan_test_directory,
    StrictnessEntry,
    StrictnessReport
)

def test_extract_test_functions_single_function():
    test_code = textwrap.dedent("""
    def test_example():
        assert True
    """)
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as tmp_file:
        tmp_file.write(test_code)
        tmp_file_path = Path(tmp_file.name)

    tree, file_stem = parse_ast_tree(tmp_file_path)
    results = extract_test_functions_from_tree(tree, file_stem)

    assert len(results) == 1
    assert results[0]["name"] == "example"

def test_extract_imports():
    test_code = textwrap.dedent("""
    import os
    from sys import path
    import my_module.submodule
    """)
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as tmp_file:
        tmp_file.write(test_code)
        tmp_file_path = Path(tmp_file.name)

    tree, _ = parse_ast_tree(tmp_file_path)
    imports = extract_imports_from_tree(tree)

    assert "os" in imports
    assert "sys" in imports
    assert "my_module" in imports

def test_analyze_strictness_correct_metrics():
    lines = [
        "def test_sample():\n",
        "    assert 1 == 1\n",
        "    if True:\n",
        "        assert 2 == 2\n",
        "    mock_call()\n",
        "    pytest.raises(ValueError)\n"
    ]
    func_meta = {"name": "test_sample", "path": "test_sample.py", "start": 1, "end": 6}
    entry = analyze_strictness(lines, func_meta)

    assert isinstance(entry, StrictnessEntry)
    assert entry.asserts == 2
    assert entry.mocks == 1
    assert entry.raises == 1
    assert entry.branches == 1
    assert entry.length == 6
    assert 0.0 <= entry.strictness_score <= 1.0

def test_scan_test_directory_and_generate_report():
    test_code = textwrap.dedent("""
    def test_case():
        assert True
        for i in range(3):
            assert i >= 0
    """)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "test_sample.py"
        tmp_file.write_text(test_code)

        report = scan_test_directory(Path(tmp_dir))

        assert isinstance(report, StrictnessReport)
        assert len(report.tests) == 1
        entry = report.tests[0]
        assert entry.name == "case"
        assert entry.asserts == 2
        assert entry.branches == 1
        assert 0.0 <= entry.strictness_score <= 1.0

def test_strictness_report_serialization():
    entry = StrictnessEntry(
        name="test_serialization",
        file="test_file.py",
        start=1,
        end=5,
        asserts=3,
        mocks=0,
        raises=1,
        branches=2,
        length=5,
        strictness_score=0.8
    )
    report = StrictnessReport(tests=[entry])

    json_str = report.to_json()
    data = json.loads(json_str)

    assert "tests" in data
    assert data["tests"][0]["name"] == "test_serialization"

def test_strictness_report_save(tmp_path):
    entry = StrictnessEntry(
        name="test_save",
        file="test_file.py",
        start=1,
        end=5,
        asserts=2,
        mocks=1,
        raises=0,
        branches=1,
        length=5,
        strictness_score=0.7
    )
    report = StrictnessReport(tests=[entry])

    output_path = tmp_path / "strictness_report.json"
    report.save(output_path)

    assert output_path.exists()
    content = json.loads(output_path.read_text(encoding="utf-8"))
    assert content["tests"][0]["name"] == "test_save"