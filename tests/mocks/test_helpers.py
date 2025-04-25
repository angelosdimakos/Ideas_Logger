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
import pytest
import tkinter as tk


def skip_if_no_display():
    """
    Skips the current test if no GUI display is available.

    Attempts to create and destroy a Tkinter root window. If this fails due to lack of GUI support,
    the test is skipped using pytest.skip.

    Raises:
        pytest.skip: If the environment does not support GUI operations.
    """
    try:
        root = tk.Tk()
        root.withdraw()
        root.update_idletasks()
        root.destroy()
    except (tk.TclError, RuntimeError):
        pytest.skip("🛑 Skipping GUI test — no GUI support available")


def make_test_indexer(encoding_offset=0.1):
    """
    Creates a BaseIndexer instance with a mocked SentenceTransformer for testing.

    The mock embedding model returns deterministic embeddings with a specified offset.

    Args:
        encoding_offset (float): Value to add to each embedding dimension for test determinism.

    Returns:
        BaseIndexer: A BaseIndexer instance with a mocked embedding model.
    """

    config = get_effective_config()
    paths = ZephyrusPaths.from_config(config)

    with patch("scripts.indexers.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array(
            [[i + encoding_offset for i in range(384)] for _ in texts]
        )

        return BaseIndexer(paths=paths, index_name="summary")


def make_summary_indexer(paths: ZephyrusPaths, embedding_offset=0.1):
    """
    Creates a SummaryIndexer instance with a mocked SentenceTransformer for testing.

    Args:
        paths (ZephyrusPaths): The ZephyrusPaths instance to use.
        embedding_offset (float): Value to add to each embedding dimension for test determinism.

    Returns:
        SummaryIndexer: A SummaryIndexer instance with a mocked embedding model.
    """
    with patch("scripts.indexers.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array(
            [[i + embedding_offset for i in range(384)] for _ in texts]
        )

        return SummaryIndexer(paths=paths, autoload=False)


def make_raw_indexer(paths: ZephyrusPaths, embedding_offset=0.1):
    """
    Creates a RawLogIndexer instance with a mocked SentenceTransformer for testing.

    Args:
        paths (ZephyrusPaths): The ZephyrusPaths instance to use.
        embedding_offset (float): Value to add to each embedding dimension for test determinism.

    Returns:
        RawLogIndexer: A RawLogIndexer instance with a mocked embedding model.
    """
    with patch("scripts.indexers.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array(
            [[i + embedding_offset for i in range(384)] for _ in texts]
        )

        return RawLogIndexer(paths=paths, autoload=False)


def make_fake_logs(date_str: str, category: str, subcat: str, count: int = 5):
    """
    Generates a fake log dictionary for testing purposes.

    Args:
        date_str (str): The date string for the log entries.
        category (str): The main category name.
        subcat (str): The subcategory name.
        count (int): Number of entries to generate.

    Returns:
        dict: A nested dictionary representing fake log data.
    """
    return {
        date_str: {
            category: {
                subcat: [
                    {"timestamp": f"{date_str} 10:{i:02d}:00", "content": f"entry {i}"}
                    for i in range(count)
                ]
            }
        }
    }


def make_dummy_aisummarizer(success=True, fallback_response="Fallback summary."):
    """
    Creates a dummy AI summarizer object for testing summarization logic.

    Args:
        success (bool): If False, summarize_entries_bulk will raise an Exception.
        fallback_response (str): The response to return from _fallback_summary.

    Returns:
        object: A dummy summarizer with summarize_entries_bulk and _fallback_summary methods.
    """

    class Dummy:
        def summarize_entries_bulk(self, entries, subcategory=None):
            if not success:
                raise Exception("Simulated failure")
            return "\n".join(
                [
                    f"Summary: {e['content']}" if isinstance(e, dict) else f"Summary: {str(e)}"
                    for e in entries
                ]
            )

        def _fallback_summary(self, full_prompt):
            return fallback_response

    return Dummy()


def assert_summary_structure(summaries: dict, category: str, subcat: str):
    """
    Asserts that the summaries dictionary has the expected structure for a given category and subcategory.

    Args:
        summaries (dict): The summaries dictionary to check.
        category (str): The main category expected in the summaries.
        subcat (str): The subcategory expected in the summaries.

    Raises:
        AssertionError: If the expected structure is not present.
    """
    assert "global" in summaries
    assert category in summaries["global"]
    assert subcat in summaries["global"][category]


def assert_resolved_test_path(config: dict, key: str, expected_suffix: str):
    """
    Asserts that a config path value contains the expected suffix and points to a test path.

    Args:
        config (dict): The configuration dictionary.
        key (str): The key to check in the config.
        expected_suffix (str): The expected suffix in the path.

    Raises:
        AssertionError: If the path does not meet expectations.
    """
    value = config.get(key)
    assert value is not None, f"Missing key: {key}"
    assert expected_suffix in value.replace(
        "\\", "/"
    ), f"{key} should include {expected_suffix}, got: {value}"
    assert (
        "pytest" in value or "tmp" in value.lower()
    ), f"{key} should point to test path, got: {value}"


def make_fake_paths(temp_dir: Path) -> ZephyrusPaths:
    """
    Creates a ZephyrusPaths instance for a temporary directory, resetting the config manager.

    Args:
        temp_dir (Path): The temporary directory to use as the script directory.

    Returns:
        ZephyrusPaths: The resolved ZephyrusPaths instance.
    """
    from scripts.config.config_manager import ConfigManager

    ConfigManager.reset()
    ConfigManager.load_config()
    return ZephyrusPaths.from_config(temp_dir)


def make_dummy_logger_core(script_dir=None):
    """
    Creates a ZephyrusLoggerCore instance for testing, resetting the config manager.

    Args:
        script_dir (str or Path, optional): The script directory to use. Defaults to current directory.

    Returns:
        ZephyrusLoggerCore: The logger core instance.
    """
    from scripts.config.config_manager import ConfigManager

    ConfigManager.reset()
    ConfigManager.load_config()
    return ZephyrusLoggerCore(script_dir=script_dir or ".")


def toggle_test_mode(flag: bool):
    """
    Toggles the 'test_mode' flag in the config.json file.

    Args:
        flag (bool): The value to set for 'test_mode'.
    """
    config_path = "config.json"
    config = read_json(config_path)
    config["test_mode"] = flag
    write_json(Path(config_path), config)


def reset_logger_state(logger_core):
    """
    Resets the state of the logger core by clearing relevant files.

    Args:
        logger_core: The ZephyrusLoggerCore instance whose files should be reset.
    """
    for path in [
        logger_core.json_log_file,
        logger_core.summary_tracker_file,
        logger_core.correction_summaries_file,
    ]:
        if path.exists():
            path.write_text("{}", encoding="utf-8")


def count_lines(path: str) -> int:
    """
    Counts the number of lines in a file.

    Args:
        path (str): The path to the file.

    Returns:
        int: The number of lines in the file.
    """
    with open(path, "r") as f:
        return sum(1 for _ in f)


def mock_refactor_data(methods=3, files=2):
    """
    Generates mock data for refactoring tests.

    Args:
        methods (int): Number of methods per file.
        files (int): Number of files.

    Returns:
        dict: Mock data structured by file and method.
    """
    return {
        f"scripts/module_{i}/file.py": {
            "complexity": {f"method_{j}": {"score": j * 5} for j in range(methods)}
        }
        for i in range(files)
    }


def create_temp_file_with_content(tmp_path, content):
    """
    Creates a temporary file with the given content.

    Args:
        tmp_path (Path): The temporary directory to create the file in.
        content (str): The content to write to the file.

    Returns:
        Path: The path to the created file.
    """
    path = tmp_path / "test.txt"
    path.write_text(content, encoding="utf-8")
    return path
