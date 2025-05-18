import json
from pathlib import Path
from scripts.doc_generation.quality_doc_generation import generate_split_reports

def test_generate_quality_reports(tmp_path):
    sample_quality = {
        "core/foo.py": {
            "docstrings": {
                "module_doc": {"description": None},
                "classes": [{"name": "X", "description": None}],
                "functions": [{"name": "bar", "description": "ok"}]
            },
            "linting": {
                "quality": {
                    "pydocstyle": {
                        "functions": {"bar": ["D100"]}
                    },
                    "mypy": {"errors": ["err 1", "err 2"]}
                }
            }
        },
        "artifacts/junk.py": {}  # should be ignored
    }

    out_dir = tmp_path / "quality"
    generate_split_reports(sample_quality, out_dir, verbose=True)

    assert (out_dir / "core.md").exists()
    assert not (out_dir / "artifacts.md").exists()
    index = (out_dir / "index.md").read_text()
    assert "- [core/](./core.md)" in index
