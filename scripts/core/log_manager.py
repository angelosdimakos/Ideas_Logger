from pathlib import Path
from datetime import datetime
import logging
from scripts.utils.file_utils import read_json, write_json

logger = logging.getLogger(__name__)

class LogManager:
    def __init__(self, json_log_file: Path, txt_log_file: Path, correction_summaries_file: Path,
                 timestamp_format: str, content_key: str, timestamp_key: str):
        """
        Initializes a LogManager instance.

        Args:
            json_log_file (Path): Path to the JSON file that stores log entries.
            txt_log_file (Path): Path to the text file that stores log entries in plain text.
            correction_summaries_file (Path): Path to the JSON file that stores correction summaries.
            timestamp_format (str): Timestamp format for log entries.
            content_key (str): Key used to store the content of a log entry in the JSON file.
            timestamp_key (str): Key used to store the timestamp of a log entry in the JSON file.
        """
        self.json_log_file = json_log_file
        self.txt_log_file = txt_log_file
        self.correction_summaries_file = correction_summaries_file
        self.timestamp_format = timestamp_format
        self.content_key = content_key
        self.timestamp_key = timestamp_key

    def _safe_read_or_create_json(self, filepath: Path) -> dict:
        """
        Safely reads a JSON file or creates it if it doesn't exist.
        If the file doesn't exist, it will create an empty JSON object.

        Args:
            filepath (Path): Path to the JSON file.

        Returns:
            dict: The parsed JSON data or an empty dictionary if the file couldn't be loaded.
        """
        if not filepath.exists():
            logger.info(f"File '{filepath}' not found. Creating new file.")
            # Create an empty JSON file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("{}")

        try:
            return read_json(filepath)
        except Exception as e:
            logger.error(f"Failed to read or parse file '{filepath}': {e}")
            return {}


    def read_logs(self) -> dict:
        """
        Reads the JSON log file and returns its contents. If the file doesn't exist, it will create an empty JSON object.

        Returns:
            dict: The parsed JSON data or an empty dictionary if the file couldn't be loaded.
        """

        return self._safe_read_or_create_json(self.json_log_file)

    def update_logs(self, update_func) -> None:

        """
        Updates the JSON log file with the provided update function.

        The update function will be provided with the current JSON data as a dictionary.
        The function should modify the dictionary in-place as needed.

        Args:
            update_func (Callable[[dict], None]): The function to call to update the JSON data.
        """
        data = self.read_logs()
        update_func(data)
        write_json(self.json_log_file, data)

    def append_entry(self, date_str: str, main_category: str, subcategory: str, entry: str) -> None:

        """
        Appends a new log entry to the JSON log file.

        Args:
            date_str (str): The date of the log entry in the format specified by `timestamp_format`.
            main_category (str): The main category of the log entry.
            subcategory (str): The subcategory of the log entry.
            entry (str): The content of the log entry.
        """
        def updater(data: dict) -> None:

            """
            Updates the JSON data to append a new log entry.

            Args:
                data (dict): The current JSON data.
            """
            data.setdefault(date_str, {})\
                .setdefault(main_category, {})\
                .setdefault(subcategory, [])\
                .append({self.timestamp_key: datetime.now().strftime(self.timestamp_format),
                         self.content_key: entry})
        self.update_logs(updater)

    def get_unsummarized_batch(self, main_category: str, subcategory: str, summarized_total: int, batch_size: int) -> list:

        """
        Retrieves a batch of unsummarized log entries for the given main category and subcategory.

        Args:
            main_category (str): The main category of the log entries.
            subcategory (str): The subcategory of the log entries.
            summarized_total (int): The total number of log entries that have already been summarized.
            batch_size (int): The number of unsummarized log entries to retrieve in the batch.

        Returns:
            list: A list of log entries, each represented as a dictionary with 'timestamp' and 'content' keys.
        """
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

        """
        Updates the correction summaries JSON file with new data.

        Args:
            main_category (str): The main category of the log entries.
            subcategory (str): The subcategory of the log entries.
            new_data (dict): The new data to append to the correction summaries.
                The dictionary should contain the following keys:
                    - "batch": The batch label.
                    - "original_summary": The original summary.
                    - "corrected_summary": The corrected summary.
                    - "correction_timestamp": The timestamp of the correction.
                    - "start": The start timestamp of the batch.
                    - "end": The end timestamp of the batch.
        """
        data = self._safe_read_or_create_json(self.correction_summaries_file)
        data.setdefault("global", {})\
            .setdefault(main_category, {})\
            .setdefault(subcategory, [])\
            .append(new_data)
        write_json(self.correction_summaries_file, data)
