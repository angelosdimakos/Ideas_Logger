

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