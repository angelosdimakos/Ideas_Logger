"""
Command Line Interface for Zephyrus Logger
===============================
This module provides a command-line interface for the Zephyrus Logger application,
allowing users to log entries, summarize categories, and search through logs.
"""

import typer
from scripts.core.core import ZephyrusLoggerCore

app = typer.Typer()
core = ZephyrusLoggerCore(".")


@app.command()
def log(main: str, sub: str, entry: str) -> None:
    """
    Log a new entry to JSON and Markdown.

    Parameters:
        main (str): The main category for the log entry.
        sub (str): The subcategory for the log entry.
        entry (str): The content of the log entry.
    """
    if core.save_entry(main, sub, entry):
        typer.echo("✅ Entry saved successfully.")
    else:
        typer.echo("❌ Failed to save entry.")


@app.command()
def summarize(main: str, sub: str) -> None:
    """
    Force summarization of a category/subcategory.

    Parameters:
        main (str): The main category for the summary.
        sub (str): The subcategory for the summary.
    """
    if core.generate_global_summary(main, sub):
        typer.echo("🧠 Summary generated.")
    else:
        typer.echo("⚠️  Not enough entries or summarization failed.")


@app.command()
def search(query: str, top_k: int = 5, kind: str = "summary") -> None:
    """
    Search summaries or raw logs.

    Parameters:
        query (str): The search query.
        top_k (int): The number of top results to return.
        kind (str): The type of search ('summary' or 'raw').
    """
    results = (
        core.search_summaries(query, top_k)
        if kind == "summary"
        else core.search_raw_logs(query, top_k)
    )
    for i, res in enumerate(results):
        typer.echo(f"{i+1}. {res}")


if __name__ == "__main__":
    app()
