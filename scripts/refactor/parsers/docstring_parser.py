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
        self.exclude_dirs = set(exclude_dirs)

    def should_exclude(self, path: Path) -> bool:
        parts = set(path.parts)
        return bool(parts & self.exclude_dirs)

    def _format_args(self, args_node: ast.arguments) -> List[str]:
        def arg_str(arg):
            arg_type = ast.unparse(arg.annotation) if arg.annotation else "Any"
            return f"{arg.arg}: {arg_type}"

        args = [arg_str(a) for a in args_node.posonlyargs]
        args += [arg_str(a) for a in args_node.args]
        if args_node.vararg:
            args.append(f"*{args_node.vararg.arg}")
        args += [arg_str(a) for a in args_node.kwonlyargs]
        if args_node.kwarg:
            args.append(f"**{args_node.kwarg.arg}")
        return args

    def _get_return_type(self, func_node: ast.FunctionDef) -> str:
        if func_node.returns:
            try:
                return ast.unparse(func_node.returns)
            except Exception:
                return "Any"
        return "Any"

    def _process_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        doc = split_docstring_sections(ast.get_docstring(node))
        return {
            "name": node.name,
            "description": doc["description"],
            "args": self._format_args(node.args),
            "returns": self._get_return_type(node),
        }

    def _process_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        doc = split_docstring_sections(ast.get_docstring(node))
        init_args = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                init_args = self._format_args(item.args)
                break
        return {
            "name": node.name,
            "description": doc["description"],
            "args": init_args or None,
            "returns": "None",  # Class constructors implicitly return None
        }

    def extract_docstrings(self, file_path: Path) -> Dict[str, Any]:
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            return {}

        if tree is None:
            return {}

        # Module-level docstring
        docstring = None
        if isinstance(tree, ast.Module) and tree.body:
            first_node = tree.body[0]
            if isinstance(first_node, ast.Expr) and isinstance(first_node.value, ast.Str):
                docstring = first_node.value.s

        result = {
            "module_doc": split_docstring_sections(docstring),
            "classes": [],
            "functions": [],
        }

        # Visit each node recursively
        def visit(node):
            if isinstance(node, ast.ClassDef):
                result["classes"].append(self._process_class(node))
            elif isinstance(node, ast.FunctionDef):
                result["functions"].append(self._process_function(node))
            for child in ast.iter_child_nodes(node):
                visit(child)

        visit(tree)
        return result

    def analyze_directory(self, root: Path) -> Dict[str, Dict[str, Any]]:
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
        Initialize the command-line interface for the docstring audit.
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
        Run the docstring audit.
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