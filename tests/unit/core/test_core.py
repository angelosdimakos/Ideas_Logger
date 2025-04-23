from scripts.utils.file_utils import read_json
from scripts.core.core import ZephyrusLoggerCore
import pytest

pytestmark = [pytest.mark.unit]


@pytest.fixture(scope="function")
def logger_core(temp_dir):
    """
    Creates a ZephyrusLoggerCore instance (from the refactored module)
    with temp_dir as the script directory.
    """
    return ZephyrusLoggerCore(script_dir=temp_dir)


@pytest.fixture
def core_instance(logger_core):
    # Simply return the logger_core fixture (now a refactored core instance).
    return logger_core


def test_save_entry(core_instance):
    """
    Unit tests for ZephyrusLoggerCore, verifying entry saving and global summary generation.
    Includes fixtures for creating a temporary core instance and tests that ensure entries
    are correctly logged to both JSON and Markdown, and that summaries are generated as expected.
    """
    # Test that saving an entry updates both the JSON log and markdown export.
    result = core_instance.save_entry("TestCat", "TestSub", "Test entry content")
    assert result is True
    logs = read_json(core_instance.paths.json_log_file)
    # Expect at least one date key present.
    assert len(logs) > 0
    md_file = core_instance.paths.export_dir / "TestCat.md"
    assert md_file.exists()
    content = md_file.read_text(encoding="utf-8")
    assert "Test entry content" in content


def test_generate_global_summary(core_instance):
    """
    Unit tests for ZephyrusLoggerCore, including fixtures for creating a temporary core instance.
    Tests verify that entries are correctly saved to both JSON and Markdown, and that global summaries
    are generated as expected when the batch size is reached.
    """
    # Append enough entries to trigger summary generation.
    date_str = "2025-03-29"
    for _ in range(core_instance.BATCH_SIZE):
        core_instance.log_manager.append_entry(date_str, "TestCat", "TestSub", "Entry for summary")
        core_instance.summary_tracker.update("TestCat", "TestSub", new_entries=1)
    result = core_instance.generate_global_summary("TestCat", "TestSub")
    assert result is True
    corrections = read_json(core_instance.paths.correction_summaries_file)
    assert "global" in corrections
    assert "TestCat" in corrections["global"]
    assert "TestSub" in corrections["global"]["TestCat"]
