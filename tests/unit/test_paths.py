import pytest
from pathlib import Path
from scripts.paths import ZephyrusPaths

pytestmark = [pytest.mark.unit]


@pytest.fixture
def test_paths_config(tmp_path, monkeypatch):
    """
    Unit tests for verifying ZephyrusPaths path resolution in test mode.

    Includes a fixture to mock configuration and tests that ensure all paths are correctly set
    according to test-specific configuration values when test_mode is enabled.
    """
    # Create a test configuration where test_mode is True.
    config = {
        "test_mode": True,
        "test_logs_dir": str(tmp_path / "logs"),
        "test_export_dir": str(tmp_path / "exports"),
        "test_vector_store_dir": str(tmp_path / "vector_store"),
        "logs_dir": str(tmp_path / "logs"),
        "export_dir": str(tmp_path / "exports"),
        "vector_store_dir": str(tmp_path / "vector_store"),
        "correction_summaries_path": str(tmp_path / "logs" / "correction_summaries.json"),
        "raw_log_path": str(tmp_path / "logs" / "zephyrus_log.json"),
    }
    monkeypatch.setattr("scripts.config.config_loader.load_config", lambda config_path=None: config)
    monkeypatch.setattr(
        "scripts.config.config_loader.get_absolute_path", lambda rel: str(Path(rel))
    )
    return config


def test_paths_in_test_mode(test_paths_config, tmp_path):
    """
    Unit tests for ZephyrusPaths path resolution in test mode.

    Provides a fixture to mock configuration values and verifies that all resolved paths
    match the expected test-specific directories and files when test_mode is enabled.
    """
    zp = ZephyrusPaths.from_config(tmp_path)
    # Since test_mode is True, the paths should be derived from the test_* keys.
    assert str(tmp_path / "logs") == str(zp.log_dir)
    assert str(tmp_path / "exports") == str(zp.export_dir)
    # Check that txt_log_file and correction_summaries_file reside in the logs directory.
    assert str(zp.txt_log_file).startswith(str(tmp_path / "logs"))
    assert str(zp.correction_summaries_file).startswith(str(tmp_path / "logs"))
