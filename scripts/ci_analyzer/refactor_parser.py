# scripts/ci_analyzer/refactor_parser.py

import json
from pathlib import Path
from scripts.ci_analyzer.artifact_base import ArtifactParser

class RefactorParser(ArtifactParser):
    def __init__(self, path: str = None):
        self.path = Path(path) if path else None

    def parse(self, path: str = None) -> dict:
        """
        Parses the refactor audit JSON file and returns summary dict.

        Returns:
            Dict: {
                "type": "refactor",
                "file_count": <int>,
                "method_count": <int>
            }
        """
        file_path = Path(path) if path else self.path
        if file_path is None:
            raise ValueError("No path specified for RefactorParser")

        with open(file_path, encoding="utf-8-sig") as f:
            data = json.load(f)

        file_count = len(data)
        method_count = sum(len(report.get("complexity", {})) for report in data.values())

        return {
            "type": "refactor",
            "file_count": file_count,
            "method_count": method_count
        }
