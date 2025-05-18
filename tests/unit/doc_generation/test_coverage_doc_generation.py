import json
from pathlib import Path
from scripts.doc_generation.coverage_doc_generation import generate_split_coverage_docs

def test_generate_split_coverage_docs(tmp_path):
    sample_data = {
        "files": {
            "core/foo.py": {"summary": {"num_statements": 10, "covered_lines": 7, "percent_covered": 70.0}},
            "tests/test_foo.py": {"summary": {"num_statements": 5, "covered_lines": 5, "percent_covered": 100.0}},
        },
        "totals": {
            "percent_covered": 80.0,
            "covered_lines": 7,
            "num_statements": 10,
            "covered_branches": 3,
            "num_branches": 5
        }
    }

    output_dir = tmp_path / "docs"
    generate_split_coverage_docs(sample_data, output_dir)

    files = list(output_dir.glob("*.md"))
    assert any("core.md" in str(f) for f in files)
    assert (output_dir / "index.md").exists()
    content = (output_dir / "core.md").read_text()
    assert "**Folder Coverage:**" in content
