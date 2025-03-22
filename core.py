import json
from pathlib import Path
from datetime import datetime
import logging
import re
from ai_summarizer import AISummarizer
import shutil

logging.basicConfig(
    level=logging.ERROR,
    filename="logs/zephyrus_logger_errors.log",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class ZephyrusLoggerCore:
    BATCH_SIZE = 10  # Number of entries before triggering AI summarization

    def __init__(self, script_dir):
        self.script_dir = Path(script_dir)
        self.log_dir = self.script_dir / "logs"
        self.export_dir = self.script_dir / "exports"
        self.json_log_file = self.log_dir / "zephyrus_log.json"
        self.txt_log_file = self.log_dir / "zephyrus_log.txt"
        self.correction_summaries_file = self.log_dir / "correction_summaries.json"
        self.ai_summarizer = AISummarizer()

        # 🔒 Backup correction_summaries.json before modification
        if self.correction_summaries_file.exists():
            shutil.copy(self.correction_summaries_file, self.log_dir / "correction_summaries_backup.json")

        self._initialize_environment()

    def _initialize_environment(self):
        """Ensure all directories and files exist before writing data."""
        self.log_dir.mkdir(exist_ok=True)
        self.export_dir.mkdir(exist_ok=True)

        if not self.json_log_file.exists():
            self.json_log_file.write_text("{}", encoding="utf-8")

        if not self.txt_log_file.exists():
            self.txt_log_file.write_text("=== Zephyrus Idea Logger ===\n", encoding="utf-8")

        if not self.correction_summaries_file.exists():
            self.correction_summaries_file.write_text("{}", encoding="utf-8")

    @staticmethod
    def safe_filename(text):
        return re.sub(r'[\\/*?:"<>|]', "_", text.replace(" ", "_"))

    def log_to_json(self, timestamp, date_str, main_category, subcategory, entry):
        """Logs the entry into JSON, triggers AI summarization if batch size is reached."""
        logs = json.loads(self.json_log_file.read_text(encoding="utf-8"))
        logs.setdefault(date_str, {}).setdefault(main_category, {}).setdefault(subcategory, [])

        logs[date_str][main_category][subcategory].append({"timestamp": timestamp, "content": entry})

        self.json_log_file.write_text(json.dumps(logs, indent=4), encoding="utf-8")

        # 🚀 **Trigger AI summarization if batch size is reached**
        if len(logs[date_str][main_category][subcategory]) % self.BATCH_SIZE == 0:
            self.generate_summary(date_str, main_category, subcategory)

        return True

    def generate_summary(self, date_str, main_category, subcategory):
        """Generates an AI summary for the last batch of entries."""
        logs = json.loads(self.json_log_file.read_text(encoding="utf-8"))
        summaries = json.loads(self.correction_summaries_file.read_text(encoding="utf-8"))

        summaries.setdefault(date_str, {}).setdefault(main_category, {}).setdefault(subcategory, [])

        entries = logs[date_str][main_category][subcategory][-self.BATCH_SIZE:]  # Get last batch
        entry_texts = [entry["content"] for entry in entries]

        # 🚀 AI-Generated Summary
        summary = self.ai_summarizer.summarize_entries_bulk(entry_texts)
        if not summary:
            return False  # Skip if summarization fails

        batch_label = f"{len(summaries[date_str][main_category][subcategory]) * self.BATCH_SIZE + 1}-{len(entries)}"

        summary_data = {
            "batch": batch_label,
            "original_summary": summary,
            "corrected_summary": "",  # User-corrected summary field
            "correction_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        summaries[date_str][main_category][subcategory].append(summary_data)
        self.correction_summaries_file.write_text(json.dumps(summaries, indent=4), encoding="utf-8")

        return True

    def log_to_markdown(self, date_str, main_category, subcategory, entry):
        """Logs entry to markdown with batch summarization."""
        md_filename = self.safe_filename(main_category) + ".md"
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

    def save_entry(self, main_category, subcategory, entry):
        """Saves a new idea entry and triggers necessary summarization."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_str = datetime.now().strftime("%Y-%m-%d")

        json_success = self.log_to_json(timestamp, date_str, main_category, subcategory, entry)
        md_success = self.log_to_markdown(date_str, main_category, subcategory, entry)

        return json_success and md_success
