import numpy as np
from unittest.mock import patch, MagicMock
from scripts.config.config_loader import get_effective_config, get_config_value
from scripts.indexers.base_indexer import BaseIndexer  # Newly added import
from scripts.indexers.summary_indexer import SummaryIndexer
from scripts.utils.file_utils import read_json, write_json
import json
from pathlib import Path
from scripts.paths import ZephyrusPaths

def make_test_indexer(encoding_offset=0.1):
    config = get_effective_config()
    with patch("scripts.indexers.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array(
            [[i + encoding_offset for i in range(384)] for _ in texts]
        )
        return BaseIndexer(
            summaries_path=get_config_value(config, "correction_summaries_path", ""),
            index_path=get_config_value(config, "faiss_index_path", ""),
            metadata_path=get_config_value(config, "faiss_metadata_path", "")
        )

def make_raw_indexer(embedding_offset=0.1):
    """
    Creates and returns a raw log indexer (a BaseIndexer configured for raw logs)
    using test configuration values.
    """
    config = get_effective_config()
    with patch("scripts.indexers.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array(
            [[i + embedding_offset for i in range(384)] for _ in texts]
        )
        return BaseIndexer(
            summaries_path=get_config_value(config, "raw_log_path", ""),
            index_path=get_config_value(config, "raw_log_index_path", ""),
            metadata_path=get_config_value(config, "raw_log_metadata_path", "")
        )

def make_summary_indexer(embedding_offset=0.1):
    """
    Creates and returns a summary indexer using test configuration values.
    """
    config = get_effective_config()
    with patch("scripts.indexers.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array(
            [[i + embedding_offset for i in range(384)] for _ in texts]
        )
        return SummaryIndexer(
            summaries_path=get_config_value(config, "correction_summaries_path", ""),
            index_path=get_config_value(config, "faiss_index_path", ""),
            metadata_path=get_config_value(config, "faiss_metadata_path", "")
        )

def assert_resolved_test_path(config: dict, key: str, expected_suffix: str):
    value = config.get(key)
    assert value is not None, f"Missing key: {key}"
    assert expected_suffix in value.replace("\\", "/"), f"{key} should include {expected_suffix}, got: {value}"
    assert "pytest" in value or "tmp" in value.lower(), f"{key} should point to test path, got: {value}"

def make_fake_logs(date_str: str, category: str, subcat: str, count: int = 5):
    return {
        date_str: {
            category: {
                subcat: [{"timestamp": f"{date_str} 10:{i:02d}:00", "content": f"entry {i}"} for i in range(count)]
            }
        }
    }

def make_dummy_aisummarizer(success=True, fallback_response="Fallback summary."):
    class Dummy:
        def summarize_entries_bulk(self, entries, subcategory=None):
            if not success:
                raise Exception("Simulated failure")
            return [f"Summary: {e['content']}" for e in entries]
        def _fallback_summary(self, full_prompt):
            return fallback_response
    return Dummy()

def assert_summary_structure(summaries: dict, category: str, subcat: str):
    assert "global" in summaries
    assert category in summaries["global"]
    assert subcat in summaries["global"][category]

def make_fake_paths(temp_dir: Path) -> ZephyrusPaths:
    # Create a ZephyrusPaths instance using temp_dir as the base directory.
    return ZephyrusPaths.from_config(temp_dir)

def make_dummy_logger_core():
    dummy_core = MagicMock()
    # Set up the nested structure for log_manager.
    mock_log_manager = MagicMock()
    mock_log_manager.json_log_file = MagicMock(spec=Path)
    mock_log_manager.json_log_file.read_text.return_value = "{}"  # empty JSON log
    dummy_core.log_manager = mock_log_manager
    return dummy_core

def write_json(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2))

def toggle_test_mode(flag: bool):
    config_path = "config.json"
    config = read_json(config_path)
    config["test_mode"] = flag
    write_json(Path(config_path), config)

def reset_logger_state(logger_core):
    for path in [
        logger_core.json_log_file,
        logger_core.summary_tracker_file,
        logger_core.correction_summaries_file
    ]:
        if path.exists():
            path.write_text("{}", encoding="utf-8")
