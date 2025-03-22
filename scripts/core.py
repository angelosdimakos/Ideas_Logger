import json
from pathlib import Path
from datetime import datetime
import logging
import re
from ai_summarizer import AISummarizer
import shutil
from summary_indexer import SummaryIndexer
from config_loader import load_config, get_config_value, get_absolute_path
import os

logging.basicConfig(
    level=logging.ERROR,
    filename="logs/zephyrus_logger_errors.log",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class ZephyrusLoggerCore:
    """
    ZephyrusLoggerCore is responsible for managing the logging process, summarization, 
    and handling the file system operations for storing logs, summaries, and metadata.
    """
    def __init__(self, script_dir):
        """
        Initializes the core components of ZephyrusLoggerCore, including setting up file paths, directories, 
        and configuring the AI summarizer.

        Parameters:
            script_dir (str): The directory where the script is located. Used to determine log and export directories.
        """
        self.config = load_config()
        self.script_dir = Path(script_dir)
        self.log_dir = get_absolute_path(get_config_value(self.config, "logs_dir", self.script_dir / "logs"))
        self.export_dir = get_absolute_path(get_config_value(self.config, "export_dir", self.script_dir / "exports"))
        self.json_log_file = Path(self.log_dir) / "zephyrus_log.json"
        self.txt_log_file = Path(self.log_dir) / "zephyrus_log.txt"
        self.correction_summaries_file = Path(self.log_dir) / "correction_summaries.json"
        self.config_file = get_absolute_path("config/config.json")
        self.ai_summarizer = AISummarizer()

        if self.correction_summaries_file.exists():
            shutil.copy(self.correction_summaries_file, Path(self.log_dir) / "correction_summaries_backup.json")

        self._initialize_environment()
        self.BATCH_SIZE = get_config_value(self.config, "batch_size", 5)

    def _initialize_environment(self):
        """
        Initializes the required directories and files for logging and summaries. Creates necessary directories
        and ensures that required files (logs, summaries) exist, creating them if not.

        This method should be called on initialization to ensure the environment is ready for logging.
        """
        
        Path(self.log_dir).mkdir(exist_ok=True, parents=True)
        Path(self.export_dir).mkdir(exist_ok=True, parents=True)

        if not self.json_log_file.exists():
            self.json_log_file.write_text("{}", encoding="utf-8")

        if not self.txt_log_file.exists():
            self.txt_log_file.write_text("=== Zephyrus Idea Logger ===\n", encoding="utf-8")

        if not self.correction_summaries_file.exists():
            self.correction_summaries_file.write_text("{}", encoding="utf-8")

        if not os.path.exists(self.config_file):
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            default_config = {"batch_size": 5}
            with open(self.config_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(default_config, indent=4))

    @staticmethod
    def safe_filename(text):
        """
        Converts a given string to a safe filename by replacing invalid characters with underscores.

        Parameters:
            text (str): The text to be converted into a safe filename.

        Returns:
            str: The safe filename with invalid characters replaced by underscores.
        """
        return re.sub(r'[\\/*?:"<>|]', "_", text.replace(" ", "_"))

    def log_to_json(self, timestamp, date_str, main_category, subcategory, entry):
        """
        Logs an entry to the JSON file, categorizing it by date, main category, and subcategory.
        If a batch of entries reaches the configured size, a summary is triggered.

        Parameters:
            timestamp (str): The timestamp when the entry was created.
            date_str (str): The date of the entry in string format (YYYY-MM-DD).
            main_category (str): The main category under which the entry is logged.
            subcategory (str): The subcategory under which the entry is logged.
            entry (str): The content of the log entry.

        Returns:
            bool: True if the entry was logged successfully and summary triggered if necessary, False otherwise.
        """
        try:
            logs = json.loads(self.json_log_file.read_text(encoding="utf-8"))

            if date_str not in logs:
                logs[date_str] = {}
            if main_category not in logs[date_str]:
                logs[date_str][main_category] = {}
            if subcategory not in logs[date_str][main_category]:
                logs[date_str][main_category][subcategory] = []

            logs[date_str][main_category][subcategory].append({"timestamp": timestamp, "content": entry})
            self.json_log_file.write_text(json.dumps(logs, indent=4), encoding="utf-8")

            entries_count = len(logs[date_str][main_category][subcategory])
            if entries_count % self.BATCH_SIZE == 0:
                print(f"[BATCH COMPLETE] {entries_count} entries in {main_category} → {subcategory}")
                return self.generate_summary(date_str, main_category, subcategory)
            else:
                needed = self.BATCH_SIZE - (entries_count % self.BATCH_SIZE)
                print(f"[LOGGED] Entry {entries_count} for {main_category} → {subcategory}. Need {needed} more to form a batch.")
                return True

        except Exception as e:
            logging.error(f"Error in log_to_json: {e}")
            print(f"[ERROR] Failed to log to JSON: {e}")
            return False

    def get_summarized_count(self, date_str, main_category, subcategory):
        """
        Retrieves the count of entries that have already been summarized for a specific date, main category, 
        and subcategory. This helps to keep track of which entries still need summarization.

        Parameters:
            date_str (str): The date of the entries (YYYY-MM-DD).
            main_category (str): The main category of the entries.
            subcategory (str): The subcategory of the entries.

        Returns:
            int: The number of entries that have already been summarized for the given date, category, and subcategory.
        """
        try:
            if not self.correction_summaries_file.exists():
                self.correction_summaries_file.write_text("{}", encoding="utf-8")
            summaries = json.loads(self.correction_summaries_file.read_text(encoding="utf-8"))

            summarized_count = 0
            cat_summaries = summaries.get(date_str, {}).get(main_category, {}).get(subcategory, [])
            for batch_summary in cat_summaries:
                batch_range = batch_summary.get("batch", "")
                if "-" in batch_range:
                    try:
                        end_idx = int(batch_range.split("-")[1])
                        if end_idx > summarized_count:
                            summarized_count = end_idx
                    except ValueError:
                        print(f"[WARNING] Could not parse batch range: {batch_range}")
            return summarized_count
        except Exception as e:
            print(f"[ERROR] get_summarized_count failed: {e}")
            logging.error(f"get_summarized_count error: {e}")
            return 0

    def generate_summary(self, date_str, main_category, subcategory):
        """
        Generates a summary for a batch of unsummarized entries. The batch is based on the entries that have 
        been logged but not yet summarized, up to the specified batch size.

        Parameters:
            date_str (str): The date of the entries to summarize.
            main_category (str): The main category for the entries.
            subcategory (str): The subcategory for the entries.

        Returns:
            bool: True if the summary was generated successfully, False otherwise.
        """
        try:
            logs = json.loads(self.json_log_file.read_text(encoding="utf-8"))

            if not self.correction_summaries_file.exists():
                self.correction_summaries_file.write_text("{}", encoding="utf-8")
            summaries = json.loads(self.correction_summaries_file.read_text(encoding="utf-8"))

            if date_str not in summaries:
                summaries[date_str] = {}
            if main_category not in summaries[date_str]:
                summaries[date_str][main_category] = {}
            if subcategory not in summaries[date_str][main_category]:
                summaries[date_str][main_category][subcategory] = []

            all_entries = logs.get(date_str, {}).get(main_category, {}).get(subcategory, [])
            if not all_entries:
                print(f"[⚠️ SKIP] No entries found for {date_str} {main_category} → {subcategory}")
                return False

            summarized_count = self.get_summarized_count(date_str, main_category, subcategory)
            print(f"[INFO] Summarized count so far for {main_category} → {subcategory}: {summarized_count}")

            remaining_entries = all_entries[summarized_count:]
            remaining_count = len(remaining_entries)
            print(f"[INFO] {remaining_count} unsummarized entries remain in {main_category} → {subcategory}")

            if remaining_count <= 0:
                print(f"[SKIP] No new entries to summarize.")
                return False

            batch_size = min(self.BATCH_SIZE, remaining_count)
            batch_entries = remaining_entries[:batch_size]
            entry_texts = [entry["content"] for entry in batch_entries]

            if not entry_texts:
                print("[❌ ERROR] No content found to summarize.")
                return False

            summary = self.ai_summarizer.summarize_entries_bulk(entry_texts, subcategory=subcategory)
            if not summary:
                print(f"[❌ ERROR] AI summary returned empty. Prompt was: {entry_texts[:2]} ...")
                return False

            start_idx = summarized_count + 1
            end_idx = start_idx + batch_size - 1
            batch_label = f"{start_idx}-{end_idx}"

            summary_data = {
                "batch": batch_label,
                "original_summary": summary,
                "corrected_summary": "",
                "correction_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            summaries[date_str][main_category][subcategory].append(summary_data)
            self.correction_summaries_file.write_text(json.dumps(summaries, indent=4), encoding="utf-8")

            print(f"[✅ SUCCESS] Summarized {batch_size} new entries → {main_category} → {subcategory} (Batch {batch_label})")
            return True

        except Exception as e:
            logging.error(f"Error in generate_summary: {e}")
            print(f"[❌ ERROR] generate_summary crashed: {e}")
            import traceback
            print(traceback.format_exc())
            return False

    def log_to_markdown(self, date_str, main_category, subcategory, entry):
        """
        Logs an entry to a Markdown file, appending it to the relevant category and subcategory section. 
        It creates a new file if necessary or updates an existing file with the new entry.

        Parameters:
            date_str (str): The date of the entry.
            main_category (str): The main category of the entry.
            subcategory (str): The subcategory of the entry.
            entry (str): The content of the entry.

        Returns:
            bool: True if the entry was successfully logged to Markdown, False otherwise.
        """
        try:
            md_filename = self.safe_filename(main_category) + ".md"
            md_path = Path(self.export_dir) / md_filename
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
            logging.error(f"Error in log_to_markdown: {e}")
            print(f"[❌ ERROR] Failed to log to Markdown: {e}")
            return False

    def save_entry(self, main_category, subcategory, entry):
        """
        Saves an entry both to the JSON log file and the Markdown export. It triggers summary generation 
        if the required number of entries have been reached for that batch.

        Parameters:
            main_category (str): The main category of the entry.
            subcategory (str): The subcategory of the entry.
            entry (str): The content of the entry.

        Returns:
            bool: True if the entry was successfully saved to both JSON and Markdown, False otherwise.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_str = datetime.now().strftime("%Y-%m-%d")

        json_success = self.log_to_json(timestamp, date_str, main_category, subcategory, entry)
        md_success = self.log_to_markdown(date_str, main_category, subcategory, entry)
        return json_success and md_success
