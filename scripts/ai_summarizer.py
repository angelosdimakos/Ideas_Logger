import ollama
import traceback
import logging
from scripts.config_loader import load_config, get_config_value

logger = logging.getLogger(__name__)

class AISummarizer:
    def __init__(self):
        """
        Initializes the AISummarizer class.

        This method loads configuration values to set up the language model
        and the prompt configurations used for generating summaries.
        """
        # Load the configuration settings
        config = load_config()

        # Retrieve the language model name from the configuration, defaulting to "mistral"
        self.model = get_config_value(config, "llm_model", "mistral")

        # Retrieve the prompts categorized by subcategory from the configuration
        self.prompts_by_subcategory = get_config_value(config, "prompts_by_subcategory", {})

        # Informational log indicating the model being initialized
        logger.info(f'[INFO] Initializing AISummarizer with model: {self.model}')
    def _fallback_summary(self, full_prompt):
        """
        Generates a summary using a fallback approach.

        Args:
            full_prompt (str): The complete prompt text to be used for generating the summary.

        Returns:
            str: The generated summary if successful, or an error message indicating failure.
        """

        logger.info("[AI] Attempting fallback approach (chat)")
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': full_prompt}
            ])
            content = response.get('message', {}).get('content', '').strip()
            if content:
                logger.debug(f"[AI-Fallback] Fallback summary:\n{content}\n")
                return content
            else:
                return "Fallback failed: Empty or invalid format"
        except Exception as e:
            logger.error(f"[❌ AI Error] Fallback failed: {str(e)}")
            return "Fallback failed: Ollama not available"

    def summarize_entry(self, entry_text, subcategory=None):
        """
        Summarizes a single log entry using the language model and the prompt configurations.

        Args:
            entry_text (str): The text of the log entry to be summarized.
            subcategory (str): The subcategory of the log entry, used to customize the prompt.

        Returns:
            str: The generated summary if successful, or an error message indicating failure.
        """

        prompt = self.prompts_by_subcategory.get(subcategory, self.prompts_by_subcategory.get("_default", "Summarize this:")).strip()
        full_prompt = f"{prompt}\n\n{entry_text}"
        try:
            logger.debug(f"[AI] Single-entry prompt:\n{full_prompt}\n")
            response = ollama.generate(model=self.model, prompt=full_prompt)
            return response['response'].strip()
        except Exception as e:
            logging.error(f"summarize_entry failed: {str(e)}")
            return self._fallback_summary(full_prompt)

    def summarize_entries_bulk(self, entries, subcategory=None):

        """
        Summarizes a list of log entries using the language model and the prompt configurations.

        Args:
            entries (list[str]): The list of log entries to be summarized.
            subcategory (str): The subcategory of the log entries, used to customize the prompt.

        Returns:
            str: The generated summary if successful, or an error message indicating failure.
        """
        if not entries:
            logger.warning("[⚠️ Empty Input] summarize_entries_bulk received empty list")
            return "No entries provided"

        prompt_intro = self.prompts_by_subcategory.get(subcategory, self.prompts_by_subcategory.get("_default", "Summarize these points:")).strip()
        combined_text = "\n".join(f"- {entry}" for entry in entries)
        full_prompt = f"{prompt_intro}\n\n{combined_text}"

        try:
            response = ollama.generate(model=self.model, prompt=full_prompt)
            if 'response' in response:
                return response['response'].strip()
            else:
                raise ValueError("Invalid response format from Ollama API")
        except Exception as e:
            logging.error(f"summarize_entries_bulk failed: {str(e)}")
            return self._fallback_summary(full_prompt)
