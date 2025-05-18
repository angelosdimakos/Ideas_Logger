#!/usr/bin/env python3
"""
Split-by-Module Docstring Documentation Generator
================================================
Creates markdown documentation files from docstring analysis:
- One file per module/package
- Generated MkDocs-compatible output structure
- Index files with navigation links
"""

from __future__ import annotations

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import defaultdict


# ─── make "scripts." imports work when executed as a script ────────────────
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

# Import rendering functions
from scripts.doc_generation.doc_renderers import render_module_docs, render_docstring_index




def generate_split_docstring_docs(docstring_data: Dict[str, Dict[str, Any]], output_dir: Path):
    """
    Generates Markdown documentation files grouped by top-level folder from Python docstring data.
    
    Each folder (excluding those starting with "tests" or "artifacts") is documented in a single Markdown file, with an index file created for navigation. Output is structured for MkDocs compatibility.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    grouped = defaultdict(list)
    IGNORED_PREFIXES = ("tests", "artifacts")

    for file_path, data in docstring_data.items():
        if not data:
            continue

        norm = file_path.replace("\\", "/")
        if any(norm.startswith(f"{p}/") for p in IGNORED_PREFIXES):
            continue

        folder = Path(norm).parent.as_posix()
        grouped[folder].append((file_path, data))

    folders = []
    sections = []

    for folder in sorted(grouped):
        safe_name = folder.replace("/", "_") if folder else "root"
        output_file = output_dir / f"{safe_name}.md"

        module_lines = [f"# `{folder}`\n"]
        section_modules = []

        for file_path, doc in sorted(grouped[folder]):
            module_name = file_path.replace(".py", "").replace("/", ".")
            md_content = render_module_docs(file_path, doc)
            module_lines.append(md_content)
            section_modules.append((Path(file_path).stem, module_name))

        output_file.write_text("\n\n".join(module_lines), encoding="utf-8")
        folders.append(folder)
        sections.append((safe_name, section_modules))

    index_lines = render_docstring_index(sections)
    (output_dir / "index.md").write_text("\n".join(index_lines), encoding="utf-8")
    print(f"📚 Minimalist docstring docs generated to {output_dir}")






def main():
    """
    Parses command-line arguments and generates Markdown documentation from a docstring JSON file.
    
    This function expects the path to a JSON file containing docstring data and an output directory.
    It validates input, loads the docstring data, and invokes the documentation generation process.
    """
    parser = argparse.ArgumentParser(description="Generate docstring documentation files.")
    parser.add_argument("--docstrings", required=True, help="Path to docstring_summary.json file")
    parser.add_argument("--output", required=True, help="Output folder for markdown documentation")

    args = parser.parse_args()

    docstrings_path = Path(args.docstrings)
    output_dir = Path(args.output)

    if not docstrings_path.exists():
        print(f"❌ Docstrings file not found at {docstrings_path}")
        exit(1)

    try:
        with open(docstrings_path, 'r', encoding="utf-8") as f:
            docstring_data = json.load(f)
    except json.JSONDecodeError:
        print("❌ Failed to parse docstring_summary.json.")
        exit(1)

    generate_split_docstring_docs(docstring_data, output_dir)


if __name__ == "__main__":
    main()