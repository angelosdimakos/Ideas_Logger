#!/usr/bin/env python3
"""
Split-by-Folder Coverage Documentation Generator
===============================================
Creates one Markdown file per folder:
- ai.md, core.md, etc.
Also generates:
- index.md with folder links
"""

import argparse
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any


def render_folder_coverage(folder: str, entries: list) -> str:
    """Renders the markdown content for a single folder's coverage."""
    md = [f"# Test Coverage Report for `{folder}/`\n"]

    total_lines = sum(e[1]['summary'].get('num_statements', 0) for e in entries)
    covered_lines = sum(e[1]['summary'].get('covered_lines', 0) for e in entries)
    pct = (covered_lines / total_lines * 100) if total_lines > 0 else 0

    md.append(f"**Folder Coverage:** {pct:.2f}% ({covered_lines} of {total_lines} lines covered)\n")

    md += [
        "## 📄 File Coverage",
        "| File | Line Coverage | Branch Coverage |",
        "| ---- | ------------- | ---------------- |"
    ]

    for file_path, file_data in sorted(entries):
        summary = file_data.get("summary", {})
        line_cov = f"{summary.get('percent_covered', 0):.2f}%"
        if summary.get("num_branches", 0) > 0:
            branch_cov = f"{summary.get('percent_covered_branches', 0):.2f}%"
        else:
            branch_cov = "N/A"

        md.append(f"| {Path(file_path).name} | {line_cov} | {branch_cov} |")

    return "\n".join(md)


def generate_split_coverage_docs(coverage_data: Dict[str, Any], output_dir: Path):
    grouped = defaultdict(list)
    IGNORED_PREFIXES = ("tests", "artifacts")

    for file_path, file_data in coverage_data.get("files", {}).items():
        folder = Path(file_path).parent.as_posix()

        if any(folder == p or folder.startswith(f"{p}/") for p in IGNORED_PREFIXES):
            continue

        grouped[folder].append((file_path, file_data))

    output_dir.mkdir(parents=True, exist_ok=True)
    totals = coverage_data.get("totals", {})
    pct = f"{totals.get('percent_covered', 0):.2f}%"
    covered_lines = totals.get("covered_lines", 0)
    total_lines = totals.get("num_statements", 0)
    branches = totals.get("covered_branches", 0)
    total_branches = totals.get("num_branches", 0)

    index_lines = ["# Test Coverage Report Index\n", "## Summary\n"]
    index_lines += [
        "| Metric | Coverage |",
        "|--------|----------|",
        f"| Overall Coverage | {pct} |",
        f"| Lines Covered | {covered_lines} of {total_lines} |"
    ]
    if total_branches > 0:
        index_lines.append(f"| Branches Covered | {branches} of {total_branches} |")
    index_lines.append("")

    for folder in sorted(grouped):
        safe_name = folder.replace("/", "_")
        output_file = output_dir / f"{safe_name}.md"
        content = render_folder_coverage(folder, grouped[folder])
        output_file.write_text(content, encoding="utf-8")
        index_lines.append(f"- [{folder}/](./{safe_name}.md)")

    # Write index file
    index_path = output_dir / "index.md"
    index_path.write_text("\n".join(index_lines), encoding="utf-8")

    print(f"✅ Split coverage reports written to: {output_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Generate folder-based coverage documentation.")
    parser.add_argument("--coverage", required=True, help="Path to coverage.json file")
    parser.add_argument("--output", required=True, help="Output folder for markdown reports")

    args = parser.parse_args()

    coverage_path = Path(args.coverage)
    output_dir = Path(args.output)

    if not coverage_path.exists():
        print(f"❌ Coverage file not found at {coverage_path}")
        exit(1)

    try:
        with open(coverage_path, 'r') as f:
            coverage_data = json.load(f)
    except json.JSONDecodeError:
        print("❌ Failed to parse coverage.json.")
        exit(1)

    generate_split_coverage_docs(coverage_data, output_dir)


if __name__ == "__main__":
    main()
