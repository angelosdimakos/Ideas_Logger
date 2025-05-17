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
        Initializes the AISummarizer with configuration settings, model selection, and prompts.
        
        Loads configuration data, sets the LLM model (defaulting to 'mistral' if unspecified), and prepares subcategory-specific prompts for summarization.
        """
        config: Dict[str, Any] = load_config()  # Load configuration settings from external source
        self.model: str = get_config_value(
            config, "llm_model", "mistral"
        )  # Set the model, defaulting to 'mistral'
        self.prompts_by_subcategory: Dict[str, Any] = get_config_value(
            config, "prompts_by_subcategory", {}
        )  # Load prompts categorized by subcategory
        logger.info("[INIT] AISummarizer initialized with model: %s", self.model)

    def _fallback_summary(self, full_prompt: str) -> str:
        """
        Generates a summary using the Ollama chat API as a fallback if primary summarization fails.
        
        Args:
            full_prompt: The prompt to send to the chat model.
        
        Returns:
            The generated summary, or an error message if the fallback fails.
        """
        logger.info("[AI] Attempting fallback approach (chat)")
        try:
            response = ollama.chat(
                model=self.model, messages=[{"role": "user", "content": full_prompt}]
            )  # Use the chat API to get a response
            content = response.get("message", {}).get("content", "")
            return (
                content.strip() if isinstance(content, str) else "Fallback failed: Invalid format"
            )  # Ensure content is valid before returning
        except (KeyError, TypeError, RequestException) as e:
            logger.error("[FallbackError] Ollama fallback failed: %s", e, exc_info=True)
            return "Fallback failed: Ollama not available"  # Handle exceptions gracefully

    def summarize_entry(self, entry_text: str, subcategory: Optional[str] = None) -> str:
        """
        Generates a summary for a single text entry using the configured LLM model and an optional subcategory-specific prompt.
        
        Args:
            entry_text: The text to be summarized.
            subcategory: An optional subcategory to select a specialized prompt.
        
        Returns:
            The generated summary, or a fallback message if summarization fails.
        """
        prompt: str = self.prompts_by_subcategory.get(
            subcategory, self.prompts_by_subcategory.get("_default", "Summarize this:")
        ).strip()  # Select prompt based on subcategory or use default
        full_prompt: str = f"{prompt}\n\n{entry_text}"  # Combine prompt with entry text

        try:
            logger.debug(
                "[AI] Single-entry prompt:\n%s", full_prompt
            )  # Log the full prompt for debugging
            response = ollama.generate(
                model=self.model, prompt=full_prompt
            )  # Generate summary using the LLM
            result: str = response.get("response")
            return (
                result.strip() if isinstance(result, str) else self._fallback_summary(full_prompt)
            )  # Return result or fallback if the response is invalid
        except Exception as e:
            logger.warning("summarize_entry failed: %s", e, exc_info=True)
            return self._fallback_summary(full_prompt)  # Fallback on error

    def summarize_entries_bulk(self, entries: List[str], subcategory: Optional[str] = None) -> str:
        """
        Generates a summary for a list of text entries using the configured LLM model and prompts.
        
        If a subcategory is provided, a corresponding prompt is used; otherwise, a default prompt is applied. Returns a fallback message if summarization fails or if the input list is empty.
        
        Args:
            entries: List of text entries to summarize.
            subcategory: Optional subcategory to select a specific prompt.
        
        Returns:
            The generated summary as a string, or a fallback message if summarization fails.
        """
        if not entries:
            logger.warning("[EmptyInput] summarize_entries_bulk received empty list")
            return "No entries provided"

        prompt_intro: str = self.prompts_by_subcategory.get(
            subcategory, self.prompts_by_subcategory.get("_default", "Summarize these points:")
        ).strip()  # Select prompt based on subcategory or use default
        combined_text: str = "\n".join(
            f"- {entry}" for entry in entries
        )  # Combine entries into a single string
        full_prompt: str = (
            f"{prompt_intro}\n\n{combined_text}"  # Combine prompt with combined entries
        )

        try:
            response = ollama.generate(
                model=self.model, prompt=full_prompt
            )  # Generate summary using the LLM
            result: str = response.get("response")
            return (
                result.strip() if isinstance(result, str) else self._fallback_summary(full_prompt)
            )  # Return result or fallback if the response is invalid
        except Exception as e:
            logger.warning("summarize_entries_bulk failed: %s", e, exc_info=True)
            return self._fallback_summary(full_prompt)  # Fallback on error
