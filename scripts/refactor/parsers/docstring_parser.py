#!/usr/bin/env python3
"""
Docstring Parser
===============================
This module scans a Python project directory for missing or partial docstrings.

It outputs structured JSON and markdown-style reports with description, args, and return sections.
Also supports generating MkDocs-compatible markdown files.
"""

import ast
import argparse
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys
from collections import defaultdict


script_path = Path(__file__).resolve()
project_root = script_path.parents[3]  # should point to your repo root
sys.path.insert(0, str(project_root))

from scripts.refactor.lint_report_pkg.path_utils import norm

DEFAULT_EXCLUDES = {".venv", "venv", "__pycache__", ".git", "build", "dist"}


def split_docstring_sections(docstring: Optional[str]) -> Dict[str, Optional[str]]:
    """
    Split a docstring into its sections: description, args, and returns.

    Args:
        docstring (Optional[str]): The docstring to split.

    Returns:
        Dict[str, Optional[str]]: A dictionary containing the sections: description, args, and returns.
    """
    sections: Dict[str, Optional[str]] = {"description": None, "args": None, "returns": None}
    if not docstring:
        return sections

    lines = docstring.strip().splitlines()
    current_section = "description"
    collected: Dict[str, List[str]] = {"description": [], "args": [], "returns": []}

    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("args:"):
            current_section = "args"
            continue
        elif stripped.lower().startswith("returns:"):
            current_section = "returns"
            continue
        if stripped:
            collected[current_section].append(stripped)

    sections["description"] = "\n".join(collected["description"]) or None
    sections["args"] = "\n".join(collected["args"]) or None
    sections["returns"] = "\n".join(collected["returns"]) or None

    return sections


class DocstringAnalyzer:
    def __init__(self, exclude_dirs: List[str]) -> None:
        """
        Initialize the DocstringAnalyzer with directories to exclude.

        Args:
            exclude_dirs (List[str]): A list of directories to exclude from analysis.
        """
        self.exclude_dirs = set(exclude_dirs)

    def should_exclude(self, path: Path) -> bool:
        """
        Determine if a given path should be excluded from analysis.

        Args:
            path (Path): The path to check.

        Returns:
            bool: True if the path should be excluded, False otherwise.
        """
        parts = set(path.parts)
        return bool(parts & self.exclude_dirs)

    def extract_docstrings(self, file_path: Path) -> Dict[str, Any]:
        """
        Extracts and organizes docstrings from a Python file, including module, class, and function docstrings.
        
        Recursively parses the given Python file to collect docstrings from the module, all classes, and all functions. Each docstring is split into description, args, and returns sections if present.
        
        Args:
            file_path: Path to the Python file to analyze.
        
        Returns:
            A dictionary with keys "module_doc", "classes", and "functions", each containing extracted docstring information.
        """
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            return {}

        if tree is None:
            return {}

        docstring = None
        if isinstance(tree, ast.Module) and tree.body:
            first_node = tree.body[0]
            if isinstance(first_node, (ast.Expr,)) and isinstance(first_node.value, ast.Str):
                docstring = first_node.value.s
        result = {
            "module_doc": split_docstring_sections(docstring),
            "classes": [],
            "functions": [],
        }

        def visit_node(node):
            if isinstance(node, ast.ClassDef):
                doc = split_docstring_sections(ast.get_docstring(node))
                result["classes"].append(
                    {
                        "name": node.name,
                        "description": doc["description"],
                        "args": doc["args"],
                        "returns": doc["returns"],
                    }
                )
            elif isinstance(node, ast.FunctionDef):
                doc = split_docstring_sections(ast.get_docstring(node))
                result["functions"].append(
                    {
                        "name": node.name,
                        "description": doc["description"],
                        "args": doc["args"],
                        "returns": doc["returns"],
                    }
                )
            for child in ast.iter_child_nodes(node):
                visit_node(child)

        visit_node(tree)
        return result

    def analyze_directory(self, root: Path) -> Dict[str, Dict[str, Any]]:
        """
        Recursively analyzes Python files in a directory, extracting docstring information.
        
        Scans all `.py` files under the specified root directory, skipping excluded directories and files starting with `test_`. Returns a dictionary mapping normalized file paths to their extracted docstring details.
        """
        results = {}
        for file in root.rglob("*.py"):
            if self.should_exclude(file) or file.name.startswith("test_"):
                continue
            if any(exclude in file.parts for exclude in self.exclude_dirs):
                continue

            rel_path = norm(file)
            results[rel_path] = self.extract_docstrings(file)

        return results





class DocstringAuditCLI:
    def __init__(self) -> None:
        """
        Initializes the DocstringAuditCLI with parsed command-line arguments and a docstring analyzer.
        """
        self.args = self.parse_args()
        self.analyzer = DocstringAnalyzer(self.args.exclude)

    def parse_args(self) -> argparse.Namespace:
        """
        Parse command-line arguments.

        Returns:
            argparse.Namespace: The parsed command-line arguments.
        """
        parser = argparse.ArgumentParser(description="Audit Python files for missing docstrings.")
        parser.add_argument("--path", type=str, default=".", help="Root directory to scan")
        parser.add_argument(
            "--exclude",
            nargs="+",
            default=list(DEFAULT_EXCLUDES),
            help="Directories to exclude from scan",
        )
        parser.add_argument("--json", action="store_true", help="Output JSON report")
        parser.add_argument("--markdown", action="store_true", help="Output Markdown report")
        parser.add_argument(
            "--check", action="store_true", help="Exit 1 if missing docstrings found"
        )
        return parser.parse_args()

    def run(self) -> None:
        """
        Executes the docstring audit based on command-line arguments.
        
        Resolves the target directory, analyzes Python files for docstring completeness, and outputs results in JSON format if specified. Prints a placeholder for Markdown output if requested. Exits with status 1 if the check flag is set and any missing docstrings are detected.
        """
        root = Path(self.args.path).resolve()
        results = self.analyzer.analyze_directory(root)

        if self.args.json:
            output_path = Path.cwd() / "docstring_summary.json"
            output_path.write_text(
                json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            print(f"✅ JSON written to {output_path}")

        if self.args.markdown:
            print("🔧 Markdown output not yet implemented for structured fields.")



        if self.args.check:
            has_missing = any(
                not info["module_doc"]["description"]
                or any(not cls["description"] for cls in info["classes"])
                or any(not fn["description"] for fn in info["functions"])
                for info in results.values()
            )
            if has_missing:
                exit(1)


if __name__ == "__main__":
    DocstringAuditCLI().run()