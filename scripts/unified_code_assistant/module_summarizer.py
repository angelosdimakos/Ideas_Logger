# summarizer.py

from typing import Optional, Dict
from scripts.ai.ai_summarizer import AISummarizer
from scripts.ai import module_docstring_summarizer as docsum

def summarize_modules(report_data: Dict, summarizer: AISummarizer, config, path_filter: Optional[str] = None) -> Dict[str, str]:
    """
    Generate summaries of module functionality based on docstrings.

    Args:
        report_data (Dict): Parsed code analysis report.
        summarizer (AISummarizer): Summarization engine.
        config: Configuration object.
        path_filter (Optional[str]): Optional substring to filter files.

    Returns:
        Dict[str, str]: Mapping of file paths to summaries.
    """
    summaries = {}
    for file_path, data in report_data.items():
        if path_filter and path_filter not in file_path:
            continue

        docstrings_info = data.get("docstrings", {})
        funcs = docstrings_info.get("functions", [])

        if funcs:
            summaries[file_path] = docsum.summarize_module(file_path, funcs, summarizer, config)
        elif docstrings_info:
            summaries[file_path] = "Docstrings exist but no functions parsed."

    return summaries
