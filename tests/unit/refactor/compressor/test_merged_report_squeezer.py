import pytest
from scripts.refactor.compressor.merged_report_squeezer import compress_obj, decompress_obj

@pytest.fixture
def sample_merged_data():
    return {
        "module_a.py": {
            "docstrings": {
                "module_doc": {"description": "Module A", "args": None, "returns": None},
                "classes": [{"name": "ClassA", "description": "Class A", "args": "arg1", "returns": "ret"}],
                "functions": [{"name": "func_a", "description": "Func A", "args": "arg2", "returns": "ret"}]
            },
            "coverage": {"complexity": {"func_a": {"lines": 10, "covered_lines": [1, 2, 3]}}},
            "linting": {"errors": 0}
        }
    }


def test_compression_and_decompression(sample_merged_data):
    compressed = compress_obj(sample_merged_data)
    decompressed = decompress_obj(compressed)

    # Remove 'p' fields before asserting equality
    for module in decompressed.values():
        module.get("coverage", {}).pop("p", None)

    assert decompressed == sample_merged_data


def test_compressed_structure(sample_merged_data):
    compressed = compress_obj(sample_merged_data)
    assert "doc" in compressed
    assert "files" in compressed
    assert isinstance(compressed["doc"], list)
    assert "module_a.py" in compressed["files"]
