#!/usr/bin/env python3
"""
docstring_linter.py

Scan a Python project directory for missing or partial docstrings.
Outputs structured JSON and markdown-style reports with description, args, and return sections.
"""

import ast
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


DEFAULT_EXCLUDES = {".venv", "venv", "__pycache__", ".git", "build", "dist"}


def split_docstring_sections(docstring: Optional[str]) -> Dict[str, Optional[str]]:
    """Split a docstring into its sections: description, args, and returns.

    Args:
        docstring (Optional[str]): The docstring to split.

    Returns:
        Dict[str, Optional[str]]: A dictionary containing the sections: description, args, and returns.
    """
    sections = {"description": None, "args": None, "returns": None}
    if not docstring:
        return sections

    lines = docstring.strip().splitlines()
    current_section = "description"
    collected = {"description": [], "args": [], "returns": []}

    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("args:"):
            current_section = "args"
            continue
        elif stripped.lower().startswith("returns:"):
            current_section = "returns"
            continue

        collected[current_section].append(line)

    return {
        "description": "\n".join(collected["description"]).strip() or None,
        "args": "\n".join(collected["args"]).strip() or None,
        "returns": "\n".join(collected["returns"]).strip() or None,
    }


class DocstringAnalyzer:
    def __init__(self, exclude_dirs: List[str]):
        """Initialize the DocstringAnalyzer with directories to exclude.

        Args:
            exclude_dirs (List[str]): A list of directories to exclude from analysis.
        """
        self.exclude_dirs = set(exclude_dirs)

    def should_exclude(self, path: Path) -> bool:
        """Determine if a given path should be excluded from analysis.

        Args:
            path (Path): The path to check.

        Returns:
            bool: True if the path should be excluded, False otherwise.
        """
        return any(part in self.exclude_dirs for part in path.parts)

    def extract_docstrings(self, file_path: Path) -> Dict[str, Any]:
        """Extract docstrings from a Python file.

        Args:
            file_path (Path): The path to the Python file.

        Returns:
            Dict[str, Any]: A dictionary containing extracted docstrings.
        """
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            return {}

        result = {
            "module_doc": split_docstring_sections(ast.get_docstring(tree)),
            "classes": [],
            "functions": [],
        }

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                doc = split_docstring_sections(ast.get_docstring(node))
                result["classes"].append({
                    "name": node.name,
                    "description": doc["description"],
                    "args": doc["args"],
                    "returns": doc["returns"],
                })
            elif isinstance(node, ast.FunctionDef):
                doc = split_docstring_sections(ast.get_docstring(node))
                result["functions"].append({
                    "name": node.name,
                    "description": doc["description"],
                    "args": doc["args"],
                    "returns": doc["returns"],
                })

        return result

    def analyze_directory(self, root: Path) -> Dict[str, Dict[str, Any]]:
        """Analyze a directory for docstrings.

        Args:
            root (Path): The root directory to analyze.

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary containing extracted docstrings.
        """
        results = {}
        for file in root.rglob("*.py"):
            if self.should_exclude(file) or file.name.startswith("test_"):
                continue
            rel_path = str(file.relative_to(root))
            results[rel_path] = self.extract_docstrings(file)
        return results


class DocstringAuditCLI:
    def __init__(self):
        """Initialize the command-line interface for the docstring audit."""
        self.args = self.parse_args()
        self.analyzer = DocstringAnalyzer(self.args.exclude)

    def parse_args(self) -> argparse.Namespace:
        """Parse command-line arguments.

        Returns:
            argparse.Namespace: The parsed command-line arguments.
        """
        parser = argparse.ArgumentParser(description="Audit Python files for missing docstrings.")
        parser.add_argument("--path", type=str, default=".", help="Root directory to scan")
        parser.add_argument("--exclude", nargs="+", default=list(DEFAULT_EXCLUDES),
                            help="Directories to exclude from scan")
        parser.add_argument("--json", action="store_true", help="Output JSON report")
        parser.add_argument("--markdown", action="store_true", help="Output Markdown report")
        parser.add_argument("--check", action="store_true", help="Exit 1 if missing docstrings found")
        return parser.parse_args()

    def run(self) -> None:
        """Run the docstring audit."""
        root = Path(self.args.path).resolve()
        results = self.analyzer.analyze_directory(root)

        if self.args.json:
            output_path = Path("docstring_summary.json")
            output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"✅ JSON written to {output_path}")

        if self.args.markdown:
            print("🔧 Markdown output not yet implemented for structured fields.")

        if self.args.check:
            has_missing = any(
                not info["module_doc"]["description"] or
                any(not cls["description"] for cls in info["classes"]) or
                any(not fn["description"] for fn in info["functions"])
                for info in results.values()
            )
            if has_missing:
                exit(1)


if __name__ == "__main__":
    DocstringAuditCLI().run()
