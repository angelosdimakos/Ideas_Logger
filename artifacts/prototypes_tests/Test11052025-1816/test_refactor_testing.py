import pytest

from refactor_linting import load_config

def test_load_config():
    """Test load_config function with a valid YAML file."""
    config_file = "test_config.yaml"  # Replace this placeholder with the path to your actual YAML file.
    loaded_config = load_config(config_file)

    assert isinstance(loaded_config, dict), "The loaded configuration should be a dictionary."
    # Add more specific tests for the structure and contents of the loaded config.

def test_load_config_invalid_file():
    """Test load_config function with an invalid file."""
    config_file = "nonexistent_file.yaml"  # Replace this placeholder with the path to a non-existent YAML file.
    with pytest.raises(FileNotFoundError):
        load_config(config_file)
