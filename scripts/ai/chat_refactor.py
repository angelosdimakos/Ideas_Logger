"""
This module provides functionality to load reports and build contextual prompts for an AI assistant.

It includes functions to load JSON reports and generate prompts based on the report data and user queries.
"""

import json
from scripts.ai.llm_router import get_prompt_template, apply_persona
from scripts.config.config_manager import ConfigManager
from scripts.ai.ai_summarizer import AISummarizer

def load_report(path: str) -> dict:
    """
    Load a JSON report from the specified file path.

    Args:
        path (str): The path to the JSON report file.

    Returns:
        dict: The loaded report data.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)  # Load and return JSON data from the specified file

def build_contextual_prompt(query: str, report_data: dict, config) -> str:
    """
    Build a contextual prompt for the AI assistant based on the developer's query and report data.

    Args:
        query (str): The developer's question.
        report_data (dict): The report data containing file information.
        config: Configuration object containing persona information.

    Returns:
        str: The constructed prompt for the AI assistant.
    """
    top_files = sorted(
        report_data.items(),
        key=lambda x: x[1].get("severity_score", 0),
        reverse=True
    )[:5]  # Select top 5 files based on severity score

    audit_summary = ""
    for fp, content in top_files:
        errors = content.get("linting", {}).get("quality", {}).get("mypy", {}).get("errors", [])
        lint = sum(len(v) for v in content.get("linting", {}).get("quality", {}).get("pydocstyle", {}).get("functions", {}).values())
        cx = [f.get("complexity", 0) for f in content.get("coverage", {}).get("complexity", {}).values()]
        cov = [f.get("coverage", 1.0) for f in content.get("coverage", {}).get("complexity", {}).values()]
        avg_cx = round(sum(cx) / len(cx), 2) if cx else 0  # Calculate average complexity, defaulting to 0 if no data
        avg_cov = round(sum(cov) / len(cov), 2) if cov else 1.0  # Calculate average coverage, defaulting to 1.0 if no data
        audit_summary += f"- `{fp}`: MyPy={len(errors)}, Lint={lint}, Cx={avg_cx}, Coverage={avg_cov * 100:.1f}%\n"

    prompt = f"""
You are an AI assistant helping engineers triage and improve Python codebases.

Here is a summary of the most risky files:
{audit_summary}

Now answer the developer question below using this context:

Q: {query}
"""
    return apply_persona(prompt.strip(), config.persona)  # Apply persona to the constructed prompt


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python chat_refactor.py merged_report.json")
        sys.exit(1)

    config = ConfigManager.load_config()  # Load configuration settings
    summarizer = AISummarizer()  # Initialize the summarizer
    report = load_report(sys.argv[1])  # Load the report from the provided file

    print("💬 Ask anything about your codebase risk, e.g:")
    print("   - What’s the worst file?")
    print("   - Which functions need tests?")
    print("   - What should I fix first?\n")

    while True:
        query = input("❓> ")
        if query.strip().lower() in {"exit", "quit"}:
            break

        prompt = build_contextual_prompt(query, report, config)  # Build prompt based on user query and report
        print("\n🧠 Mistral (via Ollama) is thinking...\n")
        summary = summarizer.summarize_entry(prompt, subcategory="Tooling & Automation")  # Get summary from the summarizer
        print(f"\n🤖 {summary}\n")
