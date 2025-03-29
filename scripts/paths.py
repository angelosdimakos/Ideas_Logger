from pathlib import Path
from dataclasses import dataclass
from scripts.config.config_loader import get_config_value, get_absolute_path, get_effective_config

@dataclass
class ZephyrusPaths:
    log_dir: Path
    export_dir: Path
    json_log_file: Path
    txt_log_file: Path
    correction_summaries_file: Path
    summary_tracker_file: Path
    config_file: Path

    @staticmethod
    def _resolve_path(config, key, default) -> Path:
        """
        Resolve a path from the configuration in production mode.
        """
        return Path(get_absolute_path(get_config_value(config, key, default)))

    @staticmethod
    def from_config(script_dir: Path) -> "ZephyrusPaths":
        config = get_effective_config()
        test_mode = config.get("test_mode", False)

        # Base directories are chosen differently based on test mode.
        if test_mode:
            base_log_dir = Path(get_absolute_path(config["test_logs_dir"]))
            base_export_dir = Path(get_absolute_path(config["test_export_dir"]))
        else:
            base_log_dir = ZephyrusPaths._resolve_path(config, "logs_dir", script_dir / "logs")
            base_export_dir = ZephyrusPaths._resolve_path(config, "export_dir", script_dir / "exports")

        # File defaults.
        default_json_log = base_log_dir / "zephyrus_log.json"
        default_correction_summaries = base_log_dir / "correction_summaries.json"

        # For files, if not in test mode, we attempt to resolve the path via config.
        json_log_file = default_json_log if test_mode else Path(
            get_absolute_path(get_config_value(config, "raw_log_path", str(default_json_log)))
        )
        correction_summaries_file = default_correction_summaries if test_mode else Path(
            get_absolute_path(get_config_value(config, "correction_summaries_path", str(default_correction_summaries)))
        )

        return ZephyrusPaths(
            log_dir=base_log_dir,
            export_dir=base_export_dir,
            json_log_file=json_log_file,
            txt_log_file=base_log_dir / "zephyrus_log.txt",
            correction_summaries_file=correction_summaries_file,
            summary_tracker_file=base_log_dir / "summary_tracker.json",
            config_file=Path(get_absolute_path("scripts/config/config.json"))

        )
