from scripts.config.config_manager import ConfigManager, AppConfig
import pytest

pytestmark = [pytest.mark.unit]


def test_config_manager_load_valid(temp_config_file):
    """
    Test that ConfigManager.load_config successfully loads a valid config file.

    Asserts:
        - The returned object is an instance of AppConfig.
        - The loaded config has expected values for mode, llm_model, and logs_dir.
    """
    ConfigManager.reset()
    config = ConfigManager.load_config(str(temp_config_file))
    assert isinstance(config, AppConfig)
    assert config.mode == "test"
    assert config.llm_model == "mistral"
    assert config.logs_dir.endswith("logs")


def test_config_manager_missing_file():
    """
    Test that loading a non-existent config file returns the default AppConfig.

    Asserts:
        - The returned object is an instance of AppConfig.
        - Default values are set as expected (mode, use_gui, category_structure, test_mode).
    """
    # No need to mock the config anymore as it's already set in conftest.py
    ConfigManager.reset()

    # Assert that when the file doesn't exist, it returns the default AppConfig
    config = ConfigManager.load_config("non_existent.json")

    # Verify it returns the default AppConfig type
    assert isinstance(config, AppConfig)

    # You can also check default values set in your AppConfig:
    assert config.mode == "test"  # Default value from the fixture
    assert config.use_gui is False  # Default value from the fixture
    assert config.category_structure == {"Test": ["Subtest"]}  # Default category
    assert config.test_mode is True  # Default value from the fixture


def test_config_manager_malformed_json(temp_dir):
    """
    Test that loading a malformed JSON config file raises a ValueError.

    Asserts:
        - ValueError is raised when attempting to load a malformed config file.
    """
    malformed_path = temp_dir / "malformed.json"
    malformed_path.write_text('{"mode": "test",,,}', encoding="utf-8")  # intentionally broken JSON
    ConfigManager.reset()
    with pytest.raises(ValueError):
        ConfigManager.load_config(str(malformed_path))


def test_config_manager_get_existing_key(temp_config_file):
    """
    Test that ConfigManager.get_value returns the correct value for an existing key.

    Asserts:
        - The value returned for an existing key matches the expected value from the config.
    """
    ConfigManager.reset()
    ConfigManager.load_config(config_path=str(temp_config_file))  # Explicitly load the config first
    value = ConfigManager.get_value("batch_size")
    assert value == 5  # Or whatever is specified in your test config


def test_config_manager_get_missing_key(temp_config_file):
    """
    Test that ConfigManager.get_value returns the provided default value for a missing key.

    Asserts:
        - The default value is returned when the key does not exist in the config.
    """
    ConfigManager.reset()
    ConfigManager.load_config(config_path=str(temp_config_file))  # Explicitly load the config first
    default_value = ConfigManager.get_value("non_existent", default=999)
    assert default_value == 999
