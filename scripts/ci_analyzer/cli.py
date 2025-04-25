"""
cli.py

This module serves as the command-line entry point for the CI Analyzer tool.
It ensures the repository root is included in the Python path for proper imports,
and delegates execution to the main function in the orchestrator module.

Run this script directly to generate CI audit summaries and reports from the command line.
"""

# ci_analyzer/cli.py
import os
import sys

# Ensure repo root is in sys.path (so we can import scripts.*)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from scripts.ci_analyzer.orchestrator import main

if __name__ == "__main__":
    main()
