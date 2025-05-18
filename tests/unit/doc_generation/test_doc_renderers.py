import pytest
from scripts.doc_generation import doc_renderers as dr

def test_render_folder_coverage_basic():
    result = dr.render_folder_coverage("core", [
        ("core/foo.py", {"summary": {"num_statements": 10, "covered_lines": 8, "percent_covered": 80.0}}),
        ("core/bar.py", {"summary": {"num_statements": 10, "covered_lines": 6, "percent_covered": 60.0}})
    ])
    assert "# Test Coverage Report for `core/`" in result
    assert "| foo.py | 80.00% | N/A |" in result
    assert "**Folder Coverage:** 70.00%" in result  # 14/20

def test_render_coverage_index_output():
    lines = dr.render_coverage_index(["core", "utils"], {
        "percent_covered": 90.0,
        "covered_lines": 45,
        "num_statements": 50,
        "covered_branches": 12,
        "num_branches": 20
    })
    assert "| Overall Coverage | 90.00% |" in lines
    assert "- [core/](./core.md)" in lines

def test_render_folder_report_verbose():
    """
    Tests that the verbose folder report rendering includes documentation, linting, and MyPy error sections with correct content.
    """
    data = {
        "totals": {"critical": 1, "high": 2, "medium": 3, "low": 4},
        "docs": [{"file": "file1.py", "module": 1, "classes": 2, "functions": 3}],
        "lint": [{"file": "file2.py", "issues": {"critical": 1, "high": 1, "medium": 1, "low": 1}, "total": 4}],
        "mypy": {"file3.py": ["error 1", "error 2"]}
    }
    out = dr.render_folder_report("core", data, verbose=True)
    assert "## 📄 Missing Documentation" in out
    assert "| file1.py | 1 | 2 | 3 |" in out
    assert "## 🧹 Linting Issues" in out
    assert "| file2.py | 1 | 1 | 1 | 1 | 4 |" in out
    assert "## 📋 MyPy Errors" in out
    assert "error 1" in out

def test_render_quality_index_links():
    """
    Tests that the quality index renderer outputs markdown links for each folder.
    
    Asserts that the rendered index includes correctly formatted links to the quality reports for the specified folders.
    """
    index = dr.render_quality_index(["core", "scripts"])
    assert "- [core/](./core.md)" in index
    assert "- [scripts/](./scripts.md)" in index

def test_render_module_docs_all_sections():
    """
    Tests that `render_module_docs` generates module documentation with all sections.
    
    Verifies that the rendered output includes module headers, class and function sections, parameter and return type details, and descriptions for each documented object.
    """
    docstrings = {
        "module_doc": {"description": "Top-level module."},
        "classes": [
            {
                "name": "MyClass",
                "description": "A class.",
                "args": "x: int",
                "returns": "None"
            }
        ],
        "functions": [
            {
                "name": "my_func",
                "description": "Does stuff.",
                "args": "y: str",
                "returns": "bool"
            }
        ]
    }

    rendered = dr.render_module_docs("core/foo.py", docstrings)

    # ✅ Matches new header layout
    assert "## `core.foo`" in rendered

    # ✅ Class section and content
    assert "### 📦 Classes" in rendered
    assert "#### `MyClass`" in rendered
    assert "**Parameters:**" in rendered
    assert "x: int" in rendered

    # ✅ Function section and content
    assert "### 🛠️ Functions" in rendered
    assert "#### `my_func`" in rendered
    assert "Does stuff." in rendered
    assert "**Returns:**" in rendered
    assert "bool" in rendered

def test_render_docstring_index_output():
    """
    Tests that the docstring index renderer outputs correct markdown links for modules and their documented objects.
    """
    index = dr.render_docstring_index([("core", [("foo", "core.foo"), ("bar", "core.bar")])])
    assert any("[core/](core.md)" in line for line in index)
    assert "- [core/](core.md)" in index
