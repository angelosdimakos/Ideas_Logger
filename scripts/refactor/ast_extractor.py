"""
ast_extractor.py

This module provides utilities for analyzing Python source files using the AST (Abstract Syntax Tree) to extract class and method information.

Core features include:
- Extracting all classes and their methods from a Python file, including method start and end line numbers.
- Supporting nested class and method extraction.
- Comparing two sets of class methods to identify missing or newly added methods after refactoring.
- Providing a ClassMethodInfo class to encapsulate class and method metadata for further analysis.

Intended for use in code analysis, refactoring tools, and automated quality checks.
"""

import ast
from typing import List, Dict, Tuple


class ClassMethodInfo:
    """
    Holds information about methods in a single class.

    Attributes:
        class_name (str): Name of the class.
        methods (Dict[str, Tuple[int, int]]): Mapping from method name to a tuple of (start_lineno, end_lineno).
    """

    def __init__(self, class_name: str) -> None:
        """
        Initializes ClassMethodInfo with the class name and an empty methods dictionary.

        Args:
            class_name (str): The name of the class.
        """
        self.class_name: str = class_name
        self.methods: Dict[str, Tuple[int, int]] = {}

    def add_method(self, name: str, linenos: Tuple[int, int]) -> None:
        """
        Record a method with its start and end line numbers.

        Args:
            name (str): The name of the method.
            linenos (Tuple[int, int]): A tuple containing the start and end line numbers of the method.
        """
        self.methods[name] = linenos

    def __repr__(self) -> str:
        """
        Returns a string representation of the ClassMethodInfo instance.

        Returns:
            str: A string representation of the class and its methods.
        """
        return f"<ClassMethodInfo {self.class_name}: methods={list(self.methods.keys())}>"


def extract_class_methods(file_path: str) -> List[ClassMethodInfo]:
    """
    Extracts all classes and their methods from a Python file, including method start and end line numbers.

    Args:
        file_path (str): Path to the Python source file.

    Returns:
        List[ClassMethodInfo]: A list of ClassMethodInfo instances containing class and method data.
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
                    end = getattr(item, "end_lineno", None)
                    if end is None:
                        end = max(getattr(n, "lineno", start) for n in ast.walk(item))
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
    original: ClassMethodInfo, refactored: ClassMethodInfo
) -> Dict[str, List[str]]:
    """
    Compare two ClassMethodInfo objects and return which methods are missing in the refactored version and which are newly added.

    Args:
        original (ClassMethodInfo): The original class method info.
        refactored (ClassMethodInfo): The refactored class method info.

    Returns:
        Dict[str, List[str]]: A dictionary with keys 'missing' and 'added', each mapping to a sorted list of method names.
    """
    orig_set = set(original.methods.keys())
    ref_set = set(refactored.methods.keys())

    missing = sorted(orig_set - ref_set)
    added = sorted(ref_set - orig_set)

    return {"missing": missing, "added": added}
