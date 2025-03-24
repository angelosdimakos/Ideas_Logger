import json
from pathlib import Path
from datetime import datetime
import logging
import re
from scripts.ai_summarizer import AISummarizer
from scripts.summary_indexer import SummaryIndexer
from scripts.config_loader import load_config, get_config_value, get_absolute_path
from utils.file_utils import sanitize_filename, safe_path, write_json, read_json, make_backup

logger = logging.getLogger(__name__)


class ZephyrusLoggerCore:
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

        Args:
            script_dir: The directory where the script is running from
        """
        self.config = load_config()
        self.script_dir = Path(script_dir)
        self.log_dir = Path(get_absolute_path(get_config_value(self.config, "logs_dir", str(self.script_dir / "logs"))))
        self.export_dir = Path(
            get_absolute_path(get_config_value(self.config, "export_dir", str(self.script_dir / "exports"))))
        self.json_log_file = self.log_dir / "zephyrus_log.json"
        self.txt_log_file = self.log_dir / "zephyrus_log.txt"
        self.correction_summaries_file = self.log_dir / "correction_summaries.json"
        self.config_file = Path(get_absolute_path("config/config.json"))
        self.ai_summarizer = AISummarizer()
        self.summary_tracker_file = self.log_dir / "summary_tracker.json"
        if not self.summary_tracker_file.exists():
            write_json(self.summary_tracker_file, {})
        self.summary_tracker = read_json(self.summary_tracker_file)

        if self.correction_summaries_file.exists():
            make_backup(self.correction_summaries_file)

        self._initialize_environment()
        self.BATCH_SIZE = max(1, int(get_config_value(self.config, "batch_size", 5)))

    def _initialize_environment(self):
        """
        Set up the necessary directories and files for the logger to function.
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
        Log an entry to the JSON log file.

        Args:
            timestamp: Timestamp of the entry
            date_str: Date string for organizing entries
            main_category: Main category of the entry
            subcategory: Subcategory of the entry
            entry: The content to log

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logs = read_json(self.json_log_file)
            logs.setdefault(date_str, {}).setdefault(main_category, {}).setdefault(subcategory, [])
            logs[date_str][main_category][subcategory].append({
                self.TIMESTAMP_KEY: timestamp,
                self.CONTENT_KEY: entry
            })
            write_json(self.json_log_file, logs)

            # Update global tracker (global counts are used only for triggering summaries across days)
            self.update_summary_tracker(main_category, subcategory, new_entries=1)

            # Calculate global unsummarized count
            tracker = self.summary_tracker.get(main_category, {}).get(subcategory, {})
            logged_total = tracker.get("logged_total", 0)
            summarized_total = tracker.get("summarized_total", 0)
            unsummarized = logged_total - summarized_total

            if unsummarized >= self.BATCH_SIZE:
                logger.info("[BATCH READY] %d unsummarized entries globally in %s → %s", unsummarized, main_category,
                            subcategory)
                # Trigger summary as a side effect; do not use its return value.
                self.generate_summary_across_days(main_category, subcategory)
            else:
                needed = self.BATCH_SIZE - unsummarized
                logger.info("[LOGGED] Entry added for %s → %s. Need %d more entries across days to trigger summary.",
                            main_category, subcategory, needed)
            return True

        except Exception as e:
            logger.error("Error in log_to_json: %s", e, exc_info=True)
            return False

    def get_summarized_count(self, date_str, main_category, subcategory):
        """
        Get the count of entries that have already been summarized.

        Args:
            date_str: Date string for organizing entries
            main_category: Main category of the entries
            subcategory: Subcategory of the entries

        Returns:
            int: The number of entries that have been summarized for the given day
        """
        summarized_count = 0
        try:
            summaries = read_json(self.correction_summaries_file)
            cat_summaries = summaries.get(date_str, {}).get(main_category, {}).get(subcategory, [])
            for batch_summary in cat_summaries:
                batch_range = batch_summary.get(self.BATCH_KEY, "")
                if "-" in batch_range:
                    try:
                        end_idx = int(batch_range.split("-")[1])
                        if end_idx > summarized_count:
                            summarized_count = end_idx
                    except ValueError:
                        logger.warning("Could not parse batch range: %s", batch_range)
        except Exception as e:
            logger.error("get_summarized_count failed: %s", e, exc_info=True)
        return summarized_count

    def generate_summary(self, date_str, main_category, subcategory):
        """
        Generate a summary for a batch of entries for a specific day.

        Args:
            date_str: Date string for organizing entries
            main_category: Main category of the entries
            subcategory: Subcategory of the entries

        Returns:
            bool: True if summary was successfully generated, False otherwise
        """
        try:
            logs = read_json(self.json_log_file)
            summaries = read_json(self.correction_summaries_file)
            summaries.setdefault(date_str, {}).setdefault(main_category, {}).setdefault(subcategory, [])
            all_entries = logs.get(date_str, {}).get(main_category, {}).get(subcategory, [])
            if not all_entries:
                logger.warning("[SKIP] No entries found for %s %s → %s", date_str, main_category, subcategory)
                return False

            summarized_count = self.get_summarized_count(date_str, main_category, subcategory)
            logger.info("[INFO] Summarized count so far for %s → %s on %s: %d", main_category, subcategory, date_str,
                        summarized_count)

            remaining_entries = all_entries[summarized_count:]
            remaining_count = len(remaining_entries)
            logger.info("[INFO] %d unsummarized entries remain for %s on %s → %s", remaining_count, date_str,
                        main_category, subcategory)

            # Only generate a summary if there are at least BATCH_SIZE new entries
            if remaining_count < self.BATCH_SIZE:
                logger.info("[SKIP] Not enough new entries to summarize for %s in %s → %s", date_str, main_category,
                            subcategory)
                return False

            batch_entries = remaining_entries[:self.BATCH_SIZE]
            entry_texts = [entry[self.CONTENT_KEY] for entry in batch_entries]

            if not entry_texts:
                logger.error("[ERROR] No content found to summarize.")
                return False

            try:
                summary = self.ai_summarizer.summarize_entries_bulk(entry_texts, subcategory=subcategory)
            except Exception as e:
                logger.error("AI summarization failed: %s. Falling back to alternative method.", e, exc_info=True)
                summary = self.ai_summarizer._fallback_summary("\n".join(entry_texts))

            if not summary:
                logger.error("[ERROR] AI summary returned empty. Prompt was: %s ...", entry_texts[:2])
                return False

            start_idx = summarized_count + 1
            end_idx = start_idx + self.BATCH_SIZE - 1
            batch_label = f"{start_idx}-{end_idx}"

            summary_data = {
                self.BATCH_KEY: batch_label,
                self.ORIGINAL_SUMMARY_KEY: summary,
                self.CORRECTED_SUMMARY_KEY: "",
                self.CORRECTION_TIMESTAMP_KEY: datetime.now().strftime(self.TIMESTAMP_FORMAT)
            }

            summaries[date_str][main_category][subcategory].append(summary_data)
            write_json(self.correction_summaries_file, summaries)

            logger.info("[SUCCESS] Summarized %d new entries for %s on %s → %s (Batch %s)", self.BATCH_SIZE,
                        main_category, date_str, subcategory, batch_label)
            return True

        except Exception as e:
            logger.error("Error in generate_summary: %s", e, exc_info=True)
            return False

    def log_to_markdown(self, date_str, main_category, subcategory, entry):
        """
        Log an entry to a Markdown file.

        Args:
            date_str: Date string for organizing entries
            main_category: Main category of the entry
            subcategory: Subcategory of the entry
            entry: The content to log

        Returns:
            bool: True if successful, False otherwise
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

        Args:
            main_category: Main category of the entry
            subcategory: Subcategory of the entry
            entry: The content to save

        Returns:
            bool: True if both operations were successful, False otherwise
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
        self.summary_tracker.setdefault(main_category, {}).setdefault(subcategory, {
            "logged_total": 0, "summarized_total": 0
        })

        self.summary_tracker[main_category][subcategory]["logged_total"] += new_entries
        self.summary_tracker[main_category][subcategory]["summarized_total"] += summarized
        write_json(self.summary_tracker_file, self.summary_tracker)

    def get_unsummarized_entries_across_days(self, main_category, subcategory):
        logs = read_json(self.json_log_file)
        entries = []
        summarized_total = self.summary_tracker.get(main_category, {}).get(subcategory, {}).get("summarized_total", 0)
        count = 0

        for date in sorted(logs.keys()):
            day_logs = logs[date].get(main_category, {}).get(subcategory, [])
            for entry in day_logs:
                if count >= summarized_total:
                    entries.append(entry["content"])
                count += 1
        return entries

    def generate_summary_across_days(self, main_category, subcategory):
        """
        Generate summaries for each day that has at least BATCH_SIZE unsummarized entries.

        Returns:
            bool: True if at least one summary was generated, False otherwise.
        """
        logs = read_json(self.json_log_file)
        summaries_written = False

        for date_str, categories in logs.items():
            entries = categories.get(main_category, {}).get(subcategory, [])
            if len(entries) < self.BATCH_SIZE:
                continue

            summarized_count = self.get_summarized_count(date_str, main_category, subcategory)
            unsummarized = entries[summarized_count:]

            if len(unsummarized) < self.BATCH_SIZE:
                print(f"[SKIP] Not enough new entries to summarize {main_category} → {subcategory} on {date_str}")
                continue

            batch = unsummarized[:self.BATCH_SIZE]
            summary = self.ai_summarizer.summarize_entries_bulk(batch, subcategory=subcategory)
            if not summary:
                continue

            new_data = {
                "batch": f"{summarized_count + 1}-{summarized_count + len(batch)}",
                "original_summary": summary,
                "corrected_summary": "",
                "correction_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            correction_data = read_json(self.correction_summaries_file)
            correction_data.setdefault(date_str, {}).setdefault(main_category, {}).setdefault(subcategory, []).append(
                new_data)
            write_json(self.correction_summaries_file, correction_data)

            self.update_summary_tracker(main_category, subcategory, summarized=len(batch))
            print(f"[✅ SUCCESS] Summarized {len(batch)} entries for {main_category} → {subcategory} on {date_str}")
            summaries_written = True

        return summaries_written
