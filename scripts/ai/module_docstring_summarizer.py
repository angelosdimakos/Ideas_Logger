"""
This module provides functionality to load audit reports and build refactor prompts for an AI assistant.

It includes functions to load JSON audit data, extract top offenders based on various metrics, and generate prompts for AI assistance.
"""

import json
from pathlib import Path
import argparse

from scripts.ai.ai_summarizer import AISummarizer
from scripts.config.config_manager import ConfigManager
from scripts.ai.llm_router import get_prompt_template, apply_persona


def summarize_module(
    file_path: str, doc_entries: list, summarizer: AISummarizer, config: ConfigManager
) -> str:
    """
    Summarize the module's docstrings using the provided summarizer.

    Args:
        file_path (str): The path to the module file.
        doc_entries (list): List of docstring entries to summarize.
        summarizer (AISummarizer): The summarizer instance to use.
        config (ConfigManager): The configuration manager instance.

    Returns:
        str: The summary of the module's docstrings.
    """
    if not doc_entries:
        return "No docstrings found."  # Early exit if no docstrings are provided

    summaries = []
    for entry in doc_entries:
        name = entry.get("name", "unknown")  # Get the name of the function or class
        desc = (entry.get("description") or "").strip()  # Get and clean the description
        summaries.append(f"- `{name}`: {desc}")  # Format summary entry
    joined = "\n".join(summaries)  # Join all summaries into a single string
    prompt = get_prompt_template(
        "Module Functionality", config
    )  # Get the prompt template for the summarization
    full_prompt = f"{prompt}\n\n{joined}"  # Combine prompt with the summary entries
    final_prompt = apply_persona(
        full_prompt, config.persona
    )  # Apply persona adjustments to the prompt
    return summarizer.summarize_entry(
        final_prompt, subcategory="Module Functionality"
    )  # Generate and return the summary


def run(input_path: str, output_path: str | None = None, path_filter: str | None = None) -> None:
    """
    Run the summarization process on the specified input file.

    Args:
        input_path (str): The path to the input JSON report file.
        output_path (str | None): Optional path to save the output summary.
        path_filter (str | None): Optional filter for file paths to include in the summary.
    """
    config = ConfigManager.load_config()  # Load configuration settings
    summarizer = AISummarizer()  # Initialize the summarizer
    summaries = {}

    with open(input_path, "r", encoding="utf-8") as f:
        report = json.load(f)  # Load the JSON report data

    for file_path, data in report.items():
        if path_filter and path_filter not in file_path:
            continue  # Skip files that do not match the filter
        funcs = data.get("docstrings", {}).get("functions", [])  # Get functions' docstrings
        if not funcs:
            continue  # Skip if no functions have docstrings
        summary = summarize_module(
            file_path, funcs, summarizer, config
        )  # Summarize the module's docstrings
        summaries[file_path] = summary  # Store the summary for the file

    if output_path:
        out_path = Path(output_path)
        lines = [
            f"## {path}\n\n{summary}\n" for path, summary in summaries.items()
        ]  # Prepare output format
        out_path.write_text(
            "\n".join(lines), encoding="utf-8"
        )  # Write summaries to the output file
        print(f"✅ Written to {output_path}")
    else:
        for path, summary in summaries.items():
            print(f"\n{path}\n{summary}")  # Print summaries if no output path is provided


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Summarize Python module functionality from docstrings."
    )
    parser.add_argument("input", help="Path to merged_report.json")
    parser.add_argument("--to", help="Path to write Markdown summary to")
    parser.add_argument("--filter", help="Only include modules with this substring in the path")
    args = parser.parse_args()
    run(args.input, output_path=args.to, path_filter=args.filter)
