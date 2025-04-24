from pathlib import Path
from scripts.refactor.parsers.docstring_parser import (
    split_docstring_sections,
    DocstringAnalyzer
)


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
    assert split_docstring_sections(None) == {
        "description": None,
        "args": None,
        "returns": None
    }


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

    assert "included.py" in results
    assert ".venv/skip.py" not in results
