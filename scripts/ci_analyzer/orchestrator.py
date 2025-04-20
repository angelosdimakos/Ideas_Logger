import json
from pathlib import Path
from typing import Any, Dict
from datetime import datetime
import shutil
import argparse

from scripts.ci_analyzer.insights.overview import generate_overview_insights
from scripts.ci_analyzer.insights.descriptive_insights import generate_complexity_insights, generate_diff_insights, generate_quality_insights, generate_testing_insights

from scripts.ci_analyzer.insights.prime_suspects import generate_prime_insights


# Add this function to create a backup
def backup_audit_file(path: str = "refactor_audit.json") -> None:
    """Create a timestamped backup of the audit file."""
    audit_path = Path(path)
    if not audit_path.exists():
        print(f"Warning: Cannot backup {path} - file not found")
        return

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("audit_backups")
    backup_dir.mkdir(exist_ok=True)

    backup_path = backup_dir / f"refactor_audit_{timestamp}.json"
    shutil.copy2(audit_path, backup_path)
    print(f"✅ Audit backup created at {backup_path}")

def load_audit(path: str = "refactor_audit.json") -> Dict[str, Any]:
    # First create a backup before loading
    backup_audit_file(path)
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def header_block() -> str:
    return """
## 🔍 CI Audit Summary

Each section includes:
- 📊 Metric summaries
- 🚨 Emoji Risk Indicators (🟢 Low, 🟡 Medium, 🔴 High)
- ▓▓ Visual bar indicators (Markdown style)
"""


def generate_ci_summary(audit: Dict[str, Any]) -> str:
    parts = [header_block()]
    parts.extend(generate_overview_insights(audit))
    parts.extend(generate_prime_insights(audit))
    parts.extend(generate_complexity_insights(audit))
    parts.extend(generate_testing_insights(audit))
    parts.extend(generate_quality_insights(audit))
    parts.extend(generate_diff_insights(audit))
    return "\n".join(parts)


def save_summary(markdown: str, out_path: str = "ci_summary.md") -> None:
    Path(out_path).write_text(markdown, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", default="refactor_audit.json", help="Path to audit JSON file")
    parser.add_argument("--output", default="ci_summary.md", help="Path to markdown output")
    args = parser.parse_args()

    audit = load_audit(args.audit)
    summary = generate_ci_summary(audit)
    save_summary(summary, args.output)
    print(f"✅ CI Summary saved to {args.output}")


if __name__ == "__main__":
    main()
