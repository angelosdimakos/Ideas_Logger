import numpy as np
from unittest.mock import patch
from pathlib import Path
from scripts.config.config_loader import get_effective_config, get_config_value
from scripts.indexers.base_indexer import BaseIndexer
from scripts.indexers.summary_indexer import SummaryIndexer
from scripts.indexers.raw_log_indexer import RawLogIndexer
from scripts.utils.file_utils import read_json, write_json
from scripts.paths import ZephyrusPaths
from scripts.core.core import ZephyrusLoggerCore  # 🔥 Real core used here
import json


def make_test_indexer(encoding_offset=0.1):
    config = get_effective_config()
    paths = ZephyrusPaths.from_config(config)

    with patch("scripts.indexers.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array(
            [[i + encoding_offset for i in range(384)] for _ in texts]
        )

        return BaseIndexer(paths=paths, index_name="summary")


def make_summary_indexer(embedding_offset=0.1):
    config = get_effective_config()
    paths = ZephyrusPaths.from_config(config)

    with patch("scripts.indexers.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array(
            [[i + embedding_offset for i in range(384)] for _ in texts]
        )

        return SummaryIndexer(paths=paths, autoload=False)



def make_raw_indexer(embedding_offset=0.1):
    config = get_effective_config()
    paths = ZephyrusPaths.from_config(config)

    with patch("scripts.indexers.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array(
            [[i + embedding_offset for i in range(384)] for _ in texts]
        )

        return RawLogIndexer(paths=paths, autoload=False)



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


def assert_resolved_test_path(config: dict, key: str, expected_suffix: str):
    value = config.get(key)
    assert value is not None, f"Missing key: {key}"
    assert expected_suffix in value.replace("\\", "/"), f"{key} should include {expected_suffix}, got: {value}"
    assert "pytest" in value or "tmp" in value.lower(), f"{key} should point to test path, got: {value}"


def make_fake_paths(temp_dir: Path) -> ZephyrusPaths:
    from scripts.config.config_manager import ConfigManager
    ConfigManager.reset()
    ConfigManager.load_config()
    return ZephyrusPaths.from_config(temp_dir)


def make_dummy_logger_core(script_dir=None):
    from scripts.config.config_manager import ConfigManager
    ConfigManager.reset()
    ConfigManager.load_config()
    return ZephyrusLoggerCore(script_dir=script_dir or ".")


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
