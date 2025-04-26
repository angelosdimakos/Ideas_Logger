"""
This module provides the AISummarizer class for generating summaries of text entries
using a configurable large language model (LLM).

It supports both single-entry and bulk summarization, with the ability to use
subcategory-specific prompts loaded from configuration. If the primary summarization
method fails, the module falls back to the Ollama chat API to attempt summarization.
Logging is integrated throughout for monitoring and debugging,
and configuration is loaded at initialization for flexible model and prompt management.

Typical use cases include automated summarization of logs, notes, or other textual data
in workflows requiring concise, context-aware summaries.
"""

import ollama
import logging
from requests.exceptions import RequestException
from scripts.config.config_loader import load_config, get_config_value
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class AISummarizer:
    """
    AISummarizer provides methods to generate summaries for single or multiple text entries
    using a configurable LLM model and subcategory-specific prompts. It supports fallback
    to the Ollama chat API if primary summarization fails and loads configuration settings
    at initialization.
    """

    def __init__(self) -> None:
        """
        Initialize AISummarizer by loading configuration, setting the LLM model,
        and preparing prompts by subcategory.
        """
        config: Dict[str, Any] = load_config()
        self.model: str = get_config_value(config, "llm_model", "mistral")
        self.prompts_by_subcategory: Dict[str, Any] = get_config_value(
            config, "prompts_by_subcategory", {}
        )
        logger.info("[INIT] AISummarizer initialized with model: %s", self.model)

    def _fallback_summary(self, full_prompt: str) -> str:
        """
        Attempt to generate a summary using the Ollama chat API as a fallback when
        primary summarization fails.

        Args:
            full_prompt (str): The prompt to send to the chat model.

        Returns:
            str: The generated summary or an error message.
        """
        logger.info("[AI] Attempting fallback approach (chat)")
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": full_prompt}]
            )
            content = response.get("message", {}).get("content", "")
            return (
                content.strip() if isinstance(content, str)
                else "Fallback failed: Invalid format"
            )
        except (KeyError, TypeError, RequestException) as e:
            logger.error("[FallbackError] Ollama fallback failed: %s", e, exc_info=True)
            return "Fallback failed: Ollama not available"

    def summarize_entry(self, entry_text: str, subcategory: Optional[str] = None) -> str:
        """
        Generate a summary for a single text entry using the configured LLM model
        and an optional subcategory-specific prompt.

        Args:
            entry_text (str): The text to summarize.
            subcategory (Optional[str], optional): The subcategory to use for the prompt.

        Returns:
            str: The generated summary or a fallback message if summarization fails.
        """
        prompt: str = self.prompts_by_subcategory.get(
            subcategory,
            self.prompts_by_subcategory.get("_default", "Summarize this:")
        ).strip()
        full_prompt: str = f"{prompt}\n\n{entry_text}"

        try:
            logger.debug("[AI] Single-entry prompt:\n%s", full_prompt)
            response = ollama.generate(model=self.model, prompt=full_prompt)
            result: str = response.get("response")
            return (
                result.strip() if isinstance(result, str)
                else self._fallback_summary(full_prompt)
            )
        except Exception as e:
            logger.warning("summarize_entry failed: %s", e, exc_info=True)
            return self._fallback_summary(full_prompt)

    def summarize_entries_bulk(self, entries: List[str], subcategory: Optional[str] = None) -> str:
        """
        Generate a summary for a list of text entries using the configured LLM model
        and subcategory-specific prompts.

        Args:
            entries (List[str]): The list of text entries to summarize.
            subcategory (Optional[str], optional): The subcategory to use for the prompt.

        Returns:
            str: The generated summary or a fallback message if summarization fails.
        """
        if not entries:
            logger.warning("[EmptyInput] summarize_entries_bulk received empty list")
            return "No entries provided"

        prompt_intro: str = self.prompts_by_subcategory.get(
            subcategory,
            self.prompts_by_subcategory.get("_default", "Summarize these points:")
        ).strip()
        combined_text: str = "\n".join(f"- {entry}" for entry in entries)
        full_prompt: str = f"{prompt_intro}\n\n{combined_text}"

        try:
            response = ollama.generate(model=self.model, prompt=full_prompt)
            result: str = response.get("response")
            return (
                result.strip() if isinstance(result, str)
                else self._fallback_summary(full_prompt)
            )
        except Exception as e:
            logger.warning("summarize_entries_bulk failed: %s", e, exc_info=True)
            return self._fallback_summary(full_prompt)