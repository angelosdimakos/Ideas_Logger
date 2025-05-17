"""
This module provides functionality to retrieve prompt templates and apply personas to prompts for an AI assistant.

It includes functions to get prompt templates based on subcategories and modify prompts according to specified personas.
"""

from scripts.config.config_manager import ConfigManager


def get_prompt_template(subcategory: str, config=None) -> str:
    """
    Retrieves the prompt template for a specified subcategory, falling back to a default if unavailable.
    
    Args:
        subcategory: The subcategory key for which to obtain the prompt.
    
    Returns:
        The prompt string associated with the subcategory, or the default prompt if not found.
    """
    config = config or ConfigManager.load_config()  # Load config if not provided
    return config.prompts_by_subcategory.get(
        subcategory, config.prompts_by_subcategory["_default"]
    )  # Return specific or default prompt


def apply_persona(prompt: str, persona: str) -> str:
    """
    Appends persona-specific instructions to a prompt based on the selected persona.
    
    If the persona is recognized, the function adds corresponding guidance to the prompt; otherwise, the prompt is returned unchanged.
    
    Args:
        prompt: The original prompt to modify.
        persona: The persona style to apply ("default", "reviewer", "mentor", or "planner").
    
    Returns:
        The prompt string with persona-specific instructions appended, or unchanged if the persona is unrecognized.
    """
    persona_mods = {
        "default": "",
        "reviewer": "\n\nRespond like a senior code reviewer. Be terse and blunt.",  # Adjust prompt for a reviewer persona
        "mentor": "\n\nRespond like a mentor. Provide suggestions with empathy and reasoning.",  # Adjust prompt for a mentor persona
        "planner": "\n\nProvide next steps like a project planner.",  # Adjust prompt for a planner persona
    }
    return prompt + persona_mods.get(persona, "")  # Append persona modifications to the prompt
