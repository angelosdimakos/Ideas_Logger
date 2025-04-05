from pathlib import Path
from datetime import datetime
import logging
import re

from scripts.ai.ai_summarizer import AISummarizer
from scripts.config.config_loader import get_config_value, get_effective_config
from scripts.utils.file_utils import sanitize_filename, write_json, read_json, make_backup
from scripts.paths import ZephyrusPaths
from scripts.core.summary_tracker import SummaryTracker
from scripts.core.log_manager import LogManager

logger = logging.getLogger(__name__)

class ZephyrusLoggerCore:
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
    DATE_FORMAT = "%Y-%m-%d"
    BATCH_KEY = "batch"
    ORIGINAL_SUMMARY_KEY = "original_summary"
    CORRECTED_SUMMARY_KEY = "corrected_summary"
    CORRECTION_TIMESTAMP_KEY = "correction_timestamp"
    CONTENT_KEY = "content"
    TIMESTAMP_KEY = "timestamp"

    def __init__(self, script_dir):
        self.script_dir = Path(script_dir)
        self.config = get_effective_config()
        self.paths = ZephyrusPaths.from_config(self.script_dir)

        if self.config.get("test_mode", False):
            logger.warning("[TEST MODE: ACTIVE] Using test directories from config")

        self.ai_summarizer = AISummarizer()
        self.summary_tracker = SummaryTracker(self.paths)
        force_rebuild = get_config_value(self.config, "force_summary_tracker_rebuild", False)
        if force_rebuild or not SummaryTracker.validate(self.summary_tracker.tracker):
            logger.warning("[RECOVERY] Summary tracker is empty or invalid. Rebuilding from log.")
            self.summary_tracker.rebuild()

        if self.paths.correction_summaries_file.exists():
            make_backup(self.paths.correction_summaries_file)
        self.BATCH_SIZE = max(1, int(get_config_value(self.config, "batch_size", 5)))

        # Initialize LogManager to handle all log operations.
        self.log_manager = LogManager(
            self.paths.json_log_file,
            self.paths.txt_log_file,
            self.paths.correction_summaries_file,
            self.TIMESTAMP_FORMAT,
            self.CONTENT_KEY,
            self.TIMESTAMP_KEY
        )

        self._initialize_environment()

    def _safe_read_json(self, filepath: Path) -> dict:
        try:
            return read_json(filepath)
        except Exception as e:
            logger.error("Failed to read JSON from %s: %s", filepath, e, exc_info=True)
            return {}

    def _initialize_environment(self):
        self.paths.log_dir.mkdir(exist_ok=True, parents=True)
        self.paths.export_dir.mkdir(exist_ok=True, parents=True)
        if not self.paths.json_log_file.exists():
            write_json(self.paths.json_log_file, {})
        if not self.paths.txt_log_file.exists():
            self.paths.txt_log_file.write_text("=== Zephyrus Idea Logger ===\n", encoding="utf-8")
        if not self.paths.correction_summaries_file.exists():
            write_json(self.paths.correction_summaries_file, {})
        elif self.paths.correction_summaries_file.stat().st_size == 0:
            logger.warning("correction_summaries_file was empty. Initializing...")
            write_json(self.paths.correction_summaries_file, {})
        if not self.paths.config_file.exists():
            self.paths.config_file.parent.mkdir(parents=True, exist_ok=True)
            write_json(self.paths.config_file, {"batch_size": 5})

    def _get_summary_for_batch(self, batch_entries, subcategory: str) -> str:
        try:
            summary = self.ai_summarizer.summarize_entries_bulk(
                [entry[self.CONTENT_KEY] for entry in batch_entries],
                subcategory=subcategory
            )
        except Exception as e:
            logger.error("AI summarization failed: %s", e, exc_info=True)
            try:
                summary = self.ai_summarizer._fallback_summary(
                    "\n".join(entry[self.CONTENT_KEY] for entry in batch_entries)
                )
            except Exception as fallback_e:
                logger.error("Fallback summarization failed: %s", fallback_e, exc_info=True)
                return None
        return summary.strip() if summary and summary.strip() else None

    def log_to_json(self, timestamp, date_str, main_category, subcategory, entry) -> bool:
        try:
            # Delegate the append operation to LogManager.
            self.log_manager.append_entry(date_str, main_category, subcategory, entry)
            self.summary_tracker.update(main_category, subcategory, new_entries=1)
            tracker = self.summary_tracker.tracker.get(main_category, {}).get(subcategory, {})
            unsummarized = tracker.get("logged_total", 0) - tracker.get("summarized_total", 0)
            if unsummarized >= self.BATCH_SIZE:
                logger.info("[BATCH READY] %d unsummarized entries in %s → %s", unsummarized, main_category, subcategory)
                self.generate_global_summary(main_category, subcategory)
            else:
                needed = self.BATCH_SIZE - unsummarized
                logger.info("[LOGGED] Entry added for %s → %s. Need %d more entries to trigger summary.", main_category, subcategory, needed)
            return True
        except Exception as e:
            logger.error("Error in log_to_json: %s", e, exc_info=True)
            return False

    def generate_global_summary(self, main_category: str, subcategory: str) -> bool:
        batch_entries = self.log_manager.get_unsummarized_batch(
            main_category,
            subcategory,
            self.summary_tracker.get_summarized_count(main_category, subcategory),
            self.BATCH_SIZE
        )
        if len(batch_entries) < self.BATCH_SIZE:
            logger.info("[SKIP] Not enough unsummarized entries for %s → %s", main_category, subcategory)
            return False
        summary = self._get_summary_for_batch(batch_entries, subcategory)
        if not summary:
            logger.error("[ERROR] AI summary returned empty after attempts.")
            return False
        start_ts = batch_entries[0][self.TIMESTAMP_KEY]
        end_ts = batch_entries[-1][self.TIMESTAMP_KEY]
        batch_label = f"{start_ts} → {end_ts}"
        new_data = {
            "batch": batch_label,
            self.ORIGINAL_SUMMARY_KEY: summary,
            self.CORRECTED_SUMMARY_KEY: "",
            self.CORRECTION_TIMESTAMP_KEY: datetime.now().strftime(self.TIMESTAMP_FORMAT),
            "start": start_ts,
            "end": end_ts
        }
        self.log_manager.update_correction_summaries(main_category, subcategory, new_data)
        self.summary_tracker.update(main_category, subcategory, summarized=self.BATCH_SIZE)
        logger.info("[SUCCESS] Global summary written for %s → %s (Batch: %s)", main_category, subcategory, batch_label)
        return True

    def generate_summary(self, date_str, main_category, subcategory):
        return self.generate_global_summary(main_category, subcategory)

    def log_to_markdown(self, date_str, main_category, subcategory, entry) -> bool:
        try:
            md_filename = sanitize_filename(main_category) + ".md"
            md_path = self.paths.export_dir / md_filename
            date_header = f"## {date_str}"
            md_content = f"- **{subcategory}**: {entry}\n"
            if md_path.exists():
                content = md_path.read_text(encoding="utf-8")
                if date_header in content:
                    updated_content = re.sub(f"({date_header}\\n)", f"\\1{md_content}", content, count=1)
                else:
                    updated_content = f"{content}\n{date_header}\n\n{md_content}"
            else:
                updated_content = f"# {main_category}\n\n{date_header}\n\n{md_content}"
            md_path.write_text(updated_content, encoding="utf-8")
            return True
        except Exception as e:
            logger.error("Error in log_to_markdown: %s", e, exc_info=True)
            return False

    def force_summary_all(self):
        """
        Forces summarization for all log entries across all dates, main categories, and subcategories.
        Iterates until no more unsummarized batches are available.
        """
        logs = self.log_manager.read_logs()
        for date in sorted(logs.keys()):
            for main_cat, subcats in logs[date].items():
                for sub_cat in subcats.keys():
                    # Continue generating summary for each (main_cat, sub_cat) until no more batches are ready.
                    while self.generate_global_summary(main_cat, sub_cat):
                        pass

    def save_entry(self, main_category, subcategory, entry) -> bool:
        if not main_category or not subcategory or not entry:
            logger.error("Invalid input: main_category, subcategory, and entry must not be empty")
            return False
        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
        date_str = datetime.now().strftime(self.DATE_FORMAT)
        json_success = self.log_to_json(timestamp, date_str, main_category, subcategory, entry)
        md_success = self.log_to_markdown(date_str, main_category, subcategory, entry)
        return json_success and md_success

    def search_summaries(self, query: str, top_k=5):
        return self.summary_tracker.summary_indexer.search(query, top_k)

    def search_raw_logs(self, query: str, top_k=5):
        return self.summary_tracker.raw_indexer.search(query, top_k)

    def log_new_entry(self, main_category, subcategory, entry):
        """
        Wrapper for save_entry to support the GUI controller interface.
        """
        return self.save_entry(main_category, subcategory, entry)


