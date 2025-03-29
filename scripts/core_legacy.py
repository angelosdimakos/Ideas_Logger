from pathlib import Path
from datetime import datetime
import logging
import re

from scripts.ai.ai_summarizer import AISummarizer
from scripts.config.config_loader import get_config_value, get_absolute_path, get_effective_config
from scripts.utils.file_utils import sanitize_filename, write_json, read_json, make_backup
"Bad Example of previous code with tight coupling between I/O, summary tracking, and breaking SRP."
logger = logging.getLogger(__name__)

class ZephyrusLoggerLegacyCore:
    # Constants for frequently used string literals
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
    DATE_FORMAT = "%Y-%m-%d"
    BATCH_KEY = "batch"
    ORIGINAL_SUMMARY_KEY = "original_summary"
    CORRECTED_SUMMARY_KEY = "corrected_summary"
    CORRECTION_TIMESTAMP_KEY = "correction_timestamp"
    CONTENT_KEY = "content"
    TIMESTAMP_KEY = "timestamp"

    def __init__(self, script_dir):
        """
        Initialize the ZephyrusLoggerCore with configuration and file paths.

        This class serves as the core logic unit for the Zephyrus Idea Logger.
        It handles the initialization of the application's state, including
        loading configuration, setting up directory paths, and loading the
        AI summarizer.

        Args:
            script_dir: The directory where the script is running from.
        """
        self.script_dir = Path(script_dir)
        self.config = get_effective_config()
        self.config_file = Path(get_absolute_path("../config/config.json"))


        # 🔒 Override paths if in test mode
        if self.config.get("test_mode", False):
            logger.warning("[TEST MODE: ACTIVE] Using test directories from config")
            self.log_dir = Path(get_absolute_path(self.config["test_logs_dir"]))
            self.export_dir = Path(get_absolute_path(self.config["test_export_dir"]))
            self.json_log_file = self.log_dir / "zephyrus_log.json"
            self.txt_log_file = self.log_dir / "zephyrus_log.txt"
            self.correction_summaries_file = self.log_dir / "correction_summaries.json"
            self.summary_tracker_file = self.log_dir / "summary_tracker.json"
        else:
            # Load paths from config or use fallback defaults.
            self.log_dir = Path(
                get_absolute_path(get_config_value(self.config, "logs_dir", str(self.script_dir / "logs"))))
            self.export_dir = Path(
                get_absolute_path(get_config_value(self.config, "export_dir", str(self.script_dir / "exports"))))

            self.json_log_file = Path(get_absolute_path(get_config_value(
                self.config, "raw_log_path", str(self.log_dir / "zephyrus_log.json")
            )))
            self.txt_log_file = self.log_dir / "zephyrus_log.txt"
            self.correction_summaries_file = Path(get_absolute_path(get_config_value(
                self.config, "correction_summaries_path", str(self.log_dir / "correction_summaries.json")
            )))
            self.summary_tracker_file = self.log_dir / "summary_tracker.json"


        self.ai_summarizer = AISummarizer()

        # Create empty summary tracker file if missing.
        if not self.summary_tracker_file.exists():
            write_json(self.summary_tracker_file, {})

        self.summary_tracker = self._safe_read_json(self.summary_tracker_file)

        # Optionally force rebuild via config setting "force_summary_tracker_rebuild".
        force_rebuild = get_config_value(self.config, "force_summary_tracker_rebuild", False)
        if force_rebuild or not self._validate_summary_tracker(self.summary_tracker):
            logger.warning("[RECOVERY] Summary tracker is empty or invalid. Rebuilding from log.")
            self.initialize_summary_tracker_from_log()

        # Backup correction summaries if they exist.
        if self.correction_summaries_file.exists():
            make_backup(self.correction_summaries_file)
        self.BATCH_SIZE = max(1, int(get_config_value(self.config, "batch_size", 5)))

        self._initialize_environment()

    def _safe_read_json(self, filepath):
        """
        Safely read a JSON file. If reading fails, log the error and return an empty dictionary.

        This function will catch any exceptions raised while reading the file, log the error
        with a traceback, and return an empty dictionary. This is useful for reading configuration
        files that might not yet exist, or reading files that might be temporarily unavailable.
        """
        try:
            return read_json(filepath)
        except Exception as e:
            logger.error("Failed to read JSON from %s: %s", filepath, e, exc_info=True)
            return {}

    def _validate_summary_tracker(self, tracker):
        """
        Validate that the summary tracker has the expected structure.
        It should be a dict where each main category maps to subcategories, each containing
        a dict with 'logged_total' and 'summarized_total' as integer values.

        The tracker should have the following structure:
        {
            "main_category_1": {
                "sub_category_1": {"logged_total": int, "summarized_total": int},
                "sub_category_2": {"logged_total": int, "summarized_total": int},
                ...
            },
            "main_category_2": {
                "sub_category_1": {"logged_total": int, "summarized_total": int},
                "sub_category_2": {"logged_total": int, "summarized_total": int},
                ...
            },
            ...
        }
        """
        if not isinstance(tracker, dict):
            return False
        for main_cat, subcats in tracker.items():
            if not isinstance(subcats, dict):
                return False
            for subcat, counts in subcats.items():
                if not isinstance(counts, dict):
                    return False
                if "logged_total" not in counts or "summarized_total" not in counts:
                    return False
                if not isinstance(counts["logged_total"], int) or not isinstance(counts["summarized_total"], int):
                    return False
        return True

    def _initialize_environment(self):
        """
        Set up the necessary directories and files for the logger to function.

        This function creates the necessary directories and files if they don't exist,
        and also checks if the files are empty and initializes them if so.
        """
        self.log_dir.mkdir(exist_ok=True, parents=True)
        self.export_dir.mkdir(exist_ok=True, parents=True)

        if not self.json_log_file.exists():
            write_json(self.json_log_file, {})

        if not self.txt_log_file.exists():
            self.txt_log_file.write_text("=== Zephyrus Idea Logger ===\n", encoding="utf-8")

        if not self.correction_summaries_file.exists():
            write_json(self.correction_summaries_file, {})
        elif self.correction_summaries_file.stat().st_size == 0:
            logger.warning("correction_summaries_file was empty. Initializing...")
            write_json(self.correction_summaries_file, {})

        if not self.config_file.exists():
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            write_json(self.config_file, {"batch_size": 5})

    def log_to_json(self, timestamp, date_str, main_category, subcategory, entry):

        """
        Log an entry to the JSON log file and update the global summary tracker.

        This function takes a timestamp, a formatted date string, a main category,
        a subcategory, and the entry to be logged. The entry is then logged to the
        JSON log file and the global summary tracker is updated.

        The function is designed to be idempotent, so it should be safe to call
        it multiple times with the same arguments without causing any issues.
        """
        try:
            logs = self._safe_read_json(self.json_log_file)
            logs.setdefault(date_str, {}).setdefault(main_category, {}).setdefault(subcategory, [])
            logs[date_str][main_category][subcategory].append({
                self.TIMESTAMP_KEY: timestamp,
                self.CONTENT_KEY: entry
            })
            write_json(self.json_log_file, logs)

            # Update the summary tracker.
            self.update_summary_tracker(main_category, subcategory, new_entries=1)

            tracker = self.summary_tracker.get(main_category, {}).get(subcategory, {})
            logged_total = tracker.get("logged_total", 0)
            summarized_total = tracker.get("summarized_total", 0)
            unsummarized = logged_total - summarized_total

            if unsummarized >= self.BATCH_SIZE:
                logger.info("[BATCH READY] %d unsummarized entries globally in %s → %s", unsummarized, main_category, subcategory)
                self.generate_global_summary(main_category, subcategory)
            else:
                needed = self.BATCH_SIZE - unsummarized
                logger.info("[LOGGED] Entry added for %s → %s. Need %d more entries globally to trigger summary.", main_category, subcategory, needed)
            return True

        except Exception as e:
            logger.error("Error in log_to_json: %s", e, exc_info=True)
            return False

    def get_unsummarized_entries_across_days(self, main_category, subcategory):

        """
        Retrieve all unsummarized entry contents for a given category/subcategory,
        aggregated chronologically from the entire log.

        This function returns a list of all unsummarized entry contents for the given
        category/subcategory, in chronological order. The list is expanded, so
        each entry is a string, and the function returns a list of strings.

        The function takes two arguments:
        - main_category: the main category of the log entries.
        - subcategory: the subcategory of the log entries.

        The function returns a list of strings, each of which is an unsummarized
        entry content in the given category/subcategory.
        """
        logs = self._safe_read_json(self.json_log_file)
        entries = []
        summarized_total = self.summary_tracker.get(main_category, {}).get(subcategory, {}).get("summarized_total", 0)
        count = 0
        for date in sorted(logs.keys()):
            day_logs = logs[date].get(main_category, {}).get(subcategory, [])
            for entry in day_logs:
                if count >= summarized_total:
                    entries.append(entry[self.CONTENT_KEY])
                count += 1
        return entries

    def get_unsummarized_batch_entries(self, main_category, subcategory):

        """
        Retrieves the first unsummarized batch (5 entries) across all dates
        for the given category/subcategory pair, along with full metadata.
        The function takes two arguments:
        - main_category: the main category of the log entries.
        - subcategory: the subcategory of the log entries.
        The function returns a list of dictionaries, each of which contains
        the full metadata for the corresponding entry (including the content
        of the entry), as well as the start and end timestamps for the batch.
        """
        logs = self._safe_read_json(self.json_log_file)
        summarized_total = self.summary_tracker.get(main_category, {}).get(subcategory, {}).get("summarized_total", 0)

        entries = []
        count = 0
        for date in sorted(logs.keys()):
            day_logs = logs[date].get(main_category, {}).get(subcategory, [])
            for entry in day_logs:
                if count >= summarized_total:
                    entries.append(entry)
                    if len(entries) == self.BATCH_SIZE:
                        return entries
                count += 1
        return []

    def generate_global_summary(self, main_category, subcategory):
        """
        Generate a comprehensive summary using the next available unsummarized batch of entries.

        This function takes a main category and a subcategory as arguments and generates a
        comprehensive summary using the next available unsummarized batch of entries. It tracks
        the operation using batch metadata, including start and end timestamps.

        The function returns a boolean indicating success.
        """

        batch_entries = self.get_unsummarized_batch_entries(main_category, subcategory)
        if len(batch_entries) < self.BATCH_SIZE:
            logger.info("[SKIP] Not enough unsummarized entries globally for %s → %s", main_category, subcategory)
            return False

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
                return False

        if summary is None or not summary.strip():
            logger.error("[ERROR] AI summary returned empty after both attempts.")
            return False

        start_ts = batch_entries[0][self.TIMESTAMP_KEY]
        end_ts = batch_entries[-1][self.TIMESTAMP_KEY]
        batch_label = f"{start_ts} → {end_ts}"

        correction_data = self._safe_read_json(self.correction_summaries_file)
        correction_data.setdefault("global", {}).setdefault(main_category, {}).setdefault(subcategory, [])

        new_data = {
            "batch": batch_label,
            self.ORIGINAL_SUMMARY_KEY: summary,
            self.CORRECTED_SUMMARY_KEY: "",
            self.CORRECTION_TIMESTAMP_KEY: datetime.now().strftime(self.TIMESTAMP_FORMAT),
            "start": start_ts,
            "end": end_ts
        }
        correction_data["global"][main_category][subcategory].append(new_data)
        write_json(self.correction_summaries_file, correction_data)

        self.update_summary_tracker(main_category, subcategory, summarized=self.BATCH_SIZE)


        logger.info("[SUCCESS] Global summary written for %s → %s (Batch: %s)", main_category, subcategory, batch_label)
        return True

    def generate_summary(self, date_str, main_category, subcategory):
        """
        For backward compatibility with the GUI (which passes a date), this method
        now delegates to the global summarization approach, ignoring the date.
        """
        return self.generate_global_summary(main_category, subcategory)

    def log_to_markdown(self, date_str, main_category, subcategory, entry):
        """
        Log an entry to a Markdown file.
        """
        try:
            md_filename = sanitize_filename(main_category) + ".md"
            md_path = self.export_dir / md_filename
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

    def save_entry(self, main_category, subcategory, entry):

        """
        Save an entry to both JSON and Markdown formats.

        This method will:
        1. Log the entry to a JSON file in the export directory.
        2. Log the entry to a Markdown file in the export directory.

        The JSON file will use the following format:
        {
            "date": "YYYY-MM-DD",
            "main_category": "...",
            "subcategory": "...",
            "entries": [...]
        }

        The Markdown file will use the following format:
        # <main_category>
        ## <date>
        - **<subcategory>**: <entry>
        """
        if not main_category or not subcategory or not entry:
            logger.error("Invalid input: main_category, subcategory, and entry must not be empty")
            return False

        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
        date_str = datetime.now().strftime(self.DATE_FORMAT)

        json_success = self.log_to_json(timestamp, date_str, main_category, subcategory, entry)
        md_success = self.log_to_markdown(date_str, main_category, subcategory, entry)
        return json_success and md_success

    def update_summary_tracker(self, main_category, subcategory, new_entries=0, summarized=0):
        """
        Update the global summary tracker for a given category/subcategory.

        Reads the current summary tracker from file, updates the relevant
        category/subcategory entry, and writes the updated tracker back to file.
        """
        self.summary_tracker.setdefault(main_category, {}).setdefault(subcategory, {"logged_total": 0, "summarized_total": 0})
        self.summary_tracker[main_category][subcategory]["logged_total"] += new_entries
        self.summary_tracker[main_category][subcategory]["summarized_total"] += summarized
        write_json(self.summary_tracker_file, self.summary_tracker)

    def initialize_summary_tracker_from_log(self):
        """
        Checks the integrity of the current summary tracker by checking for:
        1. Existence of summary tracker file
        2. Valid JSON structure
        3. Required keys and values
        4. Consistency of logged_total and summarized_total values

        If any of the above checks fail, the entire summary tracker will be
        reconstructed from zephyrus_log.json.
        """
        if self.summary_tracker and self._validate_summary_tracker(self.summary_tracker):
            logger.info("[INIT] Summary tracker integrity confirmed. Skipping rebuild.")
            return

        logger.warning("[RECOVERY] Invalid or missing summary tracker. Starting rebuild from zephyrus_log.json...")

        try:
            logs = self._safe_read_json(self.json_log_file)
            logger.info("[RECOVERY] Parsing %d date(s) from zephyrus_log.json...", len(logs))

            tracker = {}
            for date, categories in logs.items():
                for main_cat, subcats in categories.items():
                    for subcat, entries in subcats.items():
                        count = len(entries)
                        tracker.setdefault(main_cat, {}).setdefault(subcat, {
                            "logged_total": 0,
                            "summarized_total": 0
                        })
                        tracker[main_cat][subcat]["logged_total"] += count

            write_json(self.summary_tracker_file, tracker)
            self.summary_tracker = tracker
            logger.info("[RECOVERY] Rebuild complete. summary_tracker.json updated with %d top-level categories.",
                        len(tracker))

        except Exception as e:
            logger.error("[ERROR] Failed to rebuild summary tracker from log: %s", e, exc_info=True)
            self.summary_tracker = {}
            write_json(self.summary_tracker_file, self.summary_tracker)

    def get_summarized_count(self, main_category, subcategory):

        """
        Return the number of summarized entries globally from the summary tracker.

        The summary tracker is a JSON object written to `summary_tracker.json` which
        contains the following structure:

        {
            "main_category_1": {
                "sub_category_1": {"logged_total": int, "summarized_total": int},
                "sub_category_2": {"logged_total": int, "summarized_total": int},
                ...
            },
            "main_category_2": {
                "sub_category_1": {"logged_total": int, "summarized_total": int},
                "sub_category_2": {"logged_total": int, "summarized_total": int},
                ...
            },
            ...
        }

        The function will read the tracker from disk, traverse to the specified
        main category and subcategory, and return the value of "summarized_total".
        If the tracker is not found, or any of the above keys are not present, the
        function will return 0.
        """
        return self.summary_tracker.get(main_category, {}).get(subcategory, {}).get("summarized_total", 0)
