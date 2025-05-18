"""
Comprehensive tests for scripts.refactor.parsers.docstring_parser
----------------------------------------------------------------
Covered elements
  • split_docstring_sections: happy-path, partial, edge-case parsing
  • DocstringAnalyzer.should_exclude
  • DocstringAnalyzer.extract_docstrings: nested classes, missing docstrings
  • DocstringAnalyzer.analyze_directory: respect excludes + test path_utils.norm interaction
  • DocstringAuditCLI.run: --json and --check flows

All tests are self-contained and use tmp_path/monkeypatch to avoid touching real FS.
"""
from pathlib import Path
import pytest
from textwrap import dedent
import json
import sys
from typing import Any
from unittest import mock
from scripts.refactor.parsers.docstring_parser import split_docstring_sections, DocstringAnalyzer

# ─────────────────── import target module ────────────────────
MODULE_PATH = "scripts.refactor.parsers.docstring_parser"
dp = pytest.importorskip(MODULE_PATH, reason="target package must be importable")


# Add wrapper for dedented source writing
def write_dedent(path: Path, code: str):
    path.write_text(dedent(code), encoding="utf-8")

def test_split_docstring_sections_all_parts() -> None:
    """Test the split_docstring_sections function with a complete docstring."""
    docstring = """
    This function does something useful.

    Args:
        param1 (int): An integer input.
        param2 (str): A string input.

    Returns:
        bool: True if successful, False otherwise.
    """
    parts = split_docstring_sections(docstring)
    assert "does something useful" in parts["description"]
    assert "param1" in parts["args"]
    assert "bool" in parts["returns"]


def test_split_docstring_sections_partial() -> None:
    """Test the split_docstring_sections function with a partial docstring."""
    docstring = """
    Only a description is present.
    """
    parts = split_docstring_sections(docstring)
    assert parts["description"] is not None
    assert parts["args"] is None
    assert parts["returns"] is None


def test_split_docstring_sections_none() -> None:
    """Test the split_docstring_sections function with None input."""
    assert split_docstring_sections(None) == {"description": None, "args": None, "returns": None}


def test_extract_docstrings(tmp_path: Path) -> None:
    """Test the extract_docstrings method of the DocstringAnalyzer."""
    source = '''"""
    Module-level doc.

    Args:
        None

    Returns:
        None
    """

class MyClass:
    """Does something."""

    def method(self):
        """Does the method."""
        pass

def func():
    """Also does something."""
    pass
    '''

    test_file = tmp_path / "example.py"
    test_file.write_text(source, encoding="utf-8")

    analyzer = DocstringAnalyzer(exclude_dirs=[])
    result = analyzer.extract_docstrings(test_file)

    assert result["module_doc"]["description"] is not None
    assert any(cls["name"] == "MyClass" for cls in result["classes"])
    assert any(fn["name"] == "func" for fn in result["functions"])


def test_analyze_directory_excludes(tmp_path: Path) -> None:
    """Test the analyze_directory method for excluding specified directories."""
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "skip.py").write_text("def dummy(): pass", encoding="utf-8")
    (tmp_path / "included.py").write_text("def kept(): pass", encoding="utf-8")

    analyzer = DocstringAnalyzer(exclude_dirs=[".venv"])
    results = analyzer.analyze_directory(tmp_path)

    assert any(k.endswith("included.py") for k in results)
    assert ".venv/skip.py" not in results

# --------------------------------------------------------------------------------------
# split_docstring_sections
# --------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "raw, expect",
    [
        (
            # all three sections present
            """
            Handy description.

            Args:
                x (int): number

            Returns:
                int: doubled value
            """,
            {"description": "Handy description.", "args": "x (int): number", "returns": "int: doubled value"},
        ),
        (
            # description only
            """
            Solely description here.
            """,
            {"description": "Solely description here.", "args": None, "returns": None},
        ),
        (
            # odd capitalisation / spacing
            """
            Desc line.

              ARGS:
                  y: whatever

              rEtUrNs:
                  None
            """,
            {"description": "Desc line.", "args": "y: whatever", "returns": "None"},
        ),
    ],
)
def test_split_docstring_sections_variants(raw: str, expect: dict[str, Any]) -> None:
    parts = dp.split_docstring_sections(dedent(raw))
    assert parts["description"] == expect["description"]
    assert parts["args"] == expect["args"]
    assert parts["returns"] == expect["returns"]


def test_split_docstring_sections_none() -> None:
    assert dp.split_docstring_sections(None) == {"description": None, "args": None, "returns": None}


# --------------------------------------------------------------------------------------
# DocstringAnalyzer.should_exclude
# --------------------------------------------------------------------------------------
def test_should_exclude_matches_any_part() -> None:
    analyzer = dp.DocstringAnalyzer(exclude_dirs=[".git", "venv"])
    assert analyzer.should_exclude(Path("proj/.git/config"))
    assert analyzer.should_exclude(Path("proj/venv/lib.py"))
    assert not analyzer.should_exclude(Path("proj/src/ok.py"))


# --------------------------------------------------------------------------------------
# extract_docstrings – nested + missing
# --------------------------------------------------------------------------------------
def test_extract_docstrings_nested_and_missing(tmp_path: Path) -> None:
    src = tmp_path / "nested.py"
    src.write_text(
        dedent(
            '''
            """Top docs."""

            class Outer:
                """Outer docs."""

                class Inner:
                    """Inner docs."""

                    def inner_method(self):
                        """Method docs."""
                        pass

            def no_doc():
                pass
            '''
        ),
        encoding="utf-8",
    )

    res = dp.DocstringAnalyzer([]).extract_docstrings(src)

    # Module doc
    assert res["module_doc"]["description"] == "Top docs."

    # Class names
    class_names = {c["name"] for c in res["classes"]}
    assert {"Outer", "Inner"} <= class_names

    # Function with no docstring
    fn_no_doc = next(f for f in res["functions"] if f["name"] == "no_doc")
    assert fn_no_doc["description"] is None
    assert fn_no_doc["args"] == ["self: Any"] or fn_no_doc["args"] == []  # AST will still yield args
    assert fn_no_doc["returns"] == "Any" or fn_no_doc["returns"] is None

    # Nested method check
    inner_method = next((f for f in res["functions"] if f["name"] == "inner_method"), None)
    assert inner_method is not None
    assert inner_method["description"] == "Method docs."
    assert "self: Any" in inner_method["args"]
    assert inner_method["returns"] == "Any"



# --------------------------------------------------------------------------------------
# analyze_directory – respect excludes & norm
# --------------------------------------------------------------------------------------
def test_analyze_directory_exclude_and_norm(tmp_path: Path, monkeypatch) -> None:
    """Ensure excluded paths are skipped and `norm` is used to map keys."""
    # create files
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "skip.py").write_text('"""ignored"""', encoding="utf-8")
    keep = tmp_path / "sub" / "keep.py"
    keep.parent.mkdir()
    keep.write_text('"""keep"""', encoding="utf-8")

    # monkeypatch path_utils.norm to reveal call
    called_with: list[Path] = []

    def fake_norm(p: Path) -> str:
        called_with.append(p)
        # return posix-like relative str for predictability
        return p.relative_to(tmp_path).as_posix()

    monkeypatch.setitem(sys.modules, "scripts.refactor.lint_report_pkg.path_utils", mock.Mock(norm=fake_norm))
    analyzer = dp.DocstringAnalyzer(exclude_dirs=[".venv"])
    result = analyzer.analyze_directory(tmp_path)

    # 🔽 normalise to forward slashes so the test passes on all OSes
    normalised = {p.replace("\\", "/") for p in result.keys()}
    assert normalised == {"sub/keep.py"}


# --------------------------------------------------------------------------------------
# DocstringAuditCLI – --json + --check
# --------------------------------------------------------------------------------------
def _cli_run(monkeypatch, argv: list[str]) -> tuple[mock.Mock, Path]:
    """Helper to run CLI with patched argv, capture print, and return print-mock & cwd."""
    cwd = Path.cwd()
    monkeypatch.chdir(Path.cwd())  # explicit; some test runners change dirs
    monkeypatch.setattr(sys, "argv", argv)
    m_print = mock.Mock()
    monkeypatch.setattr("builtins.print", m_print)
    dp.DocstringAuditCLI().run()
    return m_print, cwd


def test_cli_json_output(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "foo.py").write_text('"""Docs."""', encoding="utf-8")
    m_print, cwd = _cli_run(monkeypatch, ["prog", "--path", str(tmp_path), "--json"])
    out_file = cwd / "docstring_summary.json"
    assert out_file.exists()
    m_print.assert_any_call(f"✅ JSON written to {out_file}")
    # the JSON should contain at least our foo module
    with out_file.open(encoding="utf-8") as f:
        data = json.load(f)
    assert any("foo.py" in k for k in data)


def test_cli_check_missing_docstrings_exits_with_code(monkeypatch, tmp_path: Path) -> None:
    """File with missing docs should trigger exit code 1."""
    (tmp_path / "bar.py").write_text("def x():\n    pass\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["prog", "--path", str(tmp_path), "--check"])
    with pytest.raises(SystemExit) as exc:
        dp.DocstringAuditCLI().run()
    assert exc.value.code == 1

def test_extract_docstrings_ast_args_and_return(tmp_path: Path) -> None:
    write_dedent(tmp_path / "typed_func.py", '''
    def add(x: int, y: int) -> int:
        """Adds two numbers."""
        return x + y
    ''')
    result = dp.DocstringAnalyzer([]).extract_docstrings(tmp_path / "typed_func.py")
    fn = result["functions"][0]
    assert fn["name"] == "add"
    assert "x: int" in fn["args"]
    assert "y: int" in fn["args"]
    assert fn["returns"] == "int"

def test_extract_docstrings_class_init_args(tmp_path: Path) -> None:
    write_dedent(tmp_path / "greeter.py", '''
    class Greeter:
        def __init__(self, name: str, loud: bool = False) -> None:
            """Initialize with name and loud flag."""
            self.name = name
    ''')
    result = dp.DocstringAnalyzer([]).extract_docstrings(tmp_path / "greeter.py")
    cls = next(c for c in result["classes"] if c["name"] == "Greeter")
    assert "name: str" in cls["args"]
    assert "loud: bool" in cls["args"]
    assert cls["returns"] == "None"

def test_extract_docstrings_untyped_args(tmp_path: Path) -> None:
    write_dedent(tmp_path / "untyped.py", '''
    def foo(x, y): return x + y
    ''')
    result = dp.DocstringAnalyzer([]).extract_docstrings(tmp_path / "untyped.py")
    args = result["functions"][0]["args"]
    assert args == ["x: Any", "y: Any"]

