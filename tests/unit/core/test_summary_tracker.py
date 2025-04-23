from scripts.utils.file_utils import write_json
from scripts.core.summary_tracker import SummaryTracker
from scripts.paths import ZephyrusPaths
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
                    {"timestamp": "2025-03-29 12:05:00", "content": "Entry 2"},
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


def test_rebuild_summary_tracker(sample_logs, tmp_path):
    """
    Unit tests for the SummaryTracker class, verifying correct rebuild and update behavior.

    Includes fixtures for creating sample log and tracker files, and tests that:
    - Rebuilding the tracker correctly counts logged entries and initializes summarized totals.
    - Updating the tracker correctly increments logged and summarized totals.

    Uses ZephyrusPaths for path management and organization-specific file utilities.
    """
    log_file, logs = sample_logs
    # Create a ZephyrusPaths instance using tmp_path as the base.
    paths = ZephyrusPaths.from_config(tmp_path)
    # Override paths for testing: use our tracker_file and sample log_file.
    paths.summary_tracker_file = tmp_path / "tracker.json"
    paths.json_log_file = log_file
    tracker = SummaryTracker(paths)
    tracker.rebuild()
    # Expect logged_total to equal the number of entries.
    assert tracker.tracker["TestCategory"]["SubCategory"]["logged_total"] == 2
    # summarized_total remains 0 after rebuild.
    assert tracker.tracker["TestCategory"]["SubCategory"]["summarized_total"] == 0


def test_update_summary_tracker(tracker_file, tmp_path):
    """
    Unit tests for the SummaryTracker class, ensuring correct rebuild and update functionality.

    Includes fixtures for creating sample log and tracker files, and tests that:
    - Rebuilding the tracker accurately counts logged entries and initializes summarized totals.
    - Updating the tracker properly increments logged and summarized totals.

    Utilizes ZephyrusPaths for path management and organization-specific file utilities.
    """
    from pathlib import Path

    # Create a ZephyrusPaths instance from tmp_path.
    paths = ZephyrusPaths.from_config(tmp_path)
    # Override with our test tracker file and a dummy json_log_file.
    paths.summary_tracker_file = tracker_file
    paths.json_log_file = tmp_path / "dummy.json"
    # Write dummy JSON for dummy.json (required by rebuild/update if needed).
    write_json(paths.json_log_file, {})
    tracker = SummaryTracker(paths)
    # Pre-populate tracker state.
    tracker.tracker = {"Cat": {"Sub": {"logged_total": 3, "summarized_total": 1}}}
    tracker.update("Cat", "Sub", new_entries=2, summarized=1)
    assert tracker.tracker["Cat"]["Sub"]["logged_total"] == 5
    assert tracker.tracker["Cat"]["Sub"]["summarized_total"] == 2
