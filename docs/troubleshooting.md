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