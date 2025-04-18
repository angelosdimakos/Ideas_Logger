import ast
from typing import Dict, Tuple, Optional, Union


class MethodRangeVisitor(ast.NodeVisitor):
    """
    Collects start and end line numbers for each function or async method,
    keyed by 'ClassName.method' for methods or just 'function' for top-level functions.
    Nested classes are also visited.
    """

    def __init__(self) -> None:
        self.ranges: Dict[str, Tuple[int, int]] = {}
        self.current_class: Optional[str] = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
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
        self._record_range(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record_range(node)

    def _record_range(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> None:
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
    Parse a Python file and return a dict mapping each function or method
    to its (start_lineno, end_lineno).

    Args:
        file_path: Path to the Python source file.

    Returns:
        A dict { "function" or "Class.method": (start, end) }.

    Raises:
        FileNotFoundError, IOError, or SyntaxError if the file cannot be read or parsed.
    """
    # Let file I/O and syntax errors propagate to the caller
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=file_path)

    visitor = MethodRangeVisitor()
    visitor.visit(tree)
    return visitor.ranges
