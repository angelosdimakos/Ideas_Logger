from scripts.utils.file_utils import write_json, read_json
from scripts.core.log_manager import LogManager
import pytest
pytestmark = [pytest.mark.unit, pytest.mark.file_ops]


@pytest.fixture
def temp_log_files(tmp_path):
    json_log_file = tmp_path / "json_log.json"
    txt_log_file = tmp_path / "log.txt"
    correction_file = tmp_path / "correction.json"
    write_json(json_log_file, {})
    write_json(correction_file, {})
    txt_log_file.write_text("")
    return json_log_file, txt_log_file, correction_file

def test_append_entry(temp_log_files):
    json_log_file, txt_log_file, correction_file = temp_log_files
    lm = LogManager(json_log_file, txt_log_file, correction_file, "%Y-%m-%d %H:%M:%S", "content", "timestamp")
    date_str = "2025-03-29"
    lm.append_entry(date_str, "Cat", "Sub", "Test Entry")
    logs = read_json(json_log_file)
    assert date_str in logs
    assert "Cat" in logs[date_str]
    assert "Sub" in logs[date_str]["Cat"]
    assert len(logs[date_str]["Cat"]["Sub"]) == 1
    assert logs[date_str]["Cat"]["Sub"][0]["content"] == "Test Entry"

def test_update_correction_summaries(temp_log_files):
    json_log_file, txt_log_file, correction_file = temp_log_files
    lm = LogManager(json_log_file, txt_log_file, correction_file, "%Y-%m-%d %H:%M:%S", "content", "timestamp")
    new_data = {
        "batch": "test",
        "original_summary": "summary",
        "corrected_summary": "",
        "correction_timestamp": "timestamp",
        "start": "start",
        "end": "end"
    }
    lm.update_correction_summaries("Cat", "Sub", new_data)
    corrections = read_json(correction_file)
    assert "global" in corrections
    assert "Cat" in corrections["global"]
    assert "Sub" in corrections["global"]["Cat"]
    assert corrections["global"]["Cat"]["Sub"][0]["batch"] == "test"

def test_get_unsummarized_batch(temp_log_files):
    json_log_file, txt_log_file, correction_file = temp_log_files
    # Prepare a log file with three entries.
    logs = {
        "2025-03-29": {
            "Cat": {
                "Sub": [
                    {"timestamp": "2025-03-29 12:00:00", "content": "Entry 1"},
                    {"timestamp": "2025-03-29 12:05:00", "content": "Entry 2"},
                    {"timestamp": "2025-03-29 12:10:00", "content": "Entry 3"}
                ]
            }
        }
    }
    write_json(json_log_file, logs)
    lm = LogManager(json_log_file, txt_log_file, correction_file, "%Y-%m-%d %H:%M:%S", "content", "timestamp")
    # Assume summarized_total is 1 and we want a batch of 2.
    batch = lm.get_unsummarized_batch("Cat", "Sub", summarized_total=1, batch_size=2)
    assert len(batch) == 2
    assert batch[0]["content"] == "Entry 2"
    assert batch[1]["content"] == "Entry 3"
