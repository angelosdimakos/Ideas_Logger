from scripts.config.config_manager import ConfigManager, AppConfig
import pytest
pytestmark = [pytest.mark.unit]


def test_config_manager_load_valid(temp_config_file):
    ConfigManager.reset()
    config = ConfigManager.load_config(str(temp_config_file))
    assert isinstance(config, AppConfig)
    assert config.mode == "test"
    assert config.llm_model == "mistral"
    assert config.logs_dir.endswith("logs")

def test_config_manager_missing_file():
    ConfigManager.reset()
    with pytest.raises(FileNotFoundError):
        ConfigManager.load_config("non_existent.json")

def test_config_manager_malformed_json(temp_dir):
    malformed_path = temp_dir / "malformed.json"
    malformed_path.write_text('{"mode": "test",,,}', encoding="utf-8")  # intentionally broken JSON
    ConfigManager.reset()
    with pytest.raises(ValueError):
        ConfigManager.load_config(str(malformed_path))

def test_config_manager_get_existing_key(temp_config_file):
    """
    Verifies that `ConfigManager.get_value` returns the correct value for an existing key.
    """
    ConfigManager.reset()
    ConfigManager.load_config(config_path=str(temp_config_file))  # Explicitly load the config first
    value = ConfigManager.get_value("batch_size")
    assert value == 5  # Or whatever is specified in your test config


def test_config_manager_get_missing_key(temp_config_file):
    """
    Verifies that `ConfigManager.get_value` returns the default value for a missing key.
    """
    ConfigManager.reset()
    ConfigManager.load_config(config_path=str(temp_config_file))  # Explicitly load the config first
    default_value = ConfigManager.get_value("non_existent", default=999)
    assert default_value == 999


