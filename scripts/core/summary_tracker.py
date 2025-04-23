"""
summary_tracker.py

This module provides the SummaryTracker class for managing and tracking summaries of logs.
It includes functionality for loading tracker data, initializing indexers, and maintaining
the state of summaries. This module is essential for the Zephyrus Logger application to
manage summaries effectively.

Dependencies:
- json
- logging
- pathlib
- collections (defaultdict)
- scripts.indexers.summary_indexer
- scripts.indexers.raw_log_indexer
- scripts.utils.file_utils
- scripts.paths.ZephyrusPaths
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, DefaultDict
from collections import defaultdict

from scripts.indexers.summary_indexer import SummaryIndexer
from scripts.indexers.raw_log_indexer import RawLogIndexer
from scripts.utils.file_utils import read_json, write_json
from scripts.paths import ZephyrusPaths

logger = logging.getLogger(__name__)


class SummaryTracker:
    """
    SummaryTracker manages the loading, initialization, and tracking of summary data for logs.

    Attributes:
        paths (ZephyrusPaths): The paths configuration for the summary tracker.
        tracker_path (Path): The path to the summary tracker file.
        tracker (Dict[str, Dict[str, Any]]): The loaded tracker data.
        summary_indexer (Optional[SummaryIndexer]): The indexer for summaries.
        raw_indexer (Optional[RawLogIndexer]): The indexer for raw logs.
    """

    def __init__(self, paths: ZephyrusPaths) -> None:
        """
        Initializes the SummaryTracker with the given paths.

        Args:
            paths (ZephyrusPaths): The paths configuration for the summary tracker.
        """
        self.paths = paths
        self.tracker_path = paths.summary_tracker_file
        self.tracker: Dict[str, Dict[str, Any]] = self._safe_load_tracker()
        self.summary_indexer = self._safe_init_summary_indexer()
        self.raw_indexer = self._safe_init_raw_indexer()

    def _safe_load_tracker(self) -> Dict[str, Dict[str, Any]]:
        """
        Safely loads the tracker data from the tracker file.

        Returns:
            Dict[str, Dict[str, Any]]: The loaded tracker data, or an empty dictionary if loading fails.
        """
        try:
            if self.tracker_path.exists() and self.tracker_path.stat().st_size > 0:
                return read_json(self.tracker_path)
            else:
                logger.warning("Tracker file missing or empty: %s", self.tracker_path)
        except Exception as e:
            logger.error("Failed to read tracker file: %s", e, exc_info=True)
        return {}

    def _safe_init_summary_indexer(self) -> Optional[SummaryIndexer]:
        """
        Safely initializes the SummaryIndexer.

        Returns:
            Optional[SummaryIndexer]: The initialized SummaryIndexer, or None if initialization fails.
        """
        try:
            return SummaryIndexer(paths=self.paths)
        except Exception as e:
            logger.error("Failed to initialize SummaryIndexer: %s", e, exc_info=True)
            return None

    def _safe_init_raw_indexer(self) -> Optional[RawLogIndexer]:
        """
        Safely initializes the RawLogIndexer.

        Returns:
            Optional[RawLogIndexer]: The initialized RawLogIndexer, or None if initialization fails.
        """
        try:
            return RawLogIndexer(paths=self.paths)
        except Exception as e:
            logger.error("Failed to initialize RawLogIndexer: %s", e, exc_info=True)
            return None

    def get_summarized_count(self, main_category: str, subcategory: str) -> int:
        """
        Retrieves the summarized count for the given main category and subcategory.

        Args:
            main_category (str): The main category.
            subcategory (str): The subcategory.

        Returns:
            int: The summarized count.
        """
        return self.tracker.get(main_category, {}).get(subcategory, {}).get("summarized_total", 0)

    def update(
        self, main_category: str, subcategory: str, summarized: int = 0, new_entries: int = 0
    ) -> None:
        """
        Updates the tracker with the given summarized and new entries counts.

        Args:
            main_category (str): The main category.
            subcategory (str): The subcategory.
            summarized (int, optional): The summarized count. Defaults to 0.
            new_entries (int, optional): The new entries count. Defaults to 0.
        """
        logger.debug(
            f"Updating {main_category} → {subcategory} | Summarized: {summarized}, New: {new_entries}"
        )
        self.tracker.setdefault(main_category, {}).setdefault(
            subcategory, {"summarized_total": 0, "logged_total": 0}
        )
        self.tracker[main_category][subcategory]["summarized_total"] += summarized
        self.tracker[main_category][subcategory]["logged_total"] += new_entries
        self._save()

    def _save(self) -> None:
        """
        Saves the tracker data to the tracker file.
        """
        try:
            write_json(self.tracker_path, self.tracker)
        except Exception as e:
            logger.error("Failed to write tracker to disk: %s", e, exc_info=True)

    def rebuild(self) -> None:
        """
        Rebuilds the tracker by clearing the current data and re-counting the logged and summarized entries.
        """
        self.tracker.clear()

        raw_logs_data = read_json(self.paths.json_log_file)
        summaries_data = read_json(self.paths.correction_summaries_file)

        # === Count Logged ===
        for date, categories in raw_logs_data.items():
            for main_cat, subcats in categories.items():
                for subcat, entries in subcats.items():
                    self.update(main_cat, subcat, new_entries=len(entries))

        # === Count Summarized ===
        summarized_counts: DefaultDict[str, DefaultDict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        for date, categories in summaries_data.items():
            for main_cat, subcats in categories.items():
                for subcat, summaries in subcats.items():
                    for summary in summaries:
                        if summary.get("corrected_summary") or summary.get("original_summary"):
                            summarized_counts[main_cat][subcat] += 1

        for main_cat, subcats in summarized_counts.items():
            for subcat, summarized in subcats.items():
                self.update(main_cat, subcat, summarized=summarized)

        if self.summary_indexer:
            self.summary_indexer.rebuild()
        if self.raw_indexer:
            self.raw_indexer.rebuild()

    def validate(self, verbose: bool = False) -> bool:
        """
        Validates the tracker by comparing the summarized counts with the actual counts in the correction summaries.

        Args:
            verbose (bool, optional): If True, logs every subcategory status. Otherwise, only logs mismatches. Defaults to False.

        Returns:
            bool: True if the tracker is valid (no mismatches), False otherwise.
        """
        if not self.tracker:
            logger.warning("[VALIDATION] Tracker is empty; triggering rebuild.")
            return False

        try:
            data = read_json(self.paths.correction_summaries_file)
            valid = True

            for date, categories in data.items():
                for main_cat, subcats in categories.items():
                    for subcat, batches in subcats.items():
                        expected = sum(
                            1
                            for batch in batches
                            if batch.get("corrected_summary") or batch.get("original_summary")
                        )
                        actual = self.get_summarized_count(main_cat, subcat)

                        if expected != actual:
                            logger.warning(
                                "[VALIDATION] ❌ Mismatch in %s → %s | tracker=%d vs actual=%d",
                                main_cat,
                                subcat,
                                actual,
                                expected,
                            )
                            valid = False
                        elif verbose:
                            logger.info(
                                "[VALIDATION] ✅ %s → %s | tracker=%d", main_cat, subcat, actual
                            )

            if valid:
                logger.info("[VALIDATION] ✅ All tracker counts match correction summaries.")
            else:
                logger.error("[VALIDATION] ❌ Tracker has mismatches. Rebuild may be needed.")

            return valid

        except Exception as e:
            logger.error("Failed to validate summary tracker: %s", e, exc_info=True)
            return False

    def get_coverage_data(self) -> list[dict]:
        """
        Returns a structured list of coverage data for all tracked (main, sub) categories.

        Each entry includes:
        - main_category
        - subcategory
        - logged_total
        - estimated_summarized_entries
        - coverage_percent (0–100)
        """
        from scripts.config.config_loader import get_effective_config, get_config_value

        config = get_effective_config()
        batch_size = int(get_config_value(config, "batch_size", 5))

        data = []
        for main_cat, subcats in self.tracker.items():
            for subcat, counts in subcats.items():
                logged = counts.get("logged_total", 0)
                summarized_batches = counts.get("summarized_total", 0)
                estimated_entries = summarized_batches * batch_size
                coverage = (estimated_entries / logged) * 100 if logged > 0 else 0
                data.append(
                    {
                        "main_category": main_cat,
                        "subcategory": subcat,
                        "logged_total": logged,
                        "estimated_summarized_entries": estimated_entries,
                        "coverage_percent": round(coverage, 2),
                    }
                )
        return data
