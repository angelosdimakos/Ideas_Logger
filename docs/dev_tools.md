# 🧰 Developer Tools

ZephyrusLogger includes internal utilities to support better code hygiene, refactoring, and development workflows. This doc explains how to use each one.

---

## 🔧 RefactorGuard

RefactorGuard is a CLI tool that analyzes Python files and directories for:

- Method-level diffs (added, removed, renamed)
- Cyclomatic complexity scoring
- Test coverage analysis (via test files or `coverage.xml`)
- Renaming suggestions

### 🔹 Basic Usage

```bash
python scripts/refactor/refactor_guard_cli.py \
  --original old_version.py \
  --refactored new_version.py

🔹 Directory Comparison

python scripts/refactor/refactor_guard_cli.py \
  --refactored scripts \
  --all \
  --missing-tests \
  --complexity-warnings \
  --json

🔹 Output Flags
Flag	Purpose
--json	Outputs JSON result instead of raw string
--missing-tests	Identifies untested methods
--complexity-warnings	Shows complexity per method
--diff-only	Suppress complexity, only show changes
📦 Zip Utility

The zip_util.py script compresses .py files in your project for archiving or sharing.
Usage:

python scripts/utils/zip_util.py --exclude backup.zip

Excludes the output file from itself.
🧠 Complexity Analysis

RefactorGuard uses an internal complexity analyzer that scores:

    If / For / While

    Try / Except / With

    Boolean operations

Each method starts at complexity 1. Scores above a threshold (default: 10) are flagged.
📁 Project Scaffolding

Use scripts/paths.py and path_utils.py to resolve paths safely across environments. These modules abstract config-aware paths and support test overrides.
🧪 Dev Mode & Test Mode

Set these in config.json:

    "test_mode": true → Routes all paths to test_* equivalents

    "dev_mode": true → Enables additional debug logs

These are useful for CI, sandboxing, and local development.
✨ Coming Soon

    coverage_parser.py → Converts coverage XML into line/method coverage maps

    summary_exporter.py → Markdown/CSV export tooling

    dataset_builder.py → Generate datasets from logs and summaries