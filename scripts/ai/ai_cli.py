# scripts/core_cli.py
"""
AI Command Line Interface for Zephyrus Logger
===============================
This module provides a command-line interface for the AI summarization
functionality within the Zephyrus Logger application, allowing users
to log entries, generate summaries, and search through logs.
"""
import argparse
import logging
from pathlib import Path

from scripts.core.core import ZephyrusLoggerCore
from scripts.ai.module_docstring_summarizer import main as summarize_module_report

logger = logging.getLogger(__name__)


def cli():
    """
    Command-line interface for the Zephyrus Logger AI functionalities.

    This function sets up the argument parser and defines the available
    subcommands for logging entries, summarizing categories, searching
    logs, and summarizing module docstrings.
    """
    parser = argparse.ArgumentParser(
        prog="zephyrus",
        description="Zephyrus Logger CLI – log ideas, generate summaries, and search entries"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Log entry
    log_cmd = subparsers.add_parser("log", help="Log a new entry to Zephyrus")
    log_cmd.add_argument("main_category", help="Main category (e.g., AI, UX, Hardware)")
    log_cmd.add_argument("subcategory", help="Subcategory (e.g., Prompting, CLI)")
    log_cmd.add_argument("entry", help="Text entry to log")

    # Summarize
    sum_cmd = subparsers.add_parser("summarize", help="Generate summaries for a category")
    sum_cmd.add_argument("main_category", help="Main category to summarize")
    sum_cmd.add_argument("subcategory", help="Subcategory to summarize")

    # Search
    search_cmd = subparsers.add_parser("search", help="Search summaries or raw logs")
    search_cmd.add_argument("query", help="Query string to search")
    search_cmd.add_argument("--type", choices=["summary", "raw"], default="summary", help="Search index type")
    search_cmd.add_argument("--top_k", type=int, default=5, help="Number of top results to return")

    # Module docstring summarizer
    modsum_cmd = subparsers.add_parser("modsum", help="Summarize a module docstring report")
    modsum_cmd.add_argument("json_path", type=Path, help="Path to docstring audit JSON file")

    args = parser.parse_args()

    if args.command == "modsum":
        summarize_module_report(args.json_path)
        return

    core = ZephyrusLoggerCore(".")

    if args.command == "log":
        ok = core.save_entry(args.main_category, args.subcategory, args.entry)
        print("✅ Logged successfully" if ok else "❌ Failed to log entry")

    elif args.command == "summarize":
        ok = core.generate_global_summary(args.main_category, args.subcategory)
        print("✅ Summary generated" if ok else "⚠️  No summary generated (not enough entries)")

    elif args.command == "search":
        fn = core.search_raw_logs if args.type == "raw" else core.search_summaries
        results = fn(args.query, args.top_k)
        if not results:
            print("🔍 No results found.")
        else:
            for idx, res in enumerate(results, 1):
                print(f"[{idx}] {res}")


if __name__ == "__main__":
    cli()
