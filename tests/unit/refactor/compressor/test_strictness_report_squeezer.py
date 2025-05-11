import pytest
from scripts.refactor.compressor.strictness_report_squeezer import compress_obj, decompress_obj, semantic_equal

@pytest.fixture
def sample_strictness_data():
    return {
        "modules": {
            "paths.py": {
                "module_coverage": 0.93,
                "methods": [{"name": "resolve_path", "coverage": 1.0, "complexity": 1}],
                "tests": [{"test_name": "test_resolve_path", "strictness": 0.5, "severity": 0.5}]
            }
        }
    }

def test_strictness_compression_roundtrip(sample_strictness_data):
    compressed = compress_obj(sample_strictness_data)
    decompressed = decompress_obj(compressed)
    assert semantic_equal(sample_strictness_data, decompressed)

def test_strictness_compressed_keys(sample_strictness_data):
    compressed = compress_obj(sample_strictness_data)
    assert "modules" in compressed
    assert "paths.py" in compressed["modules"]
    module = compressed["modules"]["paths.py"]
    assert "module_coverage" in module
    assert "methods" in module
    assert "tests" in module
