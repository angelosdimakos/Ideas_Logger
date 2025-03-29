import pytest
import json
from pathlib import Path
from tests.test_utils import make_summary_indexer

def test_load_entries_empty(tmp_path):
    """
    Tests that the `load_entries` method handles empty summaries files correctly.

    The test creates a temporary summaries file and writes an empty JSON object to it.
    It then checks that the `load_entries` method correctly returns empty lists for the
    texts and metadata.
    """
    indexer = make_summary_indexer()
    empty_file = Path(indexer.summaries_path)
    empty_file.parent.mkdir(parents=True, exist_ok=True)
    empty_file.write_text("{}", encoding="utf-8")

    texts, meta = indexer.load_entries()
    assert texts == []
    assert meta == []

def test_process_batches(tmp_path):
    """
    Tests that the indexer can correctly process batches in the summaries
    file.

    The test creates a temporary summaries file with two batches, each
    containing a single summary. The test then checks that the indexer loads
    the data correctly and that the metadata is correctly extracted.
    """
    indexer = make_summary_indexer()
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
    file = Path(indexer.summaries_path)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(test_data), encoding="utf-8")

    texts, meta = indexer.load_entries()
    assert len(texts) == 2
    assert texts[0] == "Test summary one."
    assert texts[1] == "Test summary two."
    assert meta[0]["main_category"] == "TestCategory"
    assert meta[0]["subcategory"] == "SubTest"
    assert meta[0]["date"] == "2025-03-23"

def test_build_index_and_search():
    """Tests that `SummaryIndexer.build_index` and `SummaryIndexer.search` work together as expected."""
    indexer = make_summary_indexer()
    texts = ["This is a summary about AI", "Another summary about creative ops"]
    metadata = [{"tag": "AI"}, {"tag": "creative"}]

    assert indexer.build_index(texts, metadata)
    results = indexer.search("AI", top_k=1)
    assert isinstance(results, list)
    assert results[0]["tag"] == "AI"
    assert "similarity" in results[0]
    indexer = make_summary_indexer()
    texts = ["This is a summary about AI", "Another summary about creative ops"]
    metadata = [{"tag": "AI"}, {"tag": "creative"}]

    assert indexer.build_index(texts, metadata)
    results = indexer.search("AI", top_k=1)
    assert isinstance(results, list)
    assert results[0]["tag"] == "AI"
    assert "similarity" in results[0]
