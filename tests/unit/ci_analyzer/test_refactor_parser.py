import json
import pytest
from scripts.ci_analyzer.refactor_parser import RefactorParser

def test_parse_refactor_report(tmp_path):
    data = {
        "scripts/core/core.py": {
            "complexity": {
                "some_method": {"cyclomatic": 5}
            }
        },
        "scripts/gui/gui.py": {
            "complexity": {
                "init_ui": {"cyclomatic": 4},
                "refresh": {"cyclomatic": 3}
            }
        }
    }
    sample_path = tmp_path / "refactor.json"
    sample_path.write_text(json.dumps(data), encoding="utf-8-sig")

    parser = RefactorParser(path=sample_path)
    result = parser.parse()

    assert result["file_count"] == 2
    assert result["method_count"] == 3
    assert result["type"] == "refactor"
