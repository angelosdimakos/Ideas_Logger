#!/usr/bin/env python3
"""
Documentation Generator Router Adapter
=====================================
Adapter for generating documentation based on files identified by the CI Router.

This tool reads the CI Router report and generates documentation only for the changed
files, avoiding regenerating documentation for unchanged files.

Usage:
    python docs_router.py --router-report artifacts/router/router_summary.json --output-dir docs/api
"""

import sys
import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Set

# Ensure the repo root is on sys.path so we can import project modules
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the docs router adapter."""
    parser = argparse.ArgumentParser(
        description="Generate documentation for files changed according to CI Router."
    )
    parser.add_argument(
        "--router-report",
        required=True,
        help="Path to CI Router report JSON file"
    )
    parser.add_argument(
        "--docstrings",
        help="Path to docstring summary JSON file",
        default="artifacts/docstring-summary/docstring_summary.json"
    )
    parser.add_argument(
        "--output-dir",
        help="Directory to write documentation files",
        default="docs/api"
    )
    parser.add_argument(
        "--rebuild-all",
        action="store_true",
        help="Rebuild all documentation regardless of changes"
    )
    return parser.parse_args()


def get_changed_files(router_report_path: str) -> List[str]:
    """
    Extract the list of changed files from the router report.

    Args:
        router_report_path: Path to the router summary JSON file

    Returns:
        List of changed file paths
    """
    try:
        with open(router_report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)

        # Filter for Python files only, excluding tests
        changed_files = [
            f for f in report_data.get("changed_files", [])
            if f.endswith(".py") and "test_" not in f and "/tests/" not in f
        ]
        return changed_files
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading router report: {e}")
        return []


def get_affected_modules(changed_files: List[str]) -> Set[str]:
    """
    Determine which modules are affected by the changed files.

    Args:
        changed_files: List of changed file paths

    Returns:
        Set of affected module names
    """
    affected_modules = set()

    for file_path in changed_files:
        # Extract module name (without extension)
        module_name = Path(file_path).stem
        affected_modules.add(module_name)

        # Also add the directory name as a potential module
        dir_name = Path(file_path).parent.name
        if dir_name and dir_name != ".":
            affected_modules.add(dir_name)

    return affected_modules


def load_docstring_summary(docstrings_path: str) -> Dict[str, Any]:
    """
    Load the docstring summary JSON file.

    Args:
        docstrings_path: Path to the docstring summary JSON file

    Returns:
        Dictionary with docstring data
    """
    try:
        if os.path.exists(docstrings_path):
            with open(docstrings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"Docstring summary file not found: {docstrings_path}")
            return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from {docstrings_path}: {e}")
        return {}
    except Exception as e:
        print(f"Error loading docstring summary from {docstrings_path}: {e}")
        return {}


def filter_docstring_summary(
        docstring_data: Dict[str, Any],
        affected_modules: Set[str],
        rebuild_all: bool = False
) -> Dict[str, Any]:
    """
    Filter the docstring summary to include only affected modules.

    Args:
        docstring_data: Dictionary with docstring data
        affected_modules: Set of affected module names
        rebuild_all: Whether to include all modules regardless of changes

    Returns:
        Dictionary with filtered docstring data
    """
    if rebuild_all:
        return docstring_data

    filtered_data = {}

    for file_path, doc_data in docstring_data.items():
        # Extract module name from file path
        module_name = Path(file_path).stem
        dir_name = Path(file_path).parent.name

        # Include if the module is affected
        if module_name in affected_modules or dir_name in affected_modules:
            filtered_data[file_path] = doc_data

    return filtered_data


def generate_markdown_docs(
        docstring_data: Dict[str, Any],
        output_dir: str
) -> None:
    """
    Generate markdown documentation files from docstring data.

    Args:
        docstring_data: Dictionary with docstring data
        output_dir: Directory to write documentation files
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Group by directory
    modules_by_dir = {}

    for file_path, doc_data in docstring_data.items():
        dir_name = Path(file_path).parent.name
        if dir_name not in modules_by_dir:
            modules_by_dir[dir_name] = []
        modules_by_dir[dir_name].append((file_path, doc_data))

    # Generate index file
    index_path = os.path.join(output_dir, "index.md")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("# API Documentation\n\n")
        f.write("## Modules\n\n")

        for dir_name, modules in sorted(modules_by_dir.items()):
            if dir_name == ".":
                dir_name = "Root"
            f.write(f"### {dir_name}\n\n")

            for file_path, _ in sorted(modules):
                module_name = Path(file_path).stem
                module_file = f"{dir_name}_{module_name}.md" if dir_name != "Root" else f"{module_name}.md"
                module_file = module_file.replace("/", "_")
                f.write(f"- [{module_name}](./{module_file})\n")
            f.write("\n")

    # Generate module files
    for dir_name, modules in modules_by_dir.items():
        for file_path, doc_data in modules:
            module_name = Path(file_path).stem
            module_file = f"{dir_name}_{module_name}.md" if dir_name != "." else f"{module_name}.md"
            module_file = module_file.replace("/", "_")

            with open(os.path.join(output_dir, module_file), 'w', encoding='utf-8') as f:
                # Module header
                f.write(f"# {module_name}\n\n")

                # Module docstring
                module_doc = doc_data.get("module_doc", {})
                if module_doc.get("description"):
                    f.write(f"{module_doc['description']}\n\n")

                # Classes
                classes = doc_data.get("classes", [])
                if classes:
                    f.write("## Classes\n\n")
                    for cls in classes:
                        f.write(f"### {cls['name']}\n\n")
                        if cls.get("description"):
                            f.write(f"{cls['description']}\n\n")

                        # Class arguments
                        if cls.get("args"):
                            f.write("**Arguments:**\n\n")
                            for arg in cls["args"]:
                                f.write(f"- `{arg}`\n")
                            f.write("\n")

                # Functions
                functions = doc_data.get("functions", [])
                if functions:
                    f.write("## Functions\n\n")
                    for func in functions:
                        f.write(f"### {func['name']}\n\n")
                        if func.get("description"):
                            f.write(f"{func['description']}\n\n")

                        # Function arguments
                        if func.get("args"):
                            f.write("**Arguments:**\n\n")
                            for arg in func["args"]:
                                f.write(f"- `{arg}`\n")
                            f.write("\n")

                        # Return value
                        if func.get("returns"):
                            f.write(f"**Returns:** `{func['returns']}`\n\n")


def main() -> None:
    """Main entry point for the docs router adapter."""
    args = parse_args()

    # Get changed files from router report
    changed_files = get_changed_files(args.router_report)

    if not changed_files and not args.rebuild_all:
        print("No Python files changed that require documentation updates")
        return

    # Get affected modules
    affected_modules = get_affected_modules(changed_files)

    if affected_modules:
        print(f"Generating documentation for modules: {', '.join(sorted(affected_modules))}")
    elif args.rebuild_all:
        print("Rebuilding all documentation")

    # Load docstring summary
    docstring_data = load_docstring_summary(args.docstrings)

    if not docstring_data:
        print("No docstring data found")
        return

    # Filter docstring summary
    filtered_data = filter_docstring_summary(docstring_data, affected_modules, args.rebuild_all)

    if not filtered_data:
        print("No documentation to generate after filtering")
        return

    # Generate markdown documentation
    generate_markdown_docs(filtered_data, args.output_dir)

    print(f"Documentation generated in {args.output_dir}")
    print(f"Generated documentation for {len(filtered_data)} files")


if __name__ == "__main__":
    main()