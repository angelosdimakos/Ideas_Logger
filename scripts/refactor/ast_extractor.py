import ast
from typing import List, Dict, Tuple


class ClassMethodInfo:
    """
    Holds information about methods in a single class.

    Attributes:
        class_name: Name of the class.
        methods: Mapping from method name to a tuple(start_lineno, end_lineno).
    """
    def __init__(self, class_name: str):
        self.class_name: str = class_name
        self.methods: Dict[str, Tuple[int, int]] = {}

    def add_method(self, name: str, linenos: Tuple[int, int]) -> None:
        """Record a method with its start and end line numbers."""
        self.methods[name] = linenos

    def __repr__(self) -> str:
        return f"<ClassMethodInfo {self.class_name}: methods={list(self.methods.keys())}>"


def extract_class_methods(file_path: str) -> List[ClassMethodInfo]:
    """
    Parse a Python file and extract all class methods with their line ranges.

    Args:
        file_path: Path to the Python source file.

    Returns:
        A list of ClassMethodInfo objects, each containing method names and their start/end line numbers.
        Returns an empty list if parsing fails.
    """

    # Let file errors or SyntaxError propagate to the caller
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=file_path)

    class ClassMethodExtractor(ast.NodeVisitor):
        def __init__(self):
            self.classes: List[ClassMethodInfo] = []

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            info = ClassMethodInfo(node.name)
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    start = item.lineno
                    end = getattr(item, 'end_lineno', None)
                    if end is None:
                        end = max(getattr(n, 'lineno', start) for n in ast.walk(item))
                    info.add_method(item.name, (start, end))
            self.classes.append(info)

            # Also process nested classes
            for item in node.body:
                if isinstance(item, ast.ClassDef):
                    self.visit(item)

            # Continue generic visits for other nested structures
            super().generic_visit(node)

        def generic_visit(self, node: ast.AST) -> None:
            """Visit all child nodes, to catch nested class definitions."""
            super().generic_visit(node)

    extractor = ClassMethodExtractor()
    extractor.visit(tree)
    return extractor.classes


def compare_class_methods(
    original: ClassMethodInfo,
    refactored: ClassMethodInfo
) -> Dict[str, List[str]]:
    """
    Compare two ClassMethodInfo objects and return which methods
    are missing in the refactored version and which are newly added.

    Returns:
        A dict with keys "missing" and "added", each mapping to a sorted list of method names.
    """
    orig_set = set(original.methods.keys())
    ref_set = set(refactored.methods.keys())

    missing = sorted(orig_set - ref_set)
    added = sorted(ref_set - orig_set)

    return {"missing": missing, "added": added}
