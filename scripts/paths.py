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
    vector_store_dir: Path
    faiss_index_path: Path
    faiss_metadata_path: Path
    raw_log_index_path: Path
    raw_log_metadata_path: Path
    raw_log_file: Path  # ✅ <-- ADD THIS


    @staticmethod
    def _resolve_path(config, key, default) -> Path:
        return Path(get_absolute_path(get_config_value(config, key, str(default))))

    @staticmethod
    def from_config(script_dir: Path) -> "ZephyrusPaths":
        config = get_effective_config()
        test_mode = config.get("test_mode", False)

        # Use project root, not script dir
        project_root = script_dir.resolve().parent

        if test_mode:
            log_dir = Path(get_absolute_path(config["test_logs_dir"]))
            export_dir = Path(get_absolute_path(config["test_export_dir"]))
        else:
            log_dir = ZephyrusPaths._resolve_path(config, "logs_dir", project_root / "logs")
            export_dir = ZephyrusPaths._resolve_path(config, "export_dir", project_root / "exports")

        vector_store_dir = ZephyrusPaths._resolve_path(config, "vector_store_dir", project_root / "vector_store")

        json_log_file = ZephyrusPaths._resolve_path(config, "raw_log_path", log_dir / "zephyrus_log.json")
        correction_summaries_file = ZephyrusPaths._resolve_path(config, "correction_summaries_path", log_dir / "correction_summaries.json")
        txt_log_file = log_dir / "zephyrus_log.txt"
        summary_tracker_file = log_dir / "summary_tracker.json"
        config_file = project_root / "scripts" / "config" / "config.json"

        faiss_index_path = ZephyrusPaths._resolve_path(config, "faiss_index_path", vector_store_dir / "summary_index.faiss")
        faiss_metadata_path = ZephyrusPaths._resolve_path(config, "faiss_metadata_path", vector_store_dir / "summary_metadata.pkl")
        raw_log_index_path = ZephyrusPaths._resolve_path(config, "raw_log_index_path", vector_store_dir / "raw_index.faiss")
        raw_log_metadata_path = ZephyrusPaths._resolve_path(config, "raw_log_metadata_path", vector_store_dir / "raw_metadata.pkl")

        return ZephyrusPaths(
            log_dir=log_dir,
            export_dir=export_dir,
            json_log_file=json_log_file,
            txt_log_file=txt_log_file,
            correction_summaries_file=correction_summaries_file,
            summary_tracker_file=summary_tracker_file,
            config_file=config_file,
            vector_store_dir=vector_store_dir,
            faiss_index_path=faiss_index_path,
            faiss_metadata_path=faiss_metadata_path,
            raw_log_index_path=raw_log_index_path,
            raw_log_metadata_path=raw_log_metadata_path,
            raw_log_file=json_log_file,  # ✅ <-- ADD THIS LINE
        )

