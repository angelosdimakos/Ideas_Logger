import json
from pathlib import Path
import argparse

from scripts.ai.ai_summarizer import AISummarizer
from scripts.config.config_manager import ConfigManager
from scripts.ai.llm_router import get_prompt_template, apply_persona


def summarize_module(file_path: str, doc_entries: list, summarizer: AISummarizer, config: ConfigManager) -> str:
    if not doc_entries:
        return "No docstrings found."

    summaries = []
    for entry in doc_entries:
        name = entry.get("name", "unknown")
        desc = (entry.get("description") or "").strip()
        summaries.append(f"- `{name}`: {desc}")
    joined = "\n".join(summaries)
    prompt = get_prompt_template("Module Functionality", config)
    full_prompt = f"{prompt}\n\n{joined}"
    final_prompt = apply_persona(full_prompt, config.persona)
    return summarizer.summarize_entry(final_prompt, subcategory="Module Functionality")


def run(input_path: str, output_path: str | None = None, path_filter: str | None = None) -> None:
    config = ConfigManager.load_config()
    summarizer = AISummarizer()
    summaries = {}

    with open(input_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    for file_path, data in report.items():
        if path_filter and path_filter not in file_path:
            continue
        funcs = data.get("docstrings", {}).get("functions", [])
        if not funcs:
            continue
        summary = summarize_module(file_path, funcs, summarizer, config)
        summaries[file_path] = summary

    if output_path:
        out_path = Path(output_path)
        lines = [f"## {path}\n\n{summary}\n" for path, summary in summaries.items()]
        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"✅ Written to {output_path}")
    else:
        for path, summary in summaries.items():
            print(f"\n{path}\n{summary}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize Python module functionality from docstrings.")
    parser.add_argument("input", help="Path to merged_report.json")
    parser.add_argument("--to", help="Path to write Markdown summary to")
    parser.add_argument("--filter", help="Only include modules with this substring in the path")
    args = parser.parse_args()
    run(args.input, output_path=args.to, path_filter=args.filter)
