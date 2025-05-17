import pytest
from unittest.mock import MagicMock
from scripts.gui.gui_controller import GUIController


@pytest.fixture
def dummy_core():
    # Create a dummy core with stubbed methods.
    core = MagicMock()
    core.log_new_entry.return_value = "Logged!"
    core.force_summary_all.return_value = "Summarized!"
    core.search_summaries.return_value = "Summary Results!"
    core.search_raw_logs.return_value = "Raw Log Results!"
    return core


def test_log_entry_delegation(dummy_core):
    controller = GUIController(logger_core=dummy_core)
    result = controller.log_entry("Cat", "Sub", "Test Text")
    dummy_core.log_new_entry.assert_called_once_with("Cat", "Sub", "Test Text")
    assert result == "Logged!"


def test_force_summarize_all_delegation(dummy_core):
    controller = GUIController(logger_core=dummy_core)
    result = controller.force_summarize_all()
    dummy_core.force_summary_all.assert_called_once()
    assert result == "Summarized!"


def test_search_summaries_delegation(dummy_core):
    controller = GUIController(logger_core=dummy_core)
    result = controller.search_summaries("query")
    dummy_core.search_summaries.assert_called_once_with("query")
    assert result == "Summary Results!"


def test_search_raw_logs_delegation(dummy_core):
    controller = GUIController(logger_core=dummy_core)
    result = controller.search_raw_logs("query")
    dummy_core.search_raw_logs.assert_called_once_with("query")
    assert result == "Raw Log Results!"

def test_rebuild_tracker_validates_true(dummy_core):
    dummy_core.summary_tracker.validate.return_value = True
    controller = GUIController(logger_core=dummy_core)
    result = controller.rebuild_tracker()
    dummy_core.summary_tracker.rebuild.assert_called_once()
    dummy_core.summary_tracker.validate.assert_called_once()
    assert result is True


def test_get_tracker_status_valid(dummy_core):
    dummy_core.summary_tracker.validate.return_value = True
    controller = GUIController(logger_core=dummy_core)
    status = controller.get_tracker_status()
    assert status == "✅ Valid"


def test_get_tracker_status_invalid(dummy_core):
    dummy_core.summary_tracker.validate.return_value = False
    controller = GUIController(logger_core=dummy_core)
    status = controller.get_tracker_status()
    assert status == "❌ Invalid"


def test_get_coverage_data(dummy_core):
    dummy_core.summary_tracker.get_coverage_data.return_value = {"coverage": "data"}
    controller = GUIController(logger_core=dummy_core)
    result = controller.get_coverage_data()
    dummy_core.summary_tracker.get_coverage_data.assert_called_once()
    assert result == {"coverage": "data"}


def test_get_logs_reads_file(tmp_path, dummy_core):
    # Setup a dummy log file
    dummy_log_file = tmp_path / "dummy_log.txt"
    dummy_log_file.write_text("Log content here")

    dummy_core.paths.txt_log_file = str(dummy_log_file)
    controller = GUIController(logger_core=dummy_core)

    log_data = controller.get_logs()
    assert log_data == "Log content here"

