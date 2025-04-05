from pathlib import Path
from datetime import datetime
import logging
from scripts.utils.file_utils import read_json, write_json

logger = logging.getLogger(__name__)

class LogManager:
    def __init__(self, json_log_file: Path, txt_log_file: Path, correction_summaries_file: Path,
                 timestamp_format: str, content_key: str, timestamp_key: str):
        self.json_log_file = json_log_file
        self.txt_log_file = txt_log_file
        self.correction_summaries_file = correction_summaries_file
        self.timestamp_format = timestamp_format
        self.content_key = content_key
        self.timestamp_key = timestamp_key

    def read_logs(self) -> dict:
        try:
            return read_json(self.json_log_file)
        except Exception as e:
            logger.error("Error reading logs: %s", e, exc_info=True)
            return {}

    def update_logs(self, update_func) -> None:
        data = self.read_logs()
        update_func(data)
        write_json(self.json_log_file, data)

    def append_entry(self, date_str: str, main_category: str, subcategory: str, entry: str) -> None:
        def updater(data: dict) -> None:
            data.setdefault(date_str, {})\
                .setdefault(main_category, {})\
                .setdefault(subcategory, [])\
                .append({self.timestamp_key: datetime.now().strftime(self.timestamp_format),
                         self.content_key: entry})
        self.update_logs(updater)

    def get_unsummarized_batch(self, main_category: str, subcategory: str, summarized_total: int, batch_size: int) -> list:
        logs = self.read_logs()
        entries = []
        count = 0
        for date in sorted(logs.keys()):
            for entry in logs[date].get(main_category, {}).get(subcategory, []):
                if count >= summarized_total:
                    entries.append(entry)
                    if len(entries) == batch_size:
                        return entries
                count += 1
        return []

    def update_correction_summaries(self, main_category: str, subcategory: str, new_data: dict) -> None:
        try:
            data = read_json(self.correction_summaries_file)
        except Exception as e:
            logger.error("Error reading correction summaries: %s", e, exc_info=True)
            data = {}
        data.setdefault("global", {})\
            .setdefault(main_category, {})\
            .setdefault(subcategory, [])\
            .append(new_data)
        write_json(self.correction_summaries_file, data)



