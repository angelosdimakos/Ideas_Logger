import ollama
import logging
from requests.exceptions import RequestException  # In case Ollama errors bubble up as HTTP issues
from scripts.config.config_loader import load_config, get_config_value

logger = logging.getLogger(__name__)


class AISummarizer:
    def __init__(self):
        """
        Initializes the AISummarizer class.

        Loads configuration values to set up the language model and prompt behavior.

        The following configuration values are used:

        - llm_model: The language model to use for summarization, e.g. "mistral".
        - prompts_by_subcategory: A dictionary mapping subcategory names to custom prompts.
        """
        config = load_config()
        self.model = get_config_value(config, "llm_model", "mistral")
        self.prompts_by_subcategory = get_config_value(config, "prompts_by_subcategory", {})
        logger.info("[INIT] AISummarizer initialized with model: %s", self.model)

    def _fallback_summary(self, full_prompt):
        """
        Fallback summary using Ollama chat API if standard generation fails.
        """
        logger.info("[AI] Attempting fallback approach (chat)")
        try:
            response = ollama.chat(
                model=self.model, messages=[{"role": "user", "content": full_prompt}]
            )
            content = response.get("message", {}).get("content", "").strip()
            if content:
                logger.debug("[AI-Fallback] Fallback summary:\n%s", content)
                return content
            return "Fallback failed: Empty or invalid format"
        except (KeyError, TypeError, RequestException) as e:
            logger.error("[FallbackError] Ollama fallback failed: %s", e, exc_info=True)
            return "Fallback failed: Ollama not available"

    def summarize_entry(self, entry_text, subcategory=None):
        """
        Summarizes a single log entry with an optional subcategory prompt.
        """
        prompt = self.prompts_by_subcategory.get(
            subcategory, self.prompts_by_subcategory.get("_default", "Summarize this:")
        ).strip()
        full_prompt = f"{prompt}\n\n{entry_text}"

        try:
            logger.debug("[AI] Single-entry prompt:\n%s", full_prompt)
            response = ollama.generate(model=self.model, prompt=full_prompt)
            return response["response"].strip()
        except (KeyError, TypeError, RequestException) as e:
            logger.warning("summarize_entry failed: %s", e, exc_info=True)
            return self._fallback_summary(full_prompt)

    def summarize_entries_bulk(self, entries, subcategory=None):
        """
        Summarizes a list of entries using the Ollama generate API.
        """
        if not entries:
            logger.warning("[EmptyInput] summarize_entries_bulk received empty list")
            return "No entries provided"

        prompt_intro = self.prompts_by_subcategory.get(
            subcategory, self.prompts_by_subcategory.get("_default", "Summarize these points:")
        ).strip()
        combined_text = "\n".join(f"- {entry}" for entry in entries)
        full_prompt = f"{prompt_intro}\n\n{combined_text}"

        try:
            response = ollama.generate(model=self.model, prompt=full_prompt)
            return response["response"].strip()
        except (KeyError, TypeError, RequestException) as e:
            logger.warning("summarize_entries_bulk failed: %s", e, exc_info=True)
            return self._fallback_summary(full_prompt)
