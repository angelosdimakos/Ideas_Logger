import json
from llm_router import get_prompt_template, apply_persona
from config_manager import load_config
from scripts.llm.ai_summarizer import AISummarizer


def load_report(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_contextual_prompt(query: str, report_data: dict, config) -> str:
    top_files = sorted(
        report_data.items(),
        key=lambda x: x[1].get("severity_score", 0),
        reverse=True
    )[:5]

    audit_summary = ""
    for fp, content in top_files:
        errors = content.get("linting", {}).get("quality", {}).get("mypy", {}).get("errors", [])
        lint = sum(len(v) for v in content.get("linting", {}).get("quality", {}).get("pydocstyle", {}).get("functions", {}).values())
        cx = [f.get("complexity", 0) for f in content.get("coverage", {}).get("complexity", {}).values()]
        cov = [f.get("coverage", 1.0) for f in content.get("coverage", {}).get("complexity", {}).values()]
        avg_cx = round(sum(cx) / len(cx), 2) if cx else 0
        avg_cov = round(sum(cov) / len(cov), 2) if cov else 1.0
        audit_summary += f"- `{fp}`: MyPy={len(errors)}, Lint={lint}, Cx={avg_cx}, Coverage={avg_cov * 100:.1f}%\n"

    prompt = f"""
You are an AI assistant helping engineers triage and improve Python codebases.

Here is a summary of the most risky files:
{audit_summary}

Now answer the developer question below using this context:

Q: {query}
"""
    return apply_persona(prompt.strip(), config.persona)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python chat_refactor.py merged_report.json")
        sys.exit(1)

    config = load_config()
    summarizer = AISummarizer()
    report = load_report(sys.argv[1])

    print("💬 Ask anything about your codebase risk, e.g.:")
    print("   - What’s the worst file?")
    print("   - Which functions need tests?")
    print("   - What should I fix first?\n")

    while True:
        query = input("❓> ")
        if query.strip().lower() in {"exit", "quit"}:
            break

        prompt = build_contextual_prompt(query, report, config)
        print("\n🧠 Mistral (via Ollama) is thinking...\n")
        summary = summarizer.summarize_entry(prompt, subcategory="Tooling & Automation")
        print(f"\n🤖 {summary}\n")
