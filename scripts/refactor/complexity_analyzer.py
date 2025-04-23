# complexity_analyzer.py

"""
complexity_analyzer.py

This module provides utilities for analyzing the cyclomatic complexity of Python functions, methods, and modules using the AST (Abstract Syntax Tree).

Core features include:
- Computing cyclomatic complexity for each function and method in a Python file, including support for nested classes.
- Summing per-function complexities to produce a module-level complexity score.
- Supporting Python 3.10+ match/case syntax in complexity calculations.
- Providing a ComplexityVisitor class for AST traversal and complexity computation.
- Handling syntax and I/O errors gracefully with warnings.
- Deprecated alias for backward compatibility.

Intended for use in code quality analysis, refactoring tools, and CI pipelines to help maintain manageable code complexity.
"""

import ast
import warnings
from typing import Dict, Any, Tuple

# Default complexity threshold (can be overridden by your CLI or config)
MAX_COMPLEXITY = 10

# AST node types that count as decision points for cyclomatic complexity
_DECISION_NODE_TYPES: Tuple[Any, ...] = (
    ast.If,
    ast.For,
    ast.While,
    ast.Try,
    ast.With,
    ast.BoolOp,
    ast.ExceptHandler,
    ast.ListComp,
    ast.DictComp,
    ast.SetComp,
    ast.GeneratorExp,
    ast.comprehension,
)

# Support match/case in Python 3.10+: add ast.Match and ast.match_case if available
if hasattr(ast, "Match"):
    nodes: Tuple[Any, ...] = (ast.Match,)
    if hasattr(ast, "match_case"):
        nodes += (ast.match_case,)
    _DECISION_NODE_TYPES += nodes


class ComplexityVisitor(ast.NodeVisitor):
    """
    Visits each top-level function or method definition and computes
    its cyclomatic complexity based on decision point nodes.
    Nested functions are entirely skipped; nested classes are recursed into.
    """

    def __init__(self) -> None:
        """
        Initializes the ComplexityVisitor with an empty dictionary for function scores
        and sets the current class name to an empty string.

        Returns:
            None
        """
        self.function_scores: Dict[str, int] = {}
        self.current_class: str = ""

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Visits a class definition node and computes the complexity of its methods.

        Args:
            node (ast.ClassDef): The class definition node to visit.

        Returns:
            None
        """
        prev_class = self.current_class
        self.current_class = node.name

        # Visit methods in the class
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
        Visits a function definition node and calculates its complexity.

        Args:
            node (ast.FunctionDef): The function definition node to visit.

        Returns:
            None
        """
        self._compute_and_record(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """
        Visits an asynchronous function definition node and calculates its complexity.

        Args:
            node (ast.AsyncFunctionDef): The asynchronous function definition node to visit.

        Returns:
            None
        """
        self._compute_and_record(node)

    def _compute_and_record(self, node: ast.AST) -> None:
        """
        Calculate complexity for a function/method node and record it.

        Args:
            node (ast.AST): The function or method node to analyze.

        Returns:
            None
        """

        def count_nodes(n: ast.AST) -> int:
            """
            Recursively counts the number of decision nodes in the given AST node.

            Args:
                n (ast.AST): The AST node to count decision nodes in.

            Returns:
                int: The number of decision nodes in the given AST node.
            """
            total = 0
            for child in ast.iter_child_nodes(n):
                # Skip nested function definitions entirely
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if isinstance(child, _DECISION_NODE_TYPES):
                    total += 1
                total += count_nodes(child)
            return total

        complexity = 1 + count_nodes(node)
        name = getattr(node, "name", "<anonymous>")
        full_name = f"{self.current_class}.{name}" if self.current_class else name
        self.function_scores[full_name] = complexity

    def get_scores(self) -> Dict[str, int]:
        """
        Return the computed complexity scores.

        Returns:
            Dict[str, int]: A dictionary mapping function/method names to their complexity scores.
        """
        return self.function_scores


def calculate_function_complexity_map(file_path: str) -> Dict[str, int]:
    """
    Parses the given Python file and returns a mapping from function/method
    full names to their cyclomatic complexity scores.

    Args:
        file_path (str): Path to the Python source file.

    Returns:
        Dict[str, int]: A mapping of function/method names to their complexity scores.

    On parse errors, prints a warning and returns an empty dict.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=file_path)
    except (SyntaxError, IOError) as e:
        print(f"⚠️ Failed to parse for complexity {file_path}: {e}")
        return {}

    visitor = ComplexityVisitor()
    visitor.visit(tree)
    return visitor.get_scores()


def calculate_module_complexity(module_path: str) -> int:
    """
    Sum all function/method complexities in the module and add 1 overhead.

    Args:
        module_path (str): Path to the Python module.

    Returns:
        int: The total complexity score for the module, or -1 on error.
    """
    # First, check that the file parses
    try:
        with open(module_path, "r", encoding="utf-8") as f:
            source = f.read()
        ast.parse(source, filename=module_path)
    except (SyntaxError, IOError) as e:
        print(f"⚠️ Failed to parse for complexity {module_path}: {e}")
        return -1

    # If parse succeeded, compute per-function scores
    scores = calculate_function_complexity_map(module_path)
    return sum(scores.values()) + 1


def calculate_cyclomatic_complexity_for_module(module_path: str) -> int:
    """
    Deprecated alias for calculate_module_complexity.

    Issues a DeprecationWarning and delegates to calculate_module_complexity.

    Args:
        module_path (str): Path to the Python module.

    Returns:
        int: The total complexity score for the module, or -1 on error.
    """
    warnings.warn(
        "calculate_cyclomatic_complexity_for_module is deprecated; "
        "use calculate_module_complexity instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return calculate_module_complexity(module_path)
