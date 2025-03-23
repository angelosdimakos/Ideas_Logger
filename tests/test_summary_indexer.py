# tests/test_summary_indexer.py

import os
import pytest
import json
from pathlib import Path
from unittest.mock import patch
from scripts.summary_indexer import SummaryIndexer
import numpy as np

# Define the constants at module level.
MOCK_INDEX_PATH = "tests/mock_data/vector_store/test_summary_index.faiss"
MOCK_METADATA_PATH = "tests/mock_data/vector_store/test_summary_metadata.pkl"
MOCK_SUMMARIES_PATH = "tests/mock_data/logs/test_summaries.json"

@pytest.fixture
def summary_indexer(tmp_path, monkeypatch):
    # Compute absolute paths based on tmp_path.
    abs_index_path = str(tmp_path / MOCK_INDEX_PATH)
    abs_metadata_path = str(tmp_path / MOCK_METADATA_PATH)
    abs_summaries_path = str(tmp_path / MOCK_SUMMARIES_PATH)

    # Ensure the parent directories exist.
    Path(abs_summaries_path).parent.mkdir(parents=True, exist_ok=True)
    Path(abs_index_path).parent.mkdir(parents=True, exist_ok=True)
    Path(abs_metadata_path).parent.mkdir(parents=True, exist_ok=True)

    # Patch load_config to return test-specific absolute paths.
    monkeypatch.setattr("scripts.config_loader.load_config", lambda config_path=None: {
        "embedding_model": "all-MiniLM-L6-v2",
        "batch_size": 5,
        "correction_summaries_path": abs_summaries_path,
        "faiss_index_path": abs_index_path,
        "faiss_metadata_path": abs_metadata_path,
        "logs_dir": str(tmp_path / "tests/mock_data/logs"),
        "export_dir": str(tmp_path / "tests/mock_data/exports"),
        "test_mode": True
    })

    # Patch SentenceTransformer in base_indexer for deterministic embeddings.
    with patch("scripts.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array([[i + 0.1 for i in range(384)] for _ in texts])
        indexer = SummaryIndexer(
            summaries_path=abs_summaries_path,
            index_path=abs_index_path,
            metadata_path=abs_metadata_path
        )
        yield indexer

def test_load_entries_empty(summary_indexer, tmp_path):
    # Create an empty summaries file.
    empty_file = Path(summary_indexer.summaries_path)
    empty_file.parent.mkdir(parents=True, exist_ok=True)
    empty_file.write_text("{}", encoding="utf-8")
    
    texts, meta = summary_indexer.load_entries()
    assert texts == []
    assert meta == []

def test_process_batches(summary_indexer, tmp_path):
    # Create a sample summaries JSON structure.
    test_data = {
        "2025-03-23": {
            "TestCategory": {
                "SubTest": [
                    {
                        "batch": "1-2",
                        "original_summary": "Test summary one.",
                        "corrected_summary": "",
                        "correction_timestamp": "2025-03-23 10:00:00"
                    },
                    {
                        "batch": "3-4",
                        "original_summary": "Test summary two.",
                        "corrected_summary": "",
                        "correction_timestamp": "2025-03-23 10:05:00"
                    }
                ]
            }
        }
    }
    summaries_file = Path(summary_indexer.summaries_path)
    summaries_file.parent.mkdir(parents=True, exist_ok=True)
    summaries_file.write_text(json.dumps(test_data), encoding="utf-8")

    # Reload entries from the test data.
    texts, meta = summary_indexer.load_entries()
    assert len(texts) == 2, f"Expected 2 texts, got {len(texts)}"
    assert texts[0] == "Test summary one."
    assert texts[1] == "Test summary two."
    # Verify metadata structure.
    assert meta[0]["main_category"] == "TestCategory"
    assert meta[0]["subcategory"] == "SubTest"
    assert meta[0]["date"] == "2025-03-23"

def test_build_index_and_search(summary_indexer):
    # Build an index from the summaries.
    texts = ["This is a summary about AI", "Another summary about creative ops"]
    metadata = [{"tag": "AI"}, {"tag": "creative"}]
    result = summary_indexer.build_index(texts, metadata)
    assert result is True
    # Search for a query that should match the first summary.
    results = summary_indexer.search("AI", top_k=1)
    assert isinstance(results, list)
    # Check that we get at least one result with the expected metadata.
    assert results[0]["tag"] == "AI"
    assert "similarity" in results[0]
