import pytest
from unittest.mock import MagicMock, patch, mock_open
from scripts.ai.module_idea_generator import (
    suggest_new_modules,
    generate_test_stubs,
    extract_filenames_from_code,
    export_prototypes_to_files,
    validate_test_coverage
)
import tempfile
import os
import json
from pathlib import Path

# -------------------------- Fixtures -------------------------- #

@pytest.fixture
def fake_config():
    mock = MagicMock()
    mock.persona = "concise"
    mock.prompts_by_subcategory = {
        "Architecture Planning": "Suggest modules for architecture planning.",
        "Module Prototype": "Generate code prototypes.",
        "Test Generation": "Generate test stubs."
    }
    return mock

@pytest.fixture
def fake_summary():
    return """- `load_data`: Load input data.
- `process_results`: Apply processing."""

@pytest.fixture
def fake_prototype():
    return """# Filename: module/data_loader.py
class DataLoader:
    def load(self):
        pass
"""

# -------------------------- Tests -------------------------- #

def test_extract_filenames_from_code():
    code = (
        "# Filename: module/foo.py\n```python\nprint('hi')\n```\n"
        "# Filename: test_utils.py\n```python\nprint('test')\n```"
    )
    result = extract_filenames_from_code(code)
    assert "module/foo.py" in result
    assert "test_utils.py" in result

def test_export_prototypes_to_files_creates_files():
    code = (
        "# Filename: module/data_loader.py\n"
        "```python\n# Filename: module/data_loader.py\nclass DataLoader:\n    pass\n```"
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        export_prototypes_to_files(code, output_dir=tmpdir, is_test=False)
        expected_file = Path(tmpdir) / "module" / "data_loader.py"
        assert expected_file.exists()


def test_validate_test_coverage_detects_missing():
    with tempfile.TemporaryDirectory() as mod_dir, tempfile.TemporaryDirectory() as test_dir:
        # Module file with one public function
        mod_path = os.path.join(mod_dir, "foo.py")
        with open(mod_path, "w") as f:
            f.write("""def do_work(): pass""")

        missing = validate_test_coverage(mod_dir, test_dir)
        assert "foo.do_work" in missing


@patch("scripts.ai.module_idea_generator.get_prompt_template", return_value="Suggest modules")
@patch("scripts.ai.module_idea_generator.apply_persona", side_effect=lambda p, _: p)
@patch("scripts.ai.module_idea_generator.AISummarizer")
def test_suggest_new_modules_integration(mock_summarizer_cls, mock_apply, mock_template):
    mock_summarizer = MagicMock()
    mock_summarizer.summarize_entry.side_effect = ["- `foo`: does x", "# Filename: foo.py\nclass Foo:\n    pass"]
    mock_summarizer_cls.return_value = mock_summarizer

    fake_report = {
        "my_path.py": {
            "docstrings": {
                "functions": [
                    {"name": "foo", "description": "does x"},
                ]
            }
        }
    }

    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as f:
        import json
        json.dump(fake_report, f)
        f.flush()
        suggestions, code = suggest_new_modules(f.name, config=MagicMock(), path_filter="my_path")
        assert "foo" in suggestions
        assert "Filename" in code