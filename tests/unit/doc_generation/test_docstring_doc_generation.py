from pathlib import Path
from scripts.doc_generation.docstring_doc_generation import generate_split_docstring_docs

def test_generate_docstring_docs_nested(tmp_path):
    # 🧪 Mock input: a mix of valid and ignored modules
    mock_docstrings = {
        "core/foo.py": {
            "module_doc": {"description": "Top-level doc."},
            "classes": [],
            "functions": []
        },
        "core/utils/bar.py": {
            "module_doc": {"description": "Nested utils doc."},
            "classes": [],
            "functions": []
        },
        "tests\\test_foo.py": {  # Should be ignored
            "module_doc": {"description": "Should be ignored"},
            "classes": [],
            "functions": []
        }
    }

    # 📦 Generate docs into a temp folder
    out_path = tmp_path / "api"
    generate_split_docstring_docs(mock_docstrings, out_path)

    # 📄 core.md should only include core/foo.py
    core_md = out_path / "core.md"
    assert core_md.exists(), "❌ Missing expected core.md output"
    core_text = core_md.read_text()
    assert "Top-level doc." in core_text, "❌ Missing docstring from core/foo.py"
    assert "Nested utils doc." not in core_text, "❌ Unexpected docstring from core/utils/bar.py in core.md"

    # 📄 core_utils.md should include bar.py
    core_utils_md = out_path / "core_utils.md"
    assert core_utils_md.exists(), "❌ Missing expected core_utils.md output"
    utils_text = core_utils_md.read_text()
    assert "Nested utils doc." in utils_text, "❌ Missing docstring from core/utils/bar.py"

    # 🚫 tests/ folder must be skipped entirely
    assert not (out_path / "tests").exists(), "❌ tests/ folder should not exist in output"

    # 🧭 Index should link to both files
    index_md = out_path / "index.md"
    assert index_md.exists(), "❌ index.md was not generated"
    index_text = index_md.read_text()
    assert "- [core/](core.md)" in index_text, "❌ Index missing core.md link"
    # 🧭 Index should link to both files
    index_md = out_path / "index.md"
    assert index_md.exists(), "❌ index.md was not generated"
    index_text = index_md.read_text()
    assert "- [core/](core.md)" in index_text, "❌ Index missing core.md link"
    assert "- [core/utils/](core_utils.md)" in index_text, "❌ Index missing core_utils.md link"
