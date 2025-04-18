# complexity_analyzer.py

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
        self.function_scores: Dict[str, int] = {}
        self.current_class: str = ""

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        prev = self.current_class
        self.current_class = node.name
        # Compute complexity for direct methods
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.visit(item)
        # Recurse into nested classes
        for item in node.body:
            if isinstance(item, ast.ClassDef):
                self.visit_ClassDef(item)
        self.current_class = prev

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._compute_and_record(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)

    def _compute_and_record(self, node: ast.AST) -> None:
        """
        Calculate complexity for a function/method node and record it.
        """

        def count_nodes(n: ast.AST) -> int:
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
        """
        return dict(self.function_scores)


def calculate_function_complexity_map(file_path: str) -> Dict[str, int]:
    """
    Parse the given Python file and return a mapping from function/method
    full names to their cyclomatic complexity scores.

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

    On parse errors (syntax or I/O), prints a warning and returns -1.
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
    """
    warnings.warn(
        "calculate_cyclomatic_complexity_for_module is deprecated; "
        "use calculate_module_complexity instead",
        DeprecationWarning,
        stacklevel=2
    )
    return calculate_module_complexity(module_path)
