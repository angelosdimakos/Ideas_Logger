from pathlib import Path

from scripts.refactor.lint_report_pkg.path_utils import norm
from scripts.refactor.lint_report_pkg.plugins.black import BlackPlugin
from scripts.refactor.lint_report_pkg.plugins.flake8_plugin import Flake8Plugin
from scripts.refactor.lint_report_pkg.plugins.mypy import MypyPlugin
from scripts.refactor.lint_report_pkg.plugins.pydocstyle import PydocstylePlugin
from scripts.refactor.lint_report_pkg.plugins.coverage_plugin import CoveragePlugin

# local constants
BLACK_REPORT = Path("black.txt")
FLAKE8_REPORT = Path("flake8.txt")
MYPY_REPORT = Path("mypy.txt")
PYDOCSTYLE_REPORT = Path("pydocstyle.txt")
COVERAGE_XML = Path("coverage.xml")


def test_black_report_parsing(tmp_path):
    report = tmp_path / BLACK_REPORT
    report.write_text("would reformat scripts/refactor/example.py")

    plugin = BlackPlugin()
    plugin.default_report = report

    result = {}
    plugin.parse(result)

    expected = norm("scripts/refactor/example.py")
    assert expected in result
    assert result[expected]["black"]["needs_formatting"] is True


def test_flake8_report_parsing(tmp_path):
    report = tmp_path / FLAKE8_REPORT
    report.write_text("scripts/refactor/example.py:10:5: E303 too many blank lines")

    plugin = Flake8Plugin()
    plugin.default_report = report

    result = {}
    plugin.parse(result)

    expected = norm("scripts/refactor/example.py")
    issues = result[expected]["flake8"]["issues"]
    assert any(i["code"] == "E303" for i in issues)


def test_mypy_report_parsing(tmp_path):
    report = tmp_path / MYPY_REPORT
    report.write_text("scripts/refactor/example.py:12: error: Incompatible return value type")

    plugin = MypyPlugin()
    plugin.default_report = report

    result = {}
    plugin.parse(result)

    expected = norm("scripts/refactor/example.py")
    assert expected in result
    assert result[expected]["mypy"]["errors"]


def test_pydocstyle_report_parsing(tmp_path):
    report = tmp_path / "pydocstyle.txt"
    report.write_text("scripts/refactor/example.py:1 in public module `<module>`\nD100: Missing docstring in public module")
    real_path = tmp_path / "scripts" / "refactor" / "example.py"
    real_path.parent.mkdir(parents=True)
    real_path.write_text("def foo(): pass")  # create the actual file so norm works correctly

    plugin = PydocstylePlugin()
    plugin.default_report = report

    result = {}
    plugin.parse(result)

    expected = str(Path("scripts/refactor/example.py")).replace("\\", "/")
    result = {k.replace("\\", "/"): v for k, v in result.items()}

    assert expected in result
    assert "Missing docstring" in result[expected]["pydocstyle"]["functions"]["<module>"][0]["message"]

def test_coverage_report_parsing(tmp_path):
    xml = tmp_path / COVERAGE_XML
    xml.write_text(
        """<coverage>
        <packages>
          <package name=\"scripts.refactor\">
            <classes>
              <class name=\"example\"
                     filename=\"scripts/refactor/example.py\"
                     line-rate=\"0.75\"/>
            </classes>
          </package>
        </packages>
      </coverage>"""
    )

    plugin = CoveragePlugin()
    plugin.default_report = xml

    result = {}
    plugin.parse(result)

    expected = norm("scripts/refactor/example.py")
    assert expected in result
    assert result[expected]["coverage"]["percent"] == 75.0
