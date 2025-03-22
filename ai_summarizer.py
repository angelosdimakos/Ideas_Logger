import ollama

class AISummarizer:
    """Handles AI summarization using local Ollama inference with subcategory-specific prompts."""

    def __init__(self, model="llama3"):
        self.model = model

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
        response = ollama.generate(model=self.model, prompt=full_prompt)
        return response['response'].strip()

    def summarize_entries_bulk(self, entries):
        """Summarizes multiple log entries as a batch for improved context awareness."""
        if not entries:
            return None

        combined_text = "\n".join(f"- {entry}" for entry in entries)
        prompt = f"{self.base_prompt}\n\n{combined_text}"
        
        try:
            response = ollama.generate(model=self.model, prompt=prompt)
            return response['response'].strip()
        except Exception as e:
            print(f"AI Summarization Error: {e}")
            return None
