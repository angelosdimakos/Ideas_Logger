# scripts/ci_analyzer/lint_parser.py

import re
from pathlib import Path
from scripts.ci_analyzer.artifact_base import ArtifactParser

class LintParser(ArtifactParser):
    def __init__(self, path: str = None):
        self.path = Path(path) if path else None

    def parse(self, path: str = None) -> dict:
        """
        Parses a lint report file and returns a summary dict.

        Returns:
            Dict: {
                "type": "lint",
                "file": <filepath>,
                "issue_count": <int>,
                "issues": <List[str]>
            }
        """
        file_path = Path(path) if path else self.path
        if file_path is None:
            raise ValueError("No path specified for LintParser")

        lines = file_path.read_text(encoding="utf-8").splitlines()
        issues = [line.strip() for line in lines if line.strip()]

        return {
            "type": "lint",
            "file": str(file_path),
            "issue_count": len(issues),
            "issues": issues
        }
