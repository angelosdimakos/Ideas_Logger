#!/usr/bin/env python3
"""
generate_codebase_kg.py

Builds Knowledge Graphs for a Python codebase using docstring summaries.
Analyzes module complexity (density, degree, busyness).
Colors graphs based on complexity.

Usage:
    - Load JSON docstring summary
    - Build Parent Graph (subpackages)
    - Build Child Graphs (per subpackage)
    - Analyze complexity
    - Visualize with color-coding
"""

import argparse
import logging
from typing import Dict, Any
import os
import sys

# allow importing from project root
toplevel = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, toplevel)

from scripts.kg.modules.graph_builder import CodebaseAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Generate Knowledge Graph from docstring summary JSON.")
    parser.add_argument("--json", type=str, required=True, help="Path to docstring_summary.json")
    parser.add_argument("--focus", type=str, default="scripts/refactor/", help="Prefix to filter modules")
    parser.add_argument("--export", type=str, choices=["graphml", "gexf"], help="Optional: export graph")
    args = parser.parse_args()

    # Initialize analyzer
    analyzer = CodebaseAnalyzer(args.json, args.focus)

    # Analyze codebase
    graph, density_report = analyzer.analyze()

    if density_report:
        # Print results
        print(f"Complexity Score for {args.focus}: {density_report['complexity_score']:.2f}")

        # Visualize
        analyzer.visualize(graph, density_report)

        # Export if requested
        if args.export:
            filename = analyzer.export_graph(graph, args.export)
            print(f"Graph exported as {args.export} file: {filename}")


if __name__ == "__main__":
    main()