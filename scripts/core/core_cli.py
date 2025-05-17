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
    Logs a new entry under the specified main and subcategory.
    
    Args:
        main: Main category for the log entry.
        sub: Subcategory for the log entry.
        entry: Content of the log entry.
    
    The entry is saved in both JSON and Markdown formats.
    """
    if core.save_entry(main, sub, entry):
        typer.echo("✅ Entry saved successfully.")
    else:
        typer.echo("❌ Failed to save entry.")


@app.command()
def summarize(main: str, sub: str) -> None:
    """
    Generates a summary for the specified main category and subcategory.
    
    Args:
        main: The main category to summarize.
        sub: The subcategory to summarize.
    
    Prints a confirmation message if the summary is generated, or a warning if there are insufficient entries or the operation fails.
    """
    if core.generate_global_summary(main, sub):
        typer.echo("🧠 Summary generated.")
    else:
        typer.echo("⚠️  Not enough entries or summarization failed.")


@app.command()
def search(query: str, top_k: int = 5, kind: str = "summary") -> None:
    """
    Searches summaries or raw logs and displays the top results.
    
    Args:
        query: The search query string.
        top_k: Maximum number of results to display.
        kind: Specifies whether to search 'summary' or 'raw' logs. Defaults to 'summary'.
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
