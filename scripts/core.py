import json
from pathlib import Path
from datetime import datetime
import logging
import re
from scripts.ai_summarizer import AISummarizer
from scripts.summary_indexer import SummaryIndexer
from scripts.config_loader import load_config, get_config_value, get_absolute_path
from utils.file_utils import sanitize_filename, safe_path, write_json, read_json, make_backup

logging.basicConfig(
    level=logging.ERROR,
    filename="logs/zephyrus_logger_errors.log",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class ZephyrusLoggerCore:
    def __init__(self, script_dir):
        self.config = load_config()
        self.script_dir = Path(script_dir)
        self.log_dir = Path(get_absolute_path(get_config_value(self.config, "logs_dir", self.script_dir / "logs")))
        self.export_dir = Path(get_absolute_path(get_config_value(self.config, "export_dir", self.script_dir / "exports")))
        self.json_log_file = Path(self.log_dir) / "zephyrus_log.json"
        self.txt_log_file = Path(self.log_dir) / "zephyrus_log.txt"
        self.correction_summaries_file = Path(self.log_dir) / "correction_summaries.json"
        self.config_file = Path(get_absolute_path("config/config.json"))
        self.ai_summarizer = AISummarizer()

        if self.correction_summaries_file.exists():
            make_backup(self.correction_summaries_file)

        self._initialize_environment()
        self.BATCH_SIZE = int(get_config_value(self.config, "batch_size", 5))


    def _initialize_environment(self):
        Path(self.log_dir).mkdir(exist_ok=True, parents=True)
        Path(self.export_dir).mkdir(exist_ok=True, parents=True)

        if not self.json_log_file.exists():
            write_json(self.json_log_file, {})

        if not self.txt_log_file.exists():
            self.txt_log_file.write_text("=== Zephyrus Idea Logger ===\n", encoding="utf-8")

        if not self.correction_summaries_file.exists():
            write_json(self.correction_summaries_file, {})

        if not self.config_file.exists():
            Path(self.config_file).parent.mkdir(parents=True, exist_ok=True)
            write_json(self.config_file, {"batch_size": 5})

    def log_to_json(self, timestamp, date_str, main_category, subcategory, entry):
        try:
            logs = read_json(self.json_log_file)

            logs.setdefault(date_str, {}).setdefault(main_category, {}).setdefault(subcategory, [])
            logs[date_str][main_category][subcategory].append({"timestamp": timestamp, "content": entry})
            write_json(self.json_log_file, logs)

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
        try:
            if not self.correction_summaries_file.exists():
                write_json(self.correction_summaries_file, {})
            summaries = read_json(self.correction_summaries_file)

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
        try:
            logs = read_json(self.json_log_file)

            if not self.correction_summaries_file.exists():
                write_json(self.correction_summaries_file, {})
            summaries = read_json(self.correction_summaries_file)

            summaries.setdefault(date_str, {}).setdefault(main_category, {}).setdefault(subcategory, [])
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

            try:
                # Attempt to summarize entries using AI model
                summary = self.ai_summarizer.summarize_entries_bulk(entry_texts, subcategory=subcategory)
            except Exception as e:
                # If the AI summarization fails, call the fallback
                print(f"[❌ ERROR] AI summarization failed: {e}. Falling back to alternative method.")
                summary = self.ai_summarizer._fallback_summary("\n".join(entry_texts))
            
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
            write_json(self.correction_summaries_file, summaries)

            print(f"[✅ SUCCESS] Summarized {batch_size} new entries → {main_category} → {subcategory} (Batch {batch_label})")
            return True

        except Exception as e:
            logging.error(f"Error in generate_summary: {e}")
            print(f"[❌ ERROR] generate_summary crashed: {e}")
            import traceback
            print(traceback.format_exc())
            return False


    def log_to_markdown(self, date_str, main_category, subcategory, entry):
        try:
            md_filename = sanitize_filename(main_category) + ".md"
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
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_str = datetime.now().strftime("%Y-%m-%d")

        json_success = self.log_to_json(timestamp, date_str, main_category, subcategory, entry)
        md_success = self.log_to_markdown(date_str, main_category, subcategory, entry)
        return json_success and md_success
