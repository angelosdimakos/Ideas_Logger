import ollama
import traceback
import logging
from scripts.config_loader import load_config, get_config_value

class AISummarizer:
    def __init__(self):
        """
        Initializes the AISummarizer class by loading configuration values.
        Sets up the LLM model and prompt configurations.
        """
        config = load_config()
        self.model = get_config_value(config, "llm_model", "mistral")
        self.prompts_by_subcategory = get_config_value(config, "prompts_by_subcategory", {})
        print(f"[INFO] Initializing AISummarizer with model: {self.model}")

    def _fallback_summary(self, full_prompt):
        """
        Fallback method using chat mode when generate fails.
        """
        print("[AI] Attempting fallback approach (chat)")
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': full_prompt}
            ])
            content = response.get('message', {}).get('content', '').strip()
            if content:
                print(f"[AI-Fallback] Fallback summary:\n{content}\n")
                return content
            else:
                return "Fallback failed: Empty or invalid format"
        except Exception as e:
            print(f"[❌ AI Error] Fallback failed: {str(e)}")
            return "Fallback failed: Ollama not available"

    def summarize_entry(self, entry_text, subcategory=None):
        """
        Summarize a single entry.
        """
        prompt = self.prompts_by_subcategory.get(subcategory, self.prompts_by_subcategory.get("_default", "Summarize this:")).strip()
        full_prompt = f"{prompt}\n\n{entry_text}"
        try:
            print(f"[AI] Single-entry prompt:\n{full_prompt}\n")
            response = ollama.generate(model=self.model, prompt=full_prompt)
            return response['response'].strip()
        except Exception as e:
            logging.error(f"summarize_entry failed: {str(e)}")
            return self._fallback_summary(full_prompt)

    def summarize_entries_bulk(self, entries, subcategory=None):
        """
        Summarize a list of entries in bulk for better context.
        """
        if not entries:
            print("[⚠️ Empty Input] summarize_entries_bulk received empty list")
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
