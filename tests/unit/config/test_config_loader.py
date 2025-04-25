import os
import json
import unittest
from scripts.config.config_loader import load_config, get_config_value, get_absolute_path
import pytest

pytestmark = [pytest.mark.unit]


class TestConfigLoader(unittest.TestCase):
    """
    Test suite for verifying the configuration loading and path resolution logic
    defined in `scripts.config_loader`. Uses mock directories to avoid impacting production data.
    """

    def setUp(self):
        """
        Set up a temporary testing environment:
        - Creates a mock `config` directory and JSON config file inside `tests/mock_data/`.
        - Overrides `BASE_DIR` and `CONFIG_DIR` for testing isolation.
        - Defines a local version of `get_absolute_path` for validation.
        """
        self.mock_data_dir = os.path.join(os.path.dirname(__file__), "mock_data")
        self.mock_logs_dir = os.path.join(self.mock_data_dir, "logs")
        self.mock_exports_dir = os.path.join(self.mock_data_dir, "exports")

        # Create necessary directories
        os.makedirs(self.mock_logs_dir, exist_ok=True)
        os.makedirs(self.mock_exports_dir, exist_ok=True)

        self.config_file = os.path.join(self.mock_data_dir, "config.json")
        sample_config = {
            "batch_size": 10,
            "correction_summaries_path": "logs/test_correction_summaries.json",
            "test_mode": True,
        }
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(sample_config, f)

        # Overriding `get_absolute_path` for the test context
        self.original_get_absolute_path = get_absolute_path

        def test_get_absolute_path(relative_path):
            """
            Mocks path resolution for the test environment, pointing to mock directories.
            """
            return os.path.join(self.mock_data_dir, relative_path)

        self.test_get_absolute_path = test_get_absolute_path

    def tearDown(self):
        """
        Clean up files inside the test directories but leave the directories intact for future tests.
        """
        # Remove files inside the mock_data/logs and mock_data/exports to avoid directory errors
        try:
            for root, dirs, files in os.walk(self.mock_data_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))  # Delete files inside the mock_data dir
        except Exception as e:
            print(f"[WARNING] Failed to clean up files: {e}")

    # Optionally, you can add more logic to clean specific files or subdirectories if needed.
    def test_load_config_success(self):
        """
        Validates that the config file loads successfully from the mock location and matches the expected structure.
        """
        config = load_config(self.config_file)
        self.assertIsInstance(config, dict)
        self.assertEqual(config.get("batch_size"), 10)
        self.assertEqual(
            config.get("correction_summaries_path"), "logs/test_correction_summaries.json"
        )

    def test_get_config_value(self):
        """
        Ensures that `get_config_value`:
        - Retrieves an existing key correctly.
        - Returns the default value if the key is missing.
        """
        config = load_config(self.config_file)
        self.assertEqual(get_config_value(config, "batch_size", 5), 10)
        self.assertEqual(get_config_value(config, "nonexistent_key", "default_val"), "default_val")

    def test_get_absolute_path(self):
        """
        Validates that the test version of `get_absolute_path` joins relative paths with the mock base directory.
        """
        abs_path = self.test_get_absolute_path("logs/test.json")
        expected = os.path.join(self.mock_data_dir, "logs/test.json")
        self.assertEqual(abs_path, expected)

    def test_load_config_missing_file(self):
        """
        Ensures `load_config` gracefully returns an empty dictionary when the config file is missing.
        """
        fake_path = os.path.join(self.mock_data_dir, "fake_config.json")
        config = load_config(fake_path)
        self.assertEqual(config, {})

    def test_get_effective_config_test_mode_paths(self):
        """
        Validates that `get_effective_config` overrides production paths with test paths
        when `test_mode` is True.
        """
        from scripts.config.config_loader import get_effective_config
        from tests.mocks.test_helpers import assert_resolved_test_path

        config_override = {
            "test_mode": True,
            "test_logs_dir": "tests/mock_data/logs",
            "test_export_dir": "tests/mock_data/exports",
            "test_vector_store_dir": "tests/mock_data/vector_store",
        }

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config_override, f)

        config = get_effective_config(self.config_file)

        assert_resolved_test_path(config, "logs_dir", "logs")
        assert_resolved_test_path(config, "export_dir", "exports")
        assert_resolved_test_path(config, "vector_store_dir", "vector_store")


if __name__ == "__main__":
    unittest.main()
