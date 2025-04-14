import ast
from typing import Dict, Tuple

class MethodRangeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.ranges: Dict[str, Tuple[int, int]] = {}
        self.current_class = None

    def visit_ClassDef(self, node):
        prev_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = prev_class

    def visit_FunctionDef(self, node):
        start = node.lineno
        end = getattr(node, 'end_lineno', None)

        if end is None:
            end = self._find_end_lineno(node)

        full_name = f"{self.current_class}.{node.name}" if self.current_class else node.name
        self.ranges[full_name] = (start, end)

    def _find_end_lineno(self, node):
        last_node = node.body[-1]
        if isinstance(last_node, ast.stmt):
            return getattr(last_node, 'lineno', node.lineno)
        return node.lineno

def extract_method_line_ranges(file_path: str) -> Dict[str, Tuple[int, int]]:
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=file_path)

    visitor = MethodRangeVisitor()
    visitor.visit(tree)
    return visitor.ranges
