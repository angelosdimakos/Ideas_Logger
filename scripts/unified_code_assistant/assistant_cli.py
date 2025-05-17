# assistant_cli.py

import argparse
import json
import sys
from pathlib import Path
from scripts.config.config_manager import ConfigManager
from scripts.unified_code_assistant.assistant_utils import load_report
from scripts.unified_code_assistant.analysis import analyze_report
from scripts.unified_code_assistant.strategy import generate_strategy
from scripts.unified_code_assistant.module_summarizer import summarize_modules
from scripts.unified_code_assistant.prompt_builder import build_contextual_prompt
from scripts.ai.ai_summarizer import AISummarizer


def chat_mode(report_path: str, config: ConfigManager) -> None:
    print("\n=== Code Assistant Chat Mode ===")
    print("💬 Ask anything about your codebase, e.g:")
    print("   - What's the worst file?")
    print("   - What refactoring should we prioritize?")
    print("   - Which functions need tests?")
    print("   - Suggest a plan to improve our code quality")
    print("\nType 'exit' or 'quit' to end the conversation.\n")

    report_data = load_report(report_path)
    summarizer = AISummarizer()
    analysis = analyze_report(report_data)

    while True:
        query = input("\n❓> ")
        if query.strip().lower() in {"exit", "quit"}:
            break

        print("\n🧠 Processing your question...\n")
        prompt = build_contextual_prompt(query, analysis["top_offenders"], analysis["summary_metrics"], config.persona)
        response = summarizer.summarize_entry(prompt, subcategory="Tooling & Automation")
        print(f"\n🤖 {response}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unified Code Assistant - Analyze code quality and get AI recommendations"
    )
    parser.add_argument("report_json", help="Path to merged_report.json")
    parser.add_argument(
        "--mode",
        choices=["chat", "analyze", "strategic", "summaries"],
        default="chat",
        help="Operation mode (default: chat)"
    )
    parser.add_argument("--top", type=int, default=20, help="Number of worst files to analyze")
    parser.add_argument("--persona", default="mentor", help="Assistant persona (mentor, reviewer, planner)")
    parser.add_argument("--path-filter", help="Filter to specific file paths")
    parser.add_argument("--output", "-o", help="Output file path for results")
    args = parser.parse_args()

    config = ConfigManager.load_config()
    config.persona = args.persona

    report_data = load_report(args.report_json)
    summarizer = AISummarizer()

    if args.mode == "chat":
        return chat_mode(args.report_json, config)

    elif args.mode == "analyze":
        results = analyze_report(report_data, top_n=args.top, path_filter=args.path_filter)
        output = json.dumps(results, indent=2)

    elif args.mode == "strategic":
        results = analyze_report(report_data, top_n=args.top, path_filter=args.path_filter)
        output = generate_strategy(
            severity_data=results["severity_data"],
            summary_metrics=results["summary_metrics"],
            limit=args.top,
            persona=config.persona,
            summarizer=summarizer
        )

    elif args.mode == "summaries":
        output_data = summarize_modules(report_data, summarizer, config=config)
        output = "\n\n".join([f"## {path}\n\n{summary}" for path, summary in output_data.items()])

    if args.output:
        Path(args.output).write_text(output)
        print(f"Results written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    sys.exit(main())
