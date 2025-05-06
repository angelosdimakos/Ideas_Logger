from scripts.config.config_manager import ConfigManager

def get_prompt_template(subcategory: str, config=None) -> str:
    """
    Retrieve a prompt string for a given subcategory from config.
    Falls back to "_default" if not found.
    """
    config = config or ConfigManager.load_config()
    return config.prompts_by_subcategory.get(subcategory, config.prompts_by_subcategory["_default"])

def apply_persona(prompt: str, persona: str) -> str:
    """
    Optionally tweak the prompt based on persona.
    """
    persona_mods = {
        "default": "",
        "reviewer": "\n\nRespond like a senior code reviewer. Be terse and blunt.",
        "mentor": "\n\nRespond like a mentor. Provide suggestions with empathy and reasoning.",
        "planner": "\n\nProvide next steps like a project planner.",
    }
    return prompt + persona_mods.get(persona, "")
