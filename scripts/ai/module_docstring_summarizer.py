"""
This module provides functionality to summarize the purpose of Python modules based on their function-level docstrings.

It includes functions to summarize module docstrings and process reports containing module information.
"""


import json
from pathlib import Path
from scripts.ai.ai_summarizer import AISummarizer
from scripts.config.config_manager import ConfigManager
from scripts.ai.llm_router import get_prompt_template, apply_persona


def summarize_module(file_path: str, doc_entries: list, summarizer: AISummarizer, config: ConfigManager) -> str:
    """
    Summarize a module's purpose based on its function-level docstrings.

    Args:
        file_path (str): The path of the module file.
        doc_entries (list): A list of function docstring entries.
        summarizer (AISummarizer): The summarizer object used for generating summaries.
        config (ConfigManager): Configuration object containing relevant settings.

    Returns:
        str: The summarized purpose of the module.
    """
    if not doc_entries:
        return "No docstrings found."

    summaries = []
    for entry in doc_entries:
        name = entry.get("name", "unknown")
        desc = (entry.get("description") or "").strip()

        # Always include the function name, even if description is empty
        summaries.append(f"- `{name}`: {desc}")

    joined = "\n".join(summaries)
    prompt = get_prompt_template("Module Functionality", config)
    full_prompt = f"{prompt}\n\n{joined}"
    final_prompt = apply_persona(full_prompt, config.persona)
    return summarizer.summarize_entry(final_prompt, subcategory="Module Functionality")


def main(input_path: str) -> None:
    """
    Main function to load a report and summarize the docstrings for each module.

    Args:
        input_path (str): The path to the input JSON report file.
    """
    config = ConfigManager.load_config()
    summarizer = AISummarizer()

    with open(input_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    for file_path, data in report.items():
        funcs = data.get("docstrings", {}).get("functions", [])
        if funcs:
            print(f" {file_path}")  # Print with a space prefix for consistency
            summary = summarize_module(file_path, funcs, summarizer, config)
            print(f" {summary}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python module_docstring_summarizer.py merged_report.json")
        sys.exit(1)
    main(sys.argv[1])