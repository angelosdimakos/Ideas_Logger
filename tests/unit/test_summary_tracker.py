from scripts.utils.file_utils import write_json
from scripts.core.summary_tracker import SummaryTracker
import pytest
pytestmark = [pytest.mark.unit]


@pytest.fixture
def sample_logs(tmp_path):
    # Create a sample log file with two entries.
    logs = {
        "2025-03-29": {
            "TestCategory": {
                "SubCategory": [
                    {"timestamp": "2025-03-29 12:00:00", "content": "Entry 1"},
                    {"timestamp": "2025-03-29 12:05:00", "content": "Entry 2"}
                ]
            }
        }
    }
    log_file = tmp_path / "logs.json"
    write_json(log_file, logs)
    return log_file, logs

@pytest.fixture
def tracker_file(tmp_path):
    tracker_file = tmp_path / "tracker.json"
    write_json(tracker_file, {})
    return tracker_file

def test_rebuild_summary_tracker(sample_logs, tracker_file):
    log_file, logs = sample_logs
    tracker = SummaryTracker(tracker_file, log_file)
    tracker.rebuild()
    # Expect logged_total to equal the number of entries.
    assert tracker.tracker["TestCategory"]["SubCategory"]["logged_total"] == 2
    # summarized_total remains 0 after rebuild.
    assert tracker.tracker["TestCategory"]["SubCategory"]["summarized_total"] == 0

def test_update_summary_tracker(tracker_file, tmp_path):
    # Initialize tracker with known counts.
    tracker = SummaryTracker(tracker_file, tmp_path / "dummy.json")
    tracker.tracker = {"Cat": {"Sub": {"logged_total": 3, "summarized_total": 1}}}
    tracker.update("Cat", "Sub", new_entries=2, summarized=1)
    assert tracker.tracker["Cat"]["Sub"]["logged_total"] == 5
    assert tracker.tracker["Cat"]["Sub"]["summarized_total"] == 2
