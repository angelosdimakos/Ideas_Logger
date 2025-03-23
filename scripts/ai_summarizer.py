import ollama
import traceback
import logging
from scripts.config_loader import load_config, get_config_value

# Create a logger for this module
logger = logging.getLogger(__name__)

class AISummarizer:
    def __init__(self):
        """
        Initializes the AISummarizer class by loading configuration values.
        Sets up the LLM model and prompt configurations.
        """
        config = load_config()
        self.model = get_config_value(config, "llm_model", "llama3")
        self.prompts_by_subcategory = get_config_value(config, "prompts_by_subcategory", {})

        # Optionally, set the logger level from config (e.g., "ERROR", "INFO", etc.)
        level_str = get_config_value(config, "log_level", "ERROR").upper()
        numeric_level = getattr(logging, level_str, logging.ERROR)
        logging.getLogger().setLevel(numeric_level)

        logger.info(f"Initializing AISummarizer with model: {self.model}")
    
    def _fallback_summary(self, full_prompt):
        """
        Fallback method to summarize using `ollama.chat` in case of failure.
        """
        logger.info("[AI] Attempting fallback approach (chat)")
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': full_prompt}]
            )
            if response and 'message' in response and 'content' in response['message']:
                fallback_answer = response['message']['content'].strip()
                logger.info(f"[AI-Fallback] Fallback summary:\n{fallback_answer}\n")
                return fallback_answer
            else:
                logger.error("[❌ AI Error] Fallback approach returned unexpected format")
                return "Fallback failed: Unexpected format"
        except Exception as fallback_error:
            logger.error("[❌ AI Error] Fallback approach also failed: %s", fallback_error, exc_info=True)
            return "Fallback failed: Ollama down"

    def summarize_entry(self, entry_text, subcategory=None):
        """
        Generate a summary for a single entry based on its associated subcategory.
        """
        prompt = self.prompts_by_subcategory.get(subcategory, self.prompts_by_subcategory["_default"])
        full_prompt = f"{prompt}\n\n{entry_text}"
        try:
            logger.debug(f"[AI] Single-entry prompt:\n{full_prompt}\n")
            response = ollama.generate(model=self.model, prompt=full_prompt)
            answer = response['response'].strip()
            logger.debug(f"[AI] Single-entry response:\n{answer}\n")
            return answer
        except Exception as e:
            logger.error("[❌ AI Error] summarize_entry failed: %s", e, exc_info=True)
            return self._fallback_summary(full_prompt)

    def summarize_entries_bulk(self, entries, subcategory=None):
        """
        Summarizes multiple log entries as a batch for improved context awareness.
        """
        if not entries:
            logger.warning("[⚠️ Empty Input] summarize_entries_bulk received empty entry list")
            return "No entries provided"

        prompt_intro = self.prompts_by_subcategory.get(subcategory, self.prompts_by_subcategory["_default"])
        combined_text = "\n".join(f"- {entry}" for entry in entries)
        full_prompt = f"{prompt_intro}\n\n{combined_text}"

        logger.debug(f"[AI] Bulk prompt:\n{full_prompt}\n")
        
        try:
            response = ollama.generate(model=self.model, prompt=full_prompt)
            if 'response' in response:
                result = response['response'].strip()
                logger.debug(f"[AI] Bulk response:\n{result}\n")
                return result
            else:
                raise ValueError("Invalid response format from Ollama API")
        except Exception as e:
            logger.error("[❌ AI Error] summarize_entries_bulk failed: %s", e, exc_info=True)
            fallback_result = self._fallback_summary(full_prompt)
            if not fallback_result:
                raise RuntimeError("Fallback failed to generate a summary.")
            return fallback_result

