"""
Summary Engine Module
===============================
This module provides the SummaryEngine class, which is responsible
for generating summaries from log entries using AI summarization.
It integrates with the log manager and summary tracker to manage
the summarization process.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from scripts.ai.ai_summarizer import AISummarizer
from scripts.core.log_manager import LogManager
from scripts.core.summary_tracker import SummaryTracker

logger = logging.getLogger(__name__)


class SummaryEngine:
    """
    A class to manage the summarization of log entries.

    This class utilizes an AI summarizer to generate summaries from
    batches of log entries, coordinating with the log manager and
    summary tracker.

    Attributes:
        summarizer (AISummarizer): The AI summarizer instance.
        log_manager (LogManager): The log manager instance.
        tracker (SummaryTracker): The summary tracker instance.
        timestamp_format (str): The format for timestamps.
        content_key (str): The key for content in log entries.
        timestamp_key (str): The key for timestamps in log entries.
        batch_size (int): The number of entries to process in a batch.
    """

    def __init__(
        self,
        summarizer: AISummarizer,
        log_manager: LogManager,
        summary_tracker: SummaryTracker,
        timestamp_format: str,
        content_key: str,
        timestamp_key: str,
        batch_size: int,
    ) -> None:
        """
        Initialize the SummaryEngine.

        Parameters:
            summarizer (AISummarizer): The AI summarizer instance.
            log_manager (LogManager): The log manager instance.
            summary_tracker (SummaryTracker): The summary tracker instance.
            timestamp_format (str): The format for timestamps.
            content_key (str): The key for content in log entries.
            timestamp_key (str): The key for timestamps in log entries.
            batch_size (int): The number of entries to process in a batch.
        """
        self.summarizer = summarizer
        self.log_manager = log_manager
        self.tracker = summary_tracker
        self.timestamp_format = timestamp_format
        self.content_key = content_key
        self.timestamp_key = timestamp_key
        self.batch_size = batch_size

    def _get_summary(self, batch_entries: List[Dict[str, Any]], subcategory: str) -> Optional[str]:
        """
        Generate a summary from a batch of log entries.

        Parameters:
            batch_entries (List[Dict[str, Any]]): The batch of log entries.
            subcategory (str): The subcategory for the summary.

        Returns:
            Optional[str]: The generated summary, or None if summarization fails.
        """
        try:
            content = [entry[self.content_key] for entry in batch_entries]
            summary = self.summarizer.summarize_entries_bulk(content, subcategory=subcategory)
        except Exception as e:
            logger.error("AI summarization failed: %s", e, exc_info=True)
            try:
                summary = self.summarizer._fallback_summary("\n".join(content))
            except Exception as fallback_e:
                logger.error("Fallback summarization failed: %s", fallback_e, exc_info=True)
                return None
        return summary.strip() if summary and summary.strip() else None

    def summarize(self, main_category: str, subcategory: str) -> bool:
        """
        Summarize log entries for a given main category and subcategory.

        Parameters:
            main_category (str): The main category for the summary.
            subcategory (str): The subcategory for the summary.

        Returns:
            bool: True if summarization is successful, False otherwise.
        """
        summarized_count = self.tracker.get_summarized_count(main_category, subcategory)
        batch = self.log_manager.get_unsummarized_batch(
            main_category, subcategory, summarized_count, self.batch_size
        )

        if len(batch) < self.batch_size:
            logger.info("[SKIP] Not enough entries for %s → %s", main_category, subcategory)
            return False

        summary = self._get_summary(batch, subcategory)
        if not summary:
            logger.error("[ERROR] AI returned empty summary.")
            return False

        start_ts = batch[0][self.timestamp_key]
        end_ts = batch[-1][self.timestamp_key]
        label = f"{start_ts} → {end_ts}"

        record = {
            "batch": label,
            "original_summary": summary,
            "corrected_summary": "",
            "correction_timestamp": datetime.now().strftime(self.timestamp_format),
            "start": start_ts,
            "end": end_ts,
        }

        try:
            self.log_manager.update_correction_summaries(main_category, subcategory, record)
            self.tracker.update(main_category, subcategory, summarized=self.batch_size)
            logger.info("[SUCCESS] Summary written for %s → %s", main_category, subcategory)
            return True
        except Exception as e:
            logger.error("[ERROR] Failed to save summary: %s", e, exc_info=True)
            return False
