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
        Extract docstrings from a Python file, recursively.

        Args:
            file_path (Path): The path to the Python file to analyze.

        Returns:
            Dict[str, Any]: A dictionary containing docstring information.
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
        Analyze all Python files in the given directory and its subdirectories.

        Args:
            root (Path): The path to the directory to analyze.

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary with normalized file paths as keys and
            dictionaries with docstring information as values.
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

    def generate_mkdocs_markdown(self, results: Dict[str, Dict[str, Any]], output_dir: Path) -> None:
        """
        Generate MkDocs-compatible markdown files from docstring analysis results.

        Args:
            results (Dict[str, Dict[str, Any]]): Docstring analysis results.
            output_dir (Path): Directory to write markdown files to.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create module index
        index_content = "# API Documentation\n\n"
        index_content += "This documentation is automatically generated from docstrings.\n\n"

        # Group files by directories for better navigation
        file_groups = {}
        for file_path, docstrings in results.items():
            # Skip files without docstrings
            if not docstrings:
                continue

            parts = file_path.split('/')
            if len(parts) > 1:
                group = parts[0]
                if group not in file_groups:
                    file_groups[group] = []
                file_groups[group].append((file_path, docstrings))
            else:
                if "root" not in file_groups:
                    file_groups["root"] = []
                file_groups["root"].append((file_path, docstrings))

        # Add links to modules in index
        for group, files in file_groups.items():
            index_content += f"## {group}\n\n"

            # Create section directory
            section_dir = output_dir / group
            section_dir.mkdir(exist_ok=True)

            for file_path, docstrings in files:
                # Generate filename for markdown
                file_name = file_path.replace("/", ".").replace(".py", "")
                md_filename = file_name + ".md"
                relative_link = f"{group}/{file_name}.md"

                module_name = file_path.replace(".py", "").replace("/", ".")
                index_content += f"- [{module_name}]({relative_link})\n"

                # Generate module documentation
                self._generate_module_markdown(file_path, docstrings, section_dir / file_name)

            index_content += "\n"

        # Write index file
        (output_dir / "index.md").write_text(index_content, encoding="utf-8")

    def generate_mkdocs_markdown(self, results: Dict[str, Dict[str, Any]], output_dir: Path) -> None:
        """
        Generate MkDocs-compatible markdown files from docstring analysis results.
        Now mirrors the structure of quality and coverage reports.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        index_lines = ["# API Documentation\n", "This documentation is automatically generated from docstrings.\n"]

        folder_outputs = defaultdict(list)
        IGNORED_PREFIXES = ("tests", "artifacts")

        for file_path, docstrings in results.items():
            if not docstrings:
                continue

            folder = Path(file_path).parent.as_posix()
            if any(folder == p or folder.startswith(f"{p}/") for p in IGNORED_PREFIXES):
                continue

            folder_outputs[folder].append((file_path, docstrings))

        for folder in sorted(folder_outputs):
            safe_name = folder.replace("/", "_")
            section_file = output_dir / f"{safe_name}.md"
            lines = [f"# Docstring Report for `{folder}/`\n"]

            for file_path, docstrings in sorted(folder_outputs[folder]):
                module_name = file_path.replace(".py", "").replace("/", ".")
                lines.append(f"## `{module_name}`\n")

                # Module docstring
                if docstrings.get("module_doc", {}).get("description"):
                    lines.append(docstrings["module_doc"]["description"] + "\n")

                # Classes
                if docstrings.get("classes"):
                    lines.append("### Classes")
                    for cls in docstrings["classes"]:
                        lines.append(f"#### {cls['name']}")
                        if cls["description"]:
                            lines.append(cls["description"])
                        if cls["args"]:
                            lines.append("**Constructor Arguments:**\n" + cls["args"])

                # Functions
                if docstrings.get("functions"):
                    lines.append("### Functions")
                    for fn in docstrings["functions"]:
                        lines.append(f"#### {fn['name']}")
                        if fn["description"]:
                            lines.append(fn["description"])
                        if fn["args"]:
                            lines.append("**Arguments:**\n" + fn["args"])
                        if fn["returns"]:
                            lines.append("**Returns:**\n" + fn["returns"])

            section_file.write_text("\n\n".join(lines), encoding="utf-8")
            index_lines.append(f"- [{folder}/]({safe_name}.md)")

        # Write index
        (output_dir / "index.md").write_text("\n".join(index_lines), encoding="utf-8")


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
        parser.add_argument(
            "--mkdocs", action="store_true", help="Generate MkDocs-compatible markdown files"
        )
        parser.add_argument(
            "--mkdocs-dir", type=str, default="docs/api",
            help="Directory to write MkDocs markdown files to (relative to project root)"
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

        if self.args.mkdocs:
            mkdocs_dir = Path(project_root) / self.args.mkdocs_dir
            self.analyzer.generate_mkdocs_markdown(results, mkdocs_dir)
            print(f"📚 MkDocs documentation generated in {mkdocs_dir}")

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