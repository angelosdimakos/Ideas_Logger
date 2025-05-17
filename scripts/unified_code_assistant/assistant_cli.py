import argparse
from pathlib import Path
from scripts.config.config_manager import ConfigManager
from scripts.unified_code_assistant.assistant_utils import load_report, get_issue_locations
from scripts.unified_code_assistant.analysis import analyze_report
from scripts.unified_code_assistant.strategy import generate_strategy
from scripts.unified_code_assistant.module_summarizer import summarize_modules
from scripts.unified_code_assistant.prompt_builder import build_enhanced_contextual_prompt
from scripts.ai.ai_summarizer import AISummarizer
from scripts.ai.llm_refactor_advisor import build_refactor_prompt
import sys
import io


def chat_mode(
    report_path: str,
    config: ConfigManager,
    top_n: int,
    path_filter: str
) -> None:
    print("\n=== Code Assistant Chat Mode ===")
    print("💬 Ask anything about your codebase, e.g:")
    print("   - What's the worst file?")
    print("   - What refactoring should we prioritize?")
    print("   - Which functions need tests?")
    print("   - Suggest a plan to improve our code quality")
    print("\nType 'exit' or 'quit' to end the conversation.\n")

    report_data = load_report(report_path)
    summarizer = AISummarizer()
    analysis = analyze_report(report_data, top_n=top_n, path_filter=path_filter)

    top_offenders = analysis["top_offenders"]
    summary_metrics = analysis["summary_metrics"]

    module_summaries = summarize_modules(report_data, summarizer, config, path_filter=path_filter)
    file_issues = {fp: get_issue_locations(fp, report_data) for fp, *_ in top_offenders[:top_n]}

    file_recommendations = {}
    for offender in top_offenders[:top_n]:
        fp = offender[0]
        refactor_prompt = build_refactor_prompt(
            [offender],
            config,
            subcategory="Refactor Advisor",
            verbose=False,
            limit=1
        )
        recommendation = summarizer.summarize_entry(refactor_prompt, subcategory="Tooling & Automation")
        file_recommendations[fp] = recommendation

    persona = config.persona

    while True:
        query = input("\n❓> ")
        if query.strip().lower() in {"exit", "quit"}:
            break

        print("\n🧠 Processing your question...\n")
        prompt = build_enhanced_contextual_prompt(
            query,
            top_offenders,
            summary_metrics,
            module_summaries,
            file_issues,
            file_recommendations,
            persona
        )
        response = summarizer.summarize_entry(prompt, subcategory="Refactor Advisor")
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
        return chat_mode(args.report_json, config, args.top, args.path_filter)

    elif args.mode == "analyze":
        results = analyze_report(report_data, top_n=args.top, path_filter=args.path_filter)
        offenders = results["top_offenders"]

        if not offenders:
            print(f"No offenders matched filter: {args.path_filter}")
            return

        target_fp, *_ = offenders[0]
        offender_data = report_data[target_fp]
        file_issues = {target_fp: get_issue_locations(target_fp, report_data)}
        module_summaries = summarize_modules(report_data, summarizer, config, path_filter=target_fp)

        output_text = summarizer.summarize_entry(
            build_enhanced_contextual_prompt(
                "Provide a detailed code quality assessment and improvement plan for this module.",
                results["top_offenders"],
                results["summary_metrics"],
                module_summaries,
                file_issues,
                {},  # optionally load file_recommendations here if desired
                config.persona
            ),
            subcategory="Code Analysis"
        )

        if args.output:
            Path(args.output).write_text(output_text)
            print(f"LLM recommendation written to {args.output}")
        else:
            print(f"\n🧠 LLM Recommendation for {target_fp}:\n{output_text}\n")

    elif args.mode == "strategic":
        results = analyze_report(report_data, top_n=args.top, path_filter=args.path_filter)
        output = generate_strategy(
            severity_data=results["severity_data"],
            summary_metrics=results["summary_metrics"],
            limit=args.top,
            persona=config.persona,
            summarizer=summarizer
        )

        if args.output:
            Path(args.output).write_text(output)
            print(f"Results written to {args.output}")
        else:
            print(output)

    elif args.mode == "summaries":
        output_data = summarize_modules(report_data, summarizer, config=config, path_filter=args.path_filter)
        output = "\n\n".join([f"## {path}\n\n{summary}" for path, summary in output_data.items()])

        if 'output' in locals() and args.output:
            Path(args.output).write_text(output)
            print(f"Results written to {args.output}")
        elif 'output' in locals():
            print(output)

if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    import sys
    sys.exit(main())
