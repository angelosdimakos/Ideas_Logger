import ollama
import traceback
import logging

class AISummarizer:
    """Handles AI summarization using local Ollama inference with subcategory-specific prompts."""

    def __init__(self, model="llama3"):
        self.model = model
        print(f"[INFO] Initializing AISummarizer with model: {model}")

        # Subcategory-specific prompts
        self.prompts_by_subcategory = {
            # === Narrative ===
            "Narrative Concept": "Summarize the core narrative idea with a focus on its thematic significance or plot role.",
            "Emotional Impact": "Summarize the emotional tone or psychological effect this idea is meant to deliver.",
            "Romantic Development": "Summarize this relationship insight while preserving emotional nuance and character dynamics.",

            # === World ===
            "Worldbuilding Detail": "Summarize this worldbuilding element to highlight its uniqueness or relevance to lore.",
            "Faction Dynamics": "Summarize the factional strategy, alliance, or betrayal logic described.",
            "Loop Mechanics": "Summarize this idea about time loops or memory mechanics in a structured way.",

            # === AI / Meta ===
            "AI System Design": "Summarize the AI system concept clearly, focusing on architecture or interaction design.",
            "Tooling & Automation": "Summarize the workflow, tool, or automation concept in a concise technical format.",
            "Execution Strategy": "Summarize the execution plan, decision, or optimization insight.",
            "Meta Reflection": "Summarize the philosophical or reflective insight being conveyed.",

            # === Creative ===
            "Visual or Audio Prompt": "Summarize this creative prompt into a single vivid visual/audio description.",
            "Gameplay Design Insight": "Summarize this as a gameplay mechanic or player-interaction concept.",
            "Creative Ops / Org Flow": "Summarize the creative workflow or team process insight described.",

            # Fallback default
            "_default": "Summarize the following idea into concise, meaningful bullet points:"
        }

    def summarize_entry(self, entry_text, subcategory=None):
        """Generate summary using subcategory-specific prompt if available."""
        prompt = self.prompts_by_subcategory.get(subcategory, self.prompts_by_subcategory["_default"])
        full_prompt = f"{prompt}\n\n{entry_text}"
        try:
            print(f"[AI] Single-entry prompt:\n{full_prompt}\n")
            response = ollama.generate(model=self.model, prompt=full_prompt)
            answer = response['response'].strip()
            print(f"[AI] Single-entry response:\n{answer}\n")
            return answer
        except Exception as e:
            error_msg = f"[❌ AI Error] summarize_entry failed: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            logging.error(error_msg)
            
            # Try fallback approach
            try:
                print("[AI] Attempting fallback approach (chat) for single entry")
                response = ollama.chat(model=self.model, messages=[
                    {'role': 'user', 'content': full_prompt}
                ])
                if response and 'message' in response and 'content' in response['message']:
                    fallback_answer = response['message']['content'].strip()
                    print(f"[AI-Fallback] Single-entry:\n{fallback_answer}\n")
                    return fallback_answer
                else:
                    print("[❌ AI Error] Fallback approach returned unexpected format")
                    return None
            except Exception as fallback_error:
                print(f"[❌ AI Error] Fallback approach also failed: {str(fallback_error)}")
                return None

    def summarize_entries_bulk(self, entries, subcategory=None):
        """Summarizes multiple log entries as a batch for improved context awareness."""
        if not entries:
            print("[⚠️ Empty Input] summarize_entries_bulk received empty entry list")
            return None

        prompt_intro = self.prompts_by_subcategory.get(subcategory, self.prompts_by_subcategory["_default"])
        combined_text = "\n".join(f"- {entry}" for entry in entries)
        full_prompt = f"{prompt_intro}\n\n{combined_text}"

        print(f"[AI] Bulk prompt:\n{full_prompt}\n")
        try:
            response = ollama.generate(model=self.model, prompt=full_prompt)
            result = response['response'].strip()
            print(f"[AI] Bulk response:\n{result}\n")
            return result
        except Exception as e:
            error_msg = f"[❌ AI Error] summarize_entries_bulk failed: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            logging.error(error_msg)
            
            # Attempt fallback
            try:
                print("[AI] Attempting fallback approach (chat) for bulk entries")
                response = ollama.chat(model=self.model, messages=[
                    {'role': 'user', 'content': full_prompt}
                ])
                if response and 'message' in response and 'content' in response['message']:
                    fallback_answer = response['message']['content'].strip()
                    print(f"[AI-Fallback] Bulk:\n{fallback_answer}\n")
                    return fallback_answer
                else:
                    return None
            except Exception as fallback_error:
                print(f"[❌ AI Error] Fallback approach also failed: {str(fallback_error)}")
                return None
