# Index

# ZephyrusLogger

ZephyrusLogger is a robust, modular logging and summarization framework designed for developers, designers, and writers working with iterative ideas, creative systems, or AI-driven workflows.

It combines the power of LLMs, semantic indexing (via FAISS), and user-friendly interfaces to help you track, analyze, and reflect on evolving concepts over time.

---

## ✨ Core Features

- 🧠 **AI Summarization**: Automatically distill raw ideas into structured summaries based on subcategories you define.
- 🔍 **Searchable Vector Index**: Store and retrieve summaries using semantic similarity via FAISS.
- 📊 **Coverage Tracking**: View real-time coverage stats across creative or technical categories.
- 🖥️ **Dual Interface**: Use the CLI for automation or launch a GUI for interactive logging and inspection.
- 🧪 **RefactorGuard**: Analyze Python code refactors with method diffs, complexity scoring, and test coverage checks.
- 🧰 **Developer Utilities**: Built-in tools for zipping, auditing, and maintaining high-code-quality standards.

---

## 📌 Use Cases

- Creative writing or game design logs with narrative + worldbuilding structure
- Technical notes or R&D experiments organized by functional areas
- Long-term AI system tracking with category-level reflection prompts
- Internal tooling for auditing and summarizing refactor progress

---

## 🔧 Tech Stack

- Python 3.11+
- PyQt5 (GUI)
- FAISS (vector similarity search)
- sentence-transformers (`all-MiniLM-L6-v2` by default)
- Optional: HuggingFace, OpenAI, Ollama

---

## 💡 Philosophy

ZephyrusLogger was built for power-users who want to *reason about their thinking*. It offers flexible logging with structured meaning, while remaining light enough for rapid prototyping and iteration.

Think of it as a **semantic journal**, backed by LLMs and embeddable search.

---

## 🔗 Next Steps

- [Installation Guide](install.md)
- [Configuration Reference](config.md)
- [Using the GUI or CLI](usage.md)
- [Testing & Coverage](testing.md)


---

# Install

# 🛠 Installation Guide

This guide walks you through setting up ZephyrusLogger in a local development or production environment.

---

## ✅ Requirements

- Python **3.11.x** (avoid 3.11.9 on Windows if using GUI — known tkinter issue)
- pip >= 21.0
- OS: Windows, macOS, Linux (tested on Windows + Ubuntu)

---

## 📦 1. Clone the Repo

```bash
git clone https://github.com/your-org/zephyrus-logger.git
cd zephyrus-logger

🐍 2. Set Up a Virtual Environment

python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

📦 3. Install Dependencies

python -m pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

    💡 For Windows + FAISS, install with:

pip install faiss-cpu --only-binary=faiss-cpu

💾 4. Optional: GPU Support (FAISS)

FAISS GPU isn't required, but if needed:

pip install faiss-gpu  # ⚠️ may require CUDA & compilation support

🧠 5. Optional: LLM Support

ZephyrusLogger supports multiple backends:

    OpenAI → Requires OPENAI_API_KEY or key in config.json

    Ollama → Local model serving, e.g., Mistral

Install dependencies for LLMs:

pip install openai sentence-transformers

🧪 6. Verify Installation

Run the canary test:

pytest tests/test_canary.py

Then launch the app:

python scripts/main.py

🧪 Troubleshooting
Problem	Solution
ModuleNotFoundError: scripts	Set PYTHONPATH=. or inject sys.path manually
FAISS file write error	Ensure vector_store/ directory exists
GUI fails to load	Check use_gui: true in config.json and tkinter installed

---

# Config



# ⚙️ Configuration Guide (`config.json`)

ZephyrusLogger is fully driven by a centralized `config.json` file located at:

config/config.json


This file controls everything from runtime behavior to GUI layout, LLM selection, vector indexing paths, and developer flags.

---

## 🔑 Top-Level Keys

| Key                     | Type     | Description |
|------------------------|----------|-------------|
| `mode`                 | string   | `"test"` or `"full"` – controls whether full indexing & vector storage are enabled |
| `use_gui`              | boolean  | Toggle GUI on launch |
| `test_mode`            | boolean  | If true, redirects paths to mock/test-safe folders |
| `dev_mode`             | boolean  | Enables logging/debugging flags |
| `markdown_export`      | boolean  | If true, allows Markdown export of entries |

---

## 🤖 LLM Settings

| Key               | Description |
|------------------|-------------|
| `llm_provider`   | `"openai"`, `"huggingface"`, `"ollama"` |
| `llm_model`      | Model name (e.g. `"gpt-3.5-turbo"`, `"mistral"`) |
| `embedding_model`| SentenceTransformers model name (e.g. `"all-MiniLM-L6-v2"`) – fallback if not defined |

---

## 🧠 Categories & Prompts

| Section             | Description |
|---------------------|-------------|
| `category_structure`| Maps each major category (e.g. `Narrative`, `World`) to subcategories (e.g. `Plot`, `Magic`, `Faction`) |
| `prompts_by_subcategory` | Maps each subcategory to a summarization prompt – this powers the AI guidance in the GUI or CLI |

Example:
```json
{
  "category_structure": {
    "Narrative": ["Plot", "Themes"],
    "World": ["Factions", "Magic"]
  },
  "prompts_by_subcategory": {
    "Plot": "Summarize this plot point...",
    "Magic": "Describe how this magic system functions..."
  }
}

📦 Storage Paths
Key	Description
summary_data_path	Where to save/load structured summary entries
raw_log_path	Where raw input text is saved
faiss_index_path	Vector index file (*.faiss)
faiss_metadata_path	JSON metadata matching vectors to entries
tracker_path	Saves overall category coverage tracker (summary_tracker.json)
gui_state_path	Remembers last selected dropdowns, inputs, etc.
🧪 Mock/Test Overrides

If test_mode: true, these paths override real ones:
Key	Description
test_summary_data_path	Summary JSON for test runs
test_raw_log_path	Raw logs for test runs
test_faiss_index_path	Temp index file
test_faiss_metadata_path	Temp metadata file
test_tracker_path	Tracker state for test runs
🧼 Tips

    You can reload config.json on-the-fly via CLI/GUI triggers.

    If any key is missing, ZephyrusLogger will log a warning and use a default.

    Invalid paths will not crash the app, but will skip indexing unless caught.

---

# Usage



# 🚀 Usage Guide

ZephyrusLogger can be used either as an **interactive GUI** or as a **CLI-based logging engine**. It’s designed to be flexible, scriptable, and modular.

---

## 🖥️ GUI Mode (Default)

To launch the graphical interface:

```bash
python scripts/main.py

Make sure use_gui is set to true in your config/config.json.
Key Features:

    Dropdown-based subcategory selection

    Prompt-assisted AI summarization

    Real-time coverage overview

    Logs visible inside app

    Markdown export (if enabled)

💻 CLI Mode

You can also run in headless CLI mode by setting:

"use_gui": false

Then run:

python scripts/main.py

This will process summaries and logs without the GUI, useful for automation or fast entry.
🧠 Logging an Idea

    Pick a subcategory (e.g., Narrative → Plot)

    Type or paste your raw input

    The system will:

        Apply a prompt (from config)

        Run the LLM

        Save both the input + summary

        Update your vector index and tracker

🧪 Run Refactor Audit (Dev Tool)

The built-in RefactorGuard lets you compare two versions of code and audit:

    Method diffs (added, removed, renamed)

    Cyclomatic complexity

    Missing test coverage

Example CLI usage:

python scripts/refactor/refactor_guard_cli.py \
  --original old_version.py \
  --refactored new_version.py \
  --tests test_file.py \
  --complexity-warnings \
  --missing-tests \
  --json

Or to audit the whole repo:

python scripts/refactor/refactor_guard_cli.py \
  --refactored scripts \
  --all \
  --missing-tests \
  --json

🧾 Zipping Code (for archiving)

python scripts/utils/zip_util.py --exclude my_backup.zip

This compresses all .py files into a single archive, excluding the zip file itself.
✅ Summary
Task	Command
Launch GUI	python scripts/main.py
Run CLI mode	use_gui: false + main.py
Run refactor audit	scripts/refactor/refactor_guard_cli.py
Zip project files	scripts/utils/zip_util.py

---

# Testing

# 🧪 Testing Guide

ZephyrusLogger includes a full-featured test suite covering unit, integration, and smoke tests, with CI integration via GitHub Actions and Codecov.

---

## ✅ Running Tests Locally

Make sure you’re in your virtual environment, then run:

```bash
pytest

To check coverage:

pytest --cov=scripts --cov-report=html --cov-report=xml

    🔍 This will:

        Show terminal summary

        Generate htmlcov/ folder for detailed UI

        Save coverage.xml for CI or audit analysis

🧪 Canary Test

Quick sanity test to verify base functionality:

pytest tests/test_canary.py

🧱 Test Structure
Folder	Purpose
tests/unit/	Pure logic and module tests
tests/integration/	Cross-component + system-level
tests/smoke/	GUI/CLI boot tests
tests/mocks/	Fake data + reusable fixtures
🧰 CI Integration (GitHub Actions)

You can find the CI logic in .github/workflows/pytest.yml.

This pipeline:

    Installs dependencies

    Runs tests and coverage

    Uploads coverage.xml to Codecov

    Saves htmlcov/ and refactor_audit.json as artifacts

    Summarizes complexity + audit metrics

    💡 CI fails if coverage.xml is missing or test errors occur

📈 Viewing Coverage

Run:

open htmlcov/index.html  # or start on Windows

🧪 Test Targets
File	What it Tests
test_summary_tracker.py	Tracker logic + fallback
test_ai_summarizer.py	Prompt flow + LLM stubs
test_gui_controller.py	GUI to backend interaction
test_config_loader.py	Fallback + file parse
test_indexers.py	FAISS loading + rebuild
test_refactor_guard.py	Refactor diff logic
🧼 Tips

    Use pytest -k <name> to run a single test

    Use @pytest.mark.slow for long integration tests

    Run black ., ruff ., or mypy as linter checks

---

# Dev Tools

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

---

# Architecture

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



---

# Troubleshooting

# 🧯 Troubleshooting & FAQ

This guide outlines common issues you might encounter when running ZephyrusLogger, and how to fix them.

---

## 🔧 Common Setup Issues

### ❌ `ModuleNotFoundError: scripts`
**Cause:** Python doesn’t recognize `scripts/` as a module.

**Fix:**

- Set your working directory to project root
- Or run:
  ```bash
  $env:PYTHONPATH = "."  # PowerShell
  export PYTHONPATH=.    # Bash

    Or inject this at the top of your script:

    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

❌ faiss::FileIOWriter Error

Cause: FAISS can't write to the index file because the directory doesn’t exist.

Fix: Ensure the following folder exists before starting:

mkdir vector_store

Or add this in code before saving:

index_path.parent.mkdir(parents=True, exist_ok=True)

❌ GUI Fails to Launch (no window)

Possible Causes:

    use_gui is set to false in config.json

    Missing tkinter on your Python install

    You’re in a headless (SSH) or WSL environment

Fixes:

    Set "use_gui": true

    On Windows, use Python from python.org — some WSL installs miss tkinter

    GUI is not supported in some remote environments (e.g., GitHub Codespaces)

❌ No Coverage XML Generated in CI

Cause: Pytest didn’t generate coverage.xml.

Fixes:

    Make sure you use:

pytest --cov=scripts --cov-report=xml

Add a CI step to check its presence:

    if [ ! -f coverage.xml ]; then echo "❌ Not found"; exit 1; fi

🧠 Debugging Tips

    Enable "dev_mode": true in config.json to show extra logs

    Set "test_mode": true to sandbox vector writes and paths

    Use print(json.dumps(config, indent=2)) anywhere to verify values

✅ GUI Dev Tips

    GUI state is saved to gui_state.json

    Prompt mapping comes from prompts_by_subcategory in config

    Add tooltips or validation in widget_factory.py if you want a better UX

💡 Logging

You can redirect logs to GUI and a file. Check:

    config_manager.py sets up logging

    gui_logging.py routes logs to QTextEdit widget

💬 Still Stuck?

If you’re debugging something unusual:

    Add print() inside core.py, summary_tracker.py, or ai_summarizer.py

    Run pytest -s for live output

    Use --json in RefactorGuard to get structured output

🔗 See Also

    Installation Guide

    Config Reference

    Developer Tools

---

