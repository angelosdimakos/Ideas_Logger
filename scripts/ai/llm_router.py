"""
This module provides functionality to retrieve prompt templates and apply personas to prompts for an AI assistant.

It includes functions to get prompt templates based on subcategories and modify prompts according to specified personas.
"""

from scripts.config.config_manager import ConfigManager

def get_prompt_template(subcategory: str, config=None) -> str:
    """
    Retrieve a prompt string for a given subcategory from the configuration.
    Falls back to the default if not found.

    Args:
        subcategory (str): The subcategory for which to retrieve the prompt.
        config: Optional configuration object.

    Returns:
        str: The prompt string for the specified subcategory.
    """
    config = config or ConfigManager.load_config()
    return config.prompts_by_subcategory.get(subcategory, config.prompts_by_subcategory["_default"])

def apply_persona(prompt: str, persona: str) -> str:
    """
    Optionally tweak the prompt based on the specified persona.

    Args:
        prompt (str): The original prompt string.
        persona (str): The persona to apply to the prompt.

    Returns:
        str: The modified prompt string with persona adjustments.
    """
    persona_mods = {
        "default": "",
        "reviewer": "\n\nRespond like a senior code reviewer. Be terse and blunt.",
        "mentor": "\n\nRespond like a mentor. Provide suggestions with empathy and reasoning.",
        "planner": "\n\nProvide next steps like a project planner.",
    }
    return prompt + persona_mods.get(persona, "")
