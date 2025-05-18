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