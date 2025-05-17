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

✅ Related Docs

    Testing Guide

    Troubleshooting


---

Want `architecture.md` next?

You said:
Yes
ChatGPT said:

Here’s the complete architecture.md as plain text — outlining your codebase layout and flow:

# 🧭 ZephyrusLogger Architecture

ZephyrusLogger is structured as a layered, modular application with clear separation between core logic, GUI, indexing, and utilities.

This guide walks through the project layout, data flow, and key components.

---

## 🗂️ Folder Structure

scripts/ ├── ai/ # Summarization logic, LLM adapters ├── config/ # JSON loader, defaults, logging ├── core/ # Main controller + summary tracker ├── gui/ # PyQt GUI and interaction logic ├── indexers/ # FAISS-based vector index and metadata ├── refactor/ # Code analysis, complexity, diff tooling ├── utils/ # File zipping, path helpers, CLI tools ├── main.py # Entrypoint to launch GUI or CLI ├── paths.py # Centralized path resolver


Tests are located in:

tests/ ├── unit/ ├── integration/ ├── smoke/ ├── mocks/


---

## 🔁 Execution Flow

### GUI or CLI launches:
```python
python scripts/main.py

    Loads config/config.json

    Initializes ZephyrusLoggerCore

        Loads tracker, indexers, summarizer

    Enters GUI loop (if enabled) or processes CLI inputs

🧠 Core Components
Module	Purpose
core/summary_tracker.py	Maintains metadata and category-level summary coverage
ai/ai_summarizer.py	Calls LLM using prompt based on selected subcategory
indexers/summary_indexer.py	Stores vector embeddings via FAISS
indexers/raw_log_indexer.py	Stores raw logs (non-summarized)
config/config_loader.py	Reads and validates JSON config
refactor/refactor_guard.py	Analyzes changes between refactored files
gui/	Handles dropdowns, prompts, logging window, coverage stats
📊 Vector Index Design

Each summary has:

    a raw input

    a summarized output

    a subcategory label

    a vector embedding

These are saved to:

    .faiss index

    .json metadata file (with UUIDs, timestamps, labels)

🧰 RefactorGuard Toolchain

RefactorGuard uses:

    ast parsing to extract classes/methods

    complexity_analyzer.py to calculate cyclomatic scores

    coverage_parser.py (optional) to extract test coverage

🖥️ GUI Overview

The GUI builds:

    Left: coverage table (category_structure)

    Center: text input + AI output

    Right: raw logs + config preview

    Bottom: logging window (real-time logs)

It uses widget_factory.py, style_manager.py, and gui_controller.py to modularize behavior.
🧪 CI Flow

CI runs:

    Full pytest suite

    Coverage reporting (coverage.xml, htmlcov/)

    Refactor audit (refactor_guard_cli.py)

    Summary statistics: methods, files, missing tests

