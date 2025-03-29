
import numpy as np
from unittest.mock import patch
from scripts.base_indexer import BaseIndexer
from scripts.config_loader import get_effective_config, get_config_value
from scripts.summary_indexer import SummaryIndexer
import json
from pathlib import Path

def make_test_indexer(encoding_offset=0.1):
    """
    Creates a test instance of a BaseIndexer, overriding the SentenceTransformer
    model with a mock that generates a simple incremental encoding for each text.
    Args:
        encoding_offset (float): The value to add to each encoding element.
            Defaults to 0.1.
    Returns:
        BaseIndexer: A test instance of BaseIndexer, with mocked SentenceTransformer
            model.
    """
    config = get_effective_config()

    with patch("scripts.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array([[i + encoding_offset for i in range(384)] for _ in texts])

        return BaseIndexer(
            summaries_path=get_config_value(config, "correction_summaries_path", ""),
            index_path=get_config_value(config, "faiss_index_path", ""),
            metadata_path=get_config_value(config, "faiss_metadata_path", "")
        )
    config = get_effective_config()

    with patch("scripts.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array([[i + encoding_offset for i in range(384)] for _ in texts])

        return BaseIndexer(
            summaries_path=get_config_value(config, "correction_summaries_path", ""),
            index_path=get_config_value(config, "faiss_index_path", ""),
            metadata_path=get_config_value(config, "faiss_metadata_path", "")
        )
def assert_resolved_test_path(config: dict, key: str, expected_suffix: str):

    """
    Asserts that a specific configuration path resolves to a test path.

    This function retrieves a value from the configuration dictionary using
    the provided key and checks the following conditions:
    - The value must not be None.
    - The value must include the expected suffix.
    - The value must point to a test path, either containing 'pytest' or
      having 'tmp' in its lowercase representation.

    Args:
        config (dict): The configuration dictionary containing paths.
        key (str): The key in the config dictionary to retrieve the path.
        expected_suffix (str): The suffix expected to be present in the path.

    Raises:
        AssertionError: If any of the conditions are not met.
    """
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
    """
    Creates a dummy AISummarizer instance for testing purposes.

    This function returns an instance of a mock class that mimics the behavior
    of an AISummarizer. It provides methods for summarizing entries in bulk
    and generating a fallback summary. The behavior of these methods can be
    controlled through the function's parameters.

    Args:
        success (bool): Determines if the summarization should succeed or
                        simulate a failure. Defaults to True.
        fallback_response (str): The response to return when the fallback
                                 summary method is called. Defaults to
                                 "Fallback summary.".

    Returns:
        Dummy: An instance of a dummy summarizer class with methods
               `summarize_entries_bulk` and `_fallback_summary`.
    """
    class Dummy:
        def summarize_entries_bulk(self, entries, subcategory=None):
            if not success:
                raise Exception("Simulated failure")
            return [f"Summary: {e['content']}" for e in entries]
        def _fallback_summary(self, full_prompt):
            return fallback_response
    return Dummy()

def assert_summary_structure(summaries: dict, category: str, subcat: str):
    """
    Asserts that the specified summary structure is present in the summaries dictionary.

    This function checks if the "global" key is present in the summaries dictionary,
    and within "global", it verifies the presence of the specified category and subcategory.

    Args:
        summaries (dict): The dictionary containing summary data.
        category (str): The main category to check within the "global" key.
        subcat (str): The subcategory to check within the specified category.

    Raises:
        AssertionError: If the expected structure is not present in the summaries.
    """
    assert "global" in summaries
    assert category in summaries["global"]
    assert subcat in summaries["global"][category]
    assert "global" in summaries
    assert category in summaries["global"]
    assert subcat in summaries["global"][category]



def make_raw_indexer(embedding_offset=0.1):
    """
    Creates a test instance of a BaseIndexer, overriding the SentenceTransformer model
    with a mock that generates a simple incremental encoding for each text.

    Args:
        embedding_offset (float): The value to add to each embedding element.
            Defaults to 0.1.

    Returns:
        BaseIndexer: A test instance of BaseIndexer, with mocked SentenceTransformer
            model.
    """
    config = get_effective_config()

    with patch("scripts.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array([[i + embedding_offset for i in range(384)] for _ in texts])

        return BaseIndexer(
            summaries_path=get_config_value(config, "raw_log_path", ""),
            index_path=get_config_value(config, "raw_log_index_path", ""),
            metadata_path=get_config_value(config, "raw_log_metadata_path", "")
        )

def make_summary_indexer(embedding_offset=0.1):
    """
    Creates a test instance of a SummaryIndexer, overriding the SentenceTransformer model
    with a mock that generates a simple incremental encoding for each text.

    Args:
        embedding_offset (float): The value to add to each embedding element.
            Defaults to 0.1.

    Returns:
        BaseIndexer: A test instance of BaseIndexer, with mocked SentenceTransformer
            model.
    """
    config = get_effective_config()

    with patch("scripts.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array([[i + embedding_offset for i in range(384)] for _ in texts])

        return SummaryIndexer(
            summaries_path=get_config_value(config, "correction_summaries_path", ""),
            index_path=get_config_value(config, "faiss_index_path", ""),
            metadata_path=get_config_value(config, "faiss_metadata_path", "")
        )

def assert_faiss_index_built(indexer, expected_len: int = None):
    """
    Asserts that a FAISS index has been built by checking for the presence of
    the index and metadata in the indexer instance.

    Args:
        indexer (scripts.base_indexer.BaseIndexer): The indexer instance to check.
        expected_len (int): If provided, the expected length of the metadata list.

    Raises:
        AssertionError: If the index or metadata is missing, or if the length of
            the metadata list does not match the expected length.
    """
    assert indexer.index is not None, "FAISS index is missing"
    assert isinstance(indexer.metadata, list), "Metadata must be a list"
    if expected_len is not None:
        assert len(indexer.metadata) == expected_len, f"Expected {expected_len} metadata items, got {len(indexer.metadata)}"

def assert_search_result(results: list, expected_tag=None):
    """
    Asserts that the search result is as expected.

    Args:
        results (list): The search result.
        expected_tag (str): The expected tag of the first result.

    Raises:
        AssertionError: If the search result is not a list, or if it is empty, or if the first result is missing the "similarity" key, or if the first result has a tag that does not match the expected tag.
    """
    assert isinstance(results, list), "Search result must be a list"
    assert len(results) > 0, "Search returned no results"
    assert "similarity" in results[0], "Search result missing similarity"
    if expected_tag:
        assert results[0].get("tag") == expected_tag, f"Expected tag '{expected_tag}', got '{results[0].get('tag')}'"
    assert isinstance(results, list), "Search result must be a list"
    assert len(results) > 0, "Search returned no results"
    assert "similarity" in results[0], "Search result missing similarity"
    if expected_tag:
        assert results[0].get("tag") == expected_tag, f"Expected tag '{expected_tag}', got '{results[0].get('tag')}'"

def make_dummy_logger_core():
    """
    Creates and returns a mock implementation of a logger core.

    The returned `DummyLoggerCore` class provides dummy methods to simulate logging
    operations, such as saving entries and generating summaries, for use in testing
    environments. It also provides a property to access a mock JSON log file path.

    Returns:
        DummyLoggerCore: An instance of a mock logger core with basic logging functionality.
    """
    from pathlib import Path
    class DummyLoggerCore:
        def save_entry(self, main_cat, subcat, entry): return True
        def generate_summary(self, date, main_cat, subcat): return True
        @property
        def json_log_file(self): return Path("tests/mock_data/mock_log.json")
    return DummyLoggerCore()

def write_json(path: Path, data: dict):
    """
    Writes a JSON file at the given path with the given data.

    Args:
        path (Path): The path to the JSON file to write.
        data (dict): The data to write to the JSON file.

    """
    path.write_text(json.dumps(data, indent=2))
    path.write_text(json.dumps(data, indent=2))

def toggle_test_mode(flag: bool):
    """
    Enables or disables test mode for the logger by setting the "test_mode" config option.

    Args:
        flag (bool): Whether to enable (True) or disable (False) test mode.

    """
    from utils.file_utils import read_json, write_json
    config_path = "config.json"
    config = read_json(config_path)
    config["test_mode"] = flag
    write_json(config_path, config)

def reset_logger_state(logger_core):
    """
    Resets the state of the logger by clearing the contents of related log files.

    This function iterates over the logger's JSON log file, summary tracker file, and
    correction summaries file, and clears their contents by writing an empty JSON
    object ("{}") to each file, if they exist.

    Args:
        logger_core: An instance of a logger core containing references to the
                     log files that need to be reset.
    """
    for path in [
        logger_core.json_log_file,
        logger_core.summary_tracker_file,
        logger_core.correction_summaries_file
    ]:
        if path.exists():
            path.write_text("{}", encoding="utf-8")
    for path in [
        logger_core.json_log_file,
        logger_core.summary_tracker_file,
        logger_core.correction_summaries_file
    ]:
        if path.exists():
            path.write_text("{}", encoding="utf-8")

