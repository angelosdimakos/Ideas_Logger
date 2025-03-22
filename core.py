import json
from pathlib import Path
from datetime import datetime
import logging
import re
from ai_summarizer import AISummarizer
import shutil
from summary_indexer import SummaryIndexer

logging.basicConfig(
    level=logging.ERROR,
    filename="logs/zephyrus_logger_errors.log",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class ZephyrusLoggerCore:
    def __init__(self, script_dir):
        self.script_dir = Path(script_dir)
        self.log_dir = self.script_dir / "logs"
        self.export_dir = self.script_dir / "exports"
        self.json_log_file = self.log_dir / "zephyrus_log.json"
        self.txt_log_file = self.log_dir / "zephyrus_log.txt"
        self.correction_summaries_file = self.log_dir / "correction_summaries.json"
        self.config_file = self.script_dir / "config.json"
        self.ai_summarizer = AISummarizer()

        # Backup correction_summaries if exists
        if self.correction_summaries_file.exists():
            shutil.copy(self.correction_summaries_file, self.log_dir / "correction_summaries_backup.json")

        self._initialize_environment()
        self.BATCH_SIZE = self._load_batch_size()

    def _initialize_environment(self):
        self.log_dir.mkdir(exist_ok=True)
        self.export_dir.mkdir(exist_ok=True)

        if not self.json_log_file.exists():
            self.json_log_file.write_text("{}", encoding="utf-8")

        if not self.txt_log_file.exists():
            self.txt_log_file.write_text("=== Zephyrus Idea Logger ===\n", encoding="utf-8")

        if not self.correction_summaries_file.exists():
            self.correction_summaries_file.write_text("{}", encoding="utf-8")

        if not self.config_file.exists():
            default_config = {"batch_size": 5}
            self.config_file.write_text(json.dumps(default_config, indent=4), encoding="utf-8")

    def _load_batch_size(self):
        try:
            config = json.loads(self.config_file.read_text(encoding="utf-8"))
            return config.get("batch_size", 5)
        except Exception as e:
            logging.error(f"Config Load Error: {e}")
            return 5

    @staticmethod
    def safe_filename(text):
        return re.sub(r'[\\/*?:"<>|]', "_", text.replace(" ", "_"))

    def log_to_json(self, timestamp, date_str, main_category, subcategory, entry):
        """Log an entry to JSON, then check if we need summarization."""
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
        """Count how many entries have been summarized so far from correction_summaries."""
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
        """Actually generate the summary for any unsummarized entries."""
        try:
            logs = json.loads(self.json_log_file.read_text(encoding="utf-8"))

            if not self.correction_summaries_file.exists():
                self.correction_summaries_file.write_text("{}", encoding="utf-8")
            summaries = json.loads(self.correction_summaries_file.read_text(encoding="utf-8"))

            # Ensure correction structure
            if date_str not in summaries:
                summaries[date_str] = {}
            if main_category not in summaries[date_str]:
                summaries[date_str][main_category] = {}
            if subcategory not in summaries[date_str][main_category]:
                summaries[date_str][main_category][subcategory] = []

            # All entries for that group
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

            # Summarize exactly self.BATCH_SIZE or whatever remains
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

            # Calculate next batch range
            start_idx = summarized_count + 1
            end_idx = start_idx + batch_size - 1
            batch_label = f"{start_idx}-{end_idx}"

            summary_data = {
                "batch": batch_label,
                "original_summary": summary,
                "corrected_summary": "",
                "correction_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Save the summary
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
        
        # Trigger FAISS update
        indexer = SummaryIndexer(
                                summaries_path=self.correction_summaries_file,
                                index_path=self.script_dir / "vector_store/summary_index.faiss",
                                metadata_path=self.script_dir / "vector_store/summary_metadata.pkl"
                                                                            )
        indexer.build_index()

    def log_to_markdown(self, date_str, main_category, subcategory, entry):
        """Write the idea to the relevant MD file."""
        try:
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

        except Exception as e:
            logging.error(f"Error in log_to_markdown: {e}")
            print(f"[❌ ERROR] Failed to log to Markdown: {e}")
            return False

    def save_entry(self, main_category, subcategory, entry):
        """Public method to log the new idea (JSON + MD). If batch is complete, generate summary."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_str = datetime.now().strftime("%Y-%m-%d")

        json_success = self.log_to_json(timestamp, date_str, main_category, subcategory, entry)
        md_success = self.log_to_markdown(date_str, main_category, subcategory, entry)

        return json_success and md_success
