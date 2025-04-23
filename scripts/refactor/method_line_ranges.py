"""
method_line_ranges.py

This module provides utilities for extracting the start and end line numbers of all functions and methods in a Python source file using the AST (Abstract Syntax Tree).

Core features include:
- The MethodRangeVisitor class, which traverses the AST to collect line ranges for top-level functions, class methods, and methods in nested classes.
- The extract_method_line_ranges function, which parses a Python file and returns a dictionary mapping each function or method (as "function" or "Class.method") to its (start_lineno, end_lineno) tuple.
- Handles both synchronous and asynchronous functions, and supports Python versions with or without the end_lineno attribute.
- Designed for use in code analysis, refactoring tools, and coverage mapping.

Intended to facilitate precise mapping of code structure for downstream analysis and tooling.
"""

import ast
from typing import Dict, Tuple, Optional, Union
import os


class MethodRangeVisitor(ast.NodeVisitor):
    """
    Collects start and end line numbers for each function or async method,
    keyed by 'ClassName.method' for methods or just 'function' for top-level functions.
    Nested classes are also visited.

    Attributes:
        ranges (Dict[str, Tuple[int, int]]): A dictionary mapping functions or methods to their line ranges.
        current_class (Optional[str]): The name of the current class being visited.
    """

    def __init__(self) -> None:
        """
        Initializes the MethodRangeVisitor with an empty dictionary for ranges
        and a placeholder for the current class name.
        """
        self.ranges: Dict[str, Tuple[int, int]] = {}
        self.current_class: Optional[str] = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Visits a class definition node and collects line ranges for its methods.

        Args:
            node (ast.ClassDef): The class definition node to visit.
        """
        prev_class = self.current_class
        self.current_class = node.name

        # Record ranges for direct methods
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.visit(item)

        # Recurse into nested classes
        for item in node.body:
            if isinstance(item, ast.ClassDef):
                self.visit(item)

        self.current_class = prev_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Visits a function definition node and records its line range.

        Args:
            node (ast.FunctionDef): The function definition node to visit.
        """
        self._record_range(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """
        Visits an asynchronous function definition node and records its line range.

        Args:
            node (ast.AsyncFunctionDef): The asynchronous function definition node to visit.
        """
        self._record_range(node)

    def _record_range(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> None:
        """
        Records the line range for a function or asynchronous function node.

        Args:
            node (Union[ast.FunctionDef, ast.AsyncFunctionDef]): The function or asynchronous function node to record.
        """
        # Start line is the definition line
        start = node.lineno
        # End line: use end_lineno if available, else find maximum in subtree
        end = getattr(node, "end_lineno", None)
        if end is None:
            end = max(getattr(n, "lineno", start) for n in ast.walk(node))
        # Build full name with optional class prefix
        if self.current_class:
            full_name = f"{self.current_class}.{node.name}"
        else:
            full_name = node.name
        self.ranges[full_name] = (start, end)


def extract_method_line_ranges(file_path: str) -> Dict[str, Tuple[int, int]]:
    """
    Parses a Python file and returns a dict mapping each function or method
    to its (start_lineno, end_lineno).

    Args:
        file_path (str): Path to the Python source file.

    Returns:
        Dict[str, Tuple[int, int]]: A dict mapping functions or methods to their line ranges.

    Raises:
        FileNotFoundError: If the file cannot be found.
        IOError: If the file cannot be read.
        SyntaxError: If the file cannot be parsed.
    """
    if os.path.isdir(file_path):
        return {}

    # Let file I/O and syntax errors propagate to the caller
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=file_path)

    visitor = MethodRangeVisitor()
    visitor.visit(tree)
    return visitor.ranges
