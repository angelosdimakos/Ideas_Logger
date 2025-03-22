import json
import os

# Get the base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config(config_path=os.path.join(BASE_DIR, "config.json")):
    """
    Safely load the config file. If it doesn't exist or has errors, return an empty dict.
    """
    if not os.path.exists(config_path):
        print(f"[WARN] Config file '{config_path}' not found. Using defaults.")
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse config file: {e}. Using defaults.")
        return {}


def get_config_value(config, key, default):
    """
    Helper to retrieve a config value with fallback.
    """
    return config.get(key, default)


def get_absolute_path(relative_path):
    """
    Build an absolute path from a project-root-relative path.
    """
    return os.path.join(BASE_DIR, relative_path)


# Example usage:
if __name__ == "__main__":
    config = load_config()
    batch_size = get_config_value(config, "batch_size", 5)
    summary_path = get_absolute_path(get_config_value(config, "correction_summaries_path", "logs/correction_summaries.json"))
    print("Batch Size:", batch_size)
    print("Summary Path:", summary_path)