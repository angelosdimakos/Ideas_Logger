from .refactor_parser import RefactorParser
from .lint_parser import LintParser


class CIInsightReport:
    def __init__(self):
        self.insights: dict[str, dict] = {}

    def add_insight(self, name: str, data: dict):
        self.insights[name] = data

    def generate_summary(self) -> str:
        lines = ["# 📊 CI Insight Report", ""]

        for name, data in self.insights.items():
            lines.append(f"## 🔍 {name.title().replace('_', ' ')}")
            issues = data.get("issues", [])
            lines.append(f"- Total issues found: **{len(issues)}**")

            # Optional metadata summaries
            if "file_count" in data:
                lines.append(f"- Files affected: **{data['file_count']}**")

            if "method_count" in data:
                lines.append(f"- Methods analyzed: **{data['method_count']}**")

            if "most_complex" in data:
                lines.append(f"- Most complex: `{data['most_complex']}`")

            if "longest_method" in data:
                lines.append(f"- Longest method: `{data['longest_method']}`")

            lines.append("")

            if issues:
                lines.append("**Top Issues:**")
                default_file = data.get("file", "N/A")
                for issue in issues[:5]:
                    if isinstance(issue, str):
                        file = default_file
                        line = None
                        msg = issue
                    else:
                        file = issue.get("file", default_file)
                        line = issue.get("line")
                        msg = issue.get("message", issue.get("description", str(issue)))
                    lines.append(
                        f"  - `{file}`"
                        + (f":`{line}`" if line is not None else "")
                        + f" — {msg}"
                    )
                if len(issues) > 5:
                    lines.append(f"  ...and {len(issues) - 5} more.\n")
            else:
                lines.append("  ✅ No issues found.\n")

        return "\n".join(lines)

    def save(self, filepath: str = "ci_summary.md"):
        """
        Writes the generated summary to a Markdown file.
        """
        summary = self.generate_summary()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(summary)
