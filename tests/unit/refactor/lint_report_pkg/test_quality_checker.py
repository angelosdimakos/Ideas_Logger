from pathlib import Path
from scripts.refactor.lint_report_pkg.plugins.black import BlackPlugin
from scripts.refactor.lint_report_pkg.plugins.flake8 import Flake8Plugin
from scripts.refactor.lint_report_pkg.plugins.mypy import MypyPlugin
from scripts.refactor.lint_report_pkg.plugins.pydocstyle import PydocstylePlugin

BLACK_REPORT = Path("black.txt")
FLAKE8_REPORT = Path("flake8.txt")
MYPY_REPORT = Path("mypy.txt")
PYDOCSTYLE_REPORT = Path("pydocstyle.txt")
COVERAGE_XML = Path("coverage.xml")

def find_result_key(result: dict, expected_filename: str) -> str:
    """
    Helper to normalize and find the correct key regardless of mutant path prefixes.
    """
    for key in result.keys():
        normalized_key = key.replace("\\", "/")
        if normalized_key.endswith(expected_filename):
            return key
    raise KeyError(f"Expected to find a key ending with '{expected_filename}', but found: {list(result.keys())}")

def test_black_report_parsing(tmp_path):
    report = tmp_path / BLACK_REPORT
    report.write_text("would reformat scripts/refactor/example.py")

    plugin = BlackPlugin()
    plugin.default_report = report

    result = {}
    plugin.parse(result)

    key = find_result_key(result, "scripts/refactor/example.py")
    assert result[key]["black"]["needs_formatting"] is True

def test_flake8_report_parsing(tmp_path):
    report = tmp_path / FLAKE8_REPORT
    report.write_text("scripts/refactor/example.py:10:5: E303 too many blank lines")

    plugin = Flake8Plugin()
    plugin.default_report = report

    result = {}
    plugin.parse(result)

    key = find_result_key(result, "scripts/refactor/example.py")
    issues = result[key]["flake8"]["issues"]
    assert any(i["code"] == "E303" for i in issues)

def test_mypy_report_parsing(tmp_path):
    report = tmp_path / MYPY_REPORT
    report.write_text("scripts/refactor/example.py:12: error: Incompatible return value type")

    plugin = MypyPlugin()
    plugin.default_report = report

    result = {}
    plugin.parse(result)

    key = find_result_key(result, "scripts/refactor/example.py")
    assert result[key]["mypy"]["errors"]

def test_pydocstyle_report_parsing(tmp_path):
    report = tmp_path / PYDOCSTYLE_REPORT
    report.write_text("scripts/refactor/example.py:1 in public module `<module>`\nD100: Missing docstring in public module")

    real_path = tmp_path / "scripts" / "refactor" / "example.py"
    real_path.parent.mkdir(parents=True)
    real_path.write_text("def foo(): pass")

    plugin = PydocstylePlugin()
    plugin.default_report = report

    result = {}
    plugin.parse(result)

    key = find_result_key(result, "scripts/refactor/example.py")
    assert "Missing docstring" in result[key]["pydocstyle"]["functions"]["<module>"][0]["message"]

