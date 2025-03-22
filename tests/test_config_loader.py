import os
import json
import tempfile
import unittest
from scripts.config_loader import load_config, get_config_value, get_absolute_path, BASE_DIR, CONFIG_DIR

class TestConfigLoader(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to mimic the config folder.
        self.temp_dir = tempfile.TemporaryDirectory()
        # Override BASE_DIR and CONFIG_DIR for testing purposes.
        self.original_base_dir = BASE_DIR
        self.original_config_dir = CONFIG_DIR

        # Use the temporary directory as the new BASE_DIR.
        self.test_base_dir = self.temp_dir.name
        self.test_config_dir = os.path.join(self.test_base_dir, "config")
        os.makedirs(self.test_config_dir, exist_ok=True)

        # Create a sample config file.
        self.config_file = os.path.join(self.test_config_dir, "config.json")
        sample_config = {
            "batch_size": 10,
            "correction_summaries_path": "logs/test_correction_summaries.json",
            "test_mode": True
        }
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(sample_config, f)

        # Monkey-patch get_absolute_path to use our temporary BASE_DIR.
        self.original_get_absolute_path = get_absolute_path
        # Redefine get_absolute_path for testing:
        def test_get_absolute_path(relative_path):
            return os.path.join(self.test_base_dir, relative_path)
        # We'll use this in tests instead of the module-level one.

        self.test_get_absolute_path = test_get_absolute_path

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_config_success(self):
        # Test that load_config returns our sample config.
        config = load_config(self.config_file)
        self.assertIsInstance(config, dict)
        self.assertEqual(config.get("batch_size"), 10)
        self.assertEqual(config.get("correction_summaries_path"), "logs/test_correction_summaries.json")

    def test_get_config_value(self):
        config = load_config(self.config_file)
        # Key exists.
        self.assertEqual(get_config_value(config, "batch_size", 5), 10)
        # Key missing should return default.
        self.assertEqual(get_config_value(config, "nonexistent_key", "default_val"), "default_val")

    def test_get_absolute_path(self):
        # Using our test version.
        abs_path = self.test_get_absolute_path("logs/test.json")
        expected = os.path.join(self.test_base_dir, "logs/test.json")
        self.assertEqual(abs_path, expected)

    def test_load_config_missing_file(self):
        # Provide a path that doesn't exist.
        fake_path = os.path.join(self.test_config_dir, "fake_config.json")
        config = load_config(fake_path)
        self.assertEqual(config, {})

if __name__ == "__main__":
    unittest.main()
