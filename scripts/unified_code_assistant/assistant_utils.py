# utils.py

import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def load_report(path: str) -> Dict[str, Any]:
    logger.info(f"Loading report from {path}")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load report: {e}")
        raise

def extract_code_snippets(file_path: str, issue_locations: List[Dict[str, Any]], context_lines: int = 3) -> Dict[str, str]:
    full_path = Path(file_path)
    if not full_path.exists():
        logger.warning(f"File not found: {file_path}")
        return {}

    try:
        lines = full_path.read_text(encoding='utf-8').splitlines()
        return {
            f"{issue.get('type', 'unknown')}_{issue['line_number']}": _format_snippet(lines, issue['line_number'], context_lines)
            for issue in issue_locations
            if isinstance(issue.get('line_number'), int)
        }
    except Exception as e:
        logger.error(f"Error extracting snippets from {file_path}: {e}")
        return {}

def _format_snippet(lines: List[str], line_num: int, context_lines: int) -> str:
    start = max(0, line_num - context_lines - 1)
    end = min(len(lines), line_num + context_lines)
    return '\n'.join(
        f"{i + 1:4d} {'→ ' if i == line_num - 1 else '  '}{lines[i]}"
        for i in range(start, end)
    )

def get_issue_locations(file_path: str, report_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    if file_path not in report_data:
        return []
    file_data = report_data[file_path]
    return (
        _extract_mypy_issues(file_data) +
        _extract_lint_issues(file_data) +
        _extract_complexity_issues(file_data)
    )

def _extract_mypy_issues(file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            'type': 'mypy',
            'line_number': e['line'],
            'message': e.get('message', ''),
            'severity': 'error'
        }
        for e in file_data.get("mypy", {}).get("errors", [])
        if 'line' in e
    ]

def _extract_lint_issues(file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            'type': 'lint',
            'line_number': i['line'],
            'message': i.get('message', ''),
            'severity': i.get('severity', 'warning')
        }
        for i in file_data.get("lint", {}).get("issues", [])
        if 'line' in i
    ]

def _extract_complexity_issues(file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            'type': 'complexity',
            'line_number': f.get('line_number', 0),
            'message': f"High complexity ({f.get('complexity', 0)}) in function {f.get('name', 'unknown')}",
            'severity': 'warning'
        }
        for f in file_data.get("complexity", {}).get("functions", [])
        if f.get('complexity', 0) > 10
    ]
