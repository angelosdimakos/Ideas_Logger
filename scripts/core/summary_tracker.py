import logging
from pathlib import Path
from scripts.utils.file_utils import read_json, write_json
from scripts.indexers.summary_indexer import SummaryIndexer
from scripts.indexers.raw_log_indexer import RawLogIndexer
from scripts.paths import ZephyrusPaths

logger = logging.getLogger(__name__)


class SummaryTracker:
    """
    Handles operations related to the summary tracker including loading,
    validating, updating, rebuilding from the JSON log, and querying counts.
    The tracker is expected to have the following structure:

        {
            "main_category": {
                "sub_category": {"logged_total": int, "summarized_total": int},
                ...
            },
            ...
        }
    """

    def __init__(self, paths: ZephyrusPaths):
        """
        Args:
            paths (ZephyrusPaths): An instance containing all relevant file paths.
        """
        self.paths = paths
        self.tracker = self._load_tracker()
        self.summary_indexer = SummaryIndexer(summaries_path=str(self.paths.correction_summaries_file))
        self.raw_indexer = RawLogIndexer(log_path=str(self.paths.json_log_file))

    def _load_tracker(self) -> dict:
        if not self.paths.summary_tracker_file.exists():
            return {}
        try:
            tracker = read_json(self.paths.summary_tracker_file)
            if not self.validate(tracker):
                logger.warning("Invalid tracker format detected. Initializing empty tracker.")
                return {}
            return tracker
        except Exception as e:
            logger.error("Error loading summary tracker: %s", e, exc_info=True)
            return {}

    @staticmethod
    def validate(tracker: dict) -> bool:
        """
        Validate the structure of the tracker.

        Returns:
            bool: True if tracker is valid, False otherwise.
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

    def save(self):
        try:
            write_json(self.paths.summary_tracker_file, self.tracker)
        except Exception as e:
            logger.error("Error saving summary tracker: %s", e, exc_info=True)

    def update(self, main_category: str, subcategory: str, new_entries: int = 0, summarized: int = 0):
        """
        Update the tracker for a given category/subcategory.

        Args:
            main_category (str): The main category.
            subcategory (str): The subcategory.
            new_entries (int): Number of new logged entries.
            summarized (int): Number of entries summarized.
        """
        self.tracker.setdefault(main_category, {}).setdefault(subcategory, {"logged_total": 0, "summarized_total": 0})
        self.tracker[main_category][subcategory]["logged_total"] += new_entries
        self.tracker[main_category][subcategory]["summarized_total"] += summarized
        self.save()

    def rebuild(self):
        """
        Rebuild the tracker by parsing the JSON logs file.
        """
        try:
            logs = read_json(self.paths.json_log_file)
            new_tracker = {}
            for date, categories in logs.items():
                for main_cat, subcats in categories.items():
                    for subcat, entries in subcats.items():
                        count = len(entries)
                        new_tracker.setdefault(main_cat, {}).setdefault(subcat,
                                                                        {"logged_total": 0, "summarized_total": 0})
                        new_tracker[main_cat][subcat]["logged_total"] += count
            self.tracker = new_tracker
            self.save()
            logger.info("Rebuilt summary tracker with %d main categories.", len(new_tracker))
        except Exception as e:
            logger.error("Failed to rebuild summary tracker from logs: %s", e, exc_info=True)
            self.tracker = {}
            self.save()

    def get_summarized_count(self, main_category: str, subcategory: str) -> int:
        """
        Retrieve the number of summarized entries for the specified category/subcategory.
        """
        return self.tracker.get(main_category, {}).get(subcategory, {}).get("summarized_total", 0)
