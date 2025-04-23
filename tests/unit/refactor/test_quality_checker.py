# tests/unit/refactor/test_quality_checker.py

import json
from pathlib import Path
from os.path import normpath
from scripts.refactor import quality_checker

# Local constants for test isolation
BLACK_REPORT = Path("black.txt")
FLAKE8_REPORT = Path("flake8.txt")
MYPY_REPORT = Path("mypy.txt")
PYDOCSTYLE_REPORT = Path("pydocstyle.txt")
COVERAGE_XML = Path("coverage.xml")


def test_black_report_parsing(tmp_path):
    """
    Unit tests for verifying the parsing and enrichment of code quality tool reports
    (Black, Flake8, MyPy, Pydocstyle, Coverage) using the quality_checker module.
    Each test checks that the corresponding report is correctly processed and
    normalized into the expected quality data structure.
    """
    report = tmp_path / BLACK_REPORT
    report.write_text("would reformat scripts/refactor/example.py")

    quality_checker.BLACK_REPORT = report
    result = {}
    report_paths = {"black": report}
    quality_checker._add_black_quality(result, report_paths)

    expected_path = normpath("refactor/example.py")
    assert expected_path in result
    assert result[expected_path]["black"]["needs_formatting"] is True


def test_flake8_report_parsing(tmp_path):
    """
    Unit tests for the quality_checker module, verifying correct parsing and normalization
    of Black, Flake8, MyPy, Pydocstyle, and Coverage reports into the expected quality data structure.
    Each test ensures that the corresponding tool's report is processed and integrated as intended.
    """
    report = tmp_path / FLAKE8_REPORT
    report.write_text("scripts/refactor/example.py:10:5: E303 too many blank lines")

    quality_checker.FLAKE8_REPORT = report
    result = {}
    report_paths = {"flake8": report}
    quality_checker._add_flake8_quality(result, report_paths)

    expected_path = normpath("refactor/example.py")
    assert expected_path in result
    issues = result[expected_path]["flake8"]["issues"]
    assert any("E303" in i["code"] for i in issues)


def test_mypy_report_parsing(tmp_path):
    """
    Unit tests for the quality_checker module, verifying correct parsing and normalization of Black,
    Flake8, MyPy, Pydocstyle, and Coverage reports.
    Each test ensures that the corresponding tool's report is processed
    and integrated into the expected quality data structure.
    """
    report = tmp_path / MYPY_REPORT
    report.write_text("scripts/refactor/example.py:12: error: Incompatible return value type")

    quality_checker.MYPY_REPORT = report
    result = {}
    report_paths = {"mypy": report}
    quality_checker._add_mypy_quality(result, report_paths)

    expected_path = normpath("refactor/example.py")
    assert expected_path in result
    assert len(result[expected_path]["mypy"]["errors"]) > 0


def test_pydocstyle_report_parsing(tmp_path):
    report = tmp_path / PYDOCSTYLE_REPORT
    report.write_text("scripts/refactor/example.py:1 in public module")

    quality_checker.PYDOCSTYLE_REPORT = report
    result = {}
    report_paths = {"pydocstyle": report}
    quality_checker._add_pydocstyle_quality(result, report_paths)

    expected_path = normpath("refactor/example.py")
    assert expected_path in result
    assert "in public module" in result[expected_path]["pydocstyle"]["issues"][0]


def test_coverage_report_parsing(tmp_path):
    xml = tmp_path / COVERAGE_XML
    xml.write_text(
        """
    <coverage>
      <packages>
        <package name="scripts.refactor">
          <classes>
            <class name="example" filename="scripts/refactor/example.py" line-rate="0.75"/>
          </classes>
        </package>
      </packages>
    </coverage>
    """
    )

    quality_checker.COVERAGE_XML = xml
    result = {}
    report_paths = {"coverage": xml}
    quality_checker._add_coverage_quality(result, report_paths)

    expected_path = normpath("refactor/example.py")
    assert expected_path in result
    assert result[expected_path]["coverage"]["percent"] == 75.0
