import json
import sys
from llm_router import get_prompt_template, apply_persona
from scripts.config.config_manager import ConfigManager
from scripts.ai.ai_summarizer import AISummarizer


def load_audit(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_top_offenders(report_data, top_n=5):
    rows = []
    for fp, content in report_data.items():
        errors = content.get("linting", {}).get("quality", {}).get("mypy", {}).get("errors", [])
        lint_issues = sum(len(v) for v in content.get("linting", {}).get("quality", {}).get("pydocstyle", {}).get("functions", {}).values())
        complexities = [f.get("complexity", 0) for f in content.get("coverage", {}).get("complexity", {}).values()]
        coverage = [f.get("coverage", 1.0) for f in content.get("coverage", {}).get("complexity", {}).values()]
        avg_cx = round(sum(complexities) / len(complexities), 2) if complexities else 0
        avg_cov = round(sum(coverage) / len(coverage), 2) if coverage else 1.0
        score = 2 * len(errors) + 1.5 * lint_issues + avg_cx + 2 * (1 - avg_cov)
        rows.append((fp, score, errors, lint_issues, avg_cx, avg_cov))
    return sorted(rows, key=lambda r: r[1], reverse=True)[:top_n]


def build_refactor_prompt(offenders, config, subcategory="Tooling & Automation"):
    prompt = get_prompt_template(subcategory, config)
    prompt += "\n\nHere is a ranked list of risky files:\n"
    for fp, score, errors, lint_issues, cx, cov in offenders:
        prompt += f"- `{fp}`: Score={score:.1f}, MyPy={len(errors)}, Lint={lint_issues}, Cx={cx}, Coverage={cov*100:.1f}%\n"
    return apply_persona(prompt, config.persona)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gpt_refactor_advisor.py merged_report.json")
        sys.exit(1)

    config = ConfigManager.load_config()
    audit_data = load_audit(sys.argv[1])
    offenders = extract_top_offenders(audit_data, top_n=5)
    final_prompt = build_refactor_prompt(offenders, config, subcategory="Refactor Advisor")

    print("\n==== REFRACTOR ADVISOR PROMPT ====")
    print(final_prompt)

    print("\n==== MISTRAL SUGGESTION ====")
    summarizer = AISummarizer()
    summary = summarizer.summarize_entry(final_prompt, subcategory="Tooling & Automation")
    print(summary)
