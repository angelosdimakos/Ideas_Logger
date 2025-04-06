# complexity_analyzer.py
import ast

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.decision_points = 0

    def visit_If(self, node):
        self.decision_points += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.decision_points += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.decision_points += 1
        self.generic_visit(node)

    def visit_Try(self, node):
        # Count each except clause as a decision point.
        self.decision_points += len(node.handlers)
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        # For boolean operations, count each additional operand beyond the first.
        self.decision_points += len(node.values) - 1
        self.generic_visit(node)

def calculate_function_complexity(function_node: ast.FunctionDef) -> int:
    """Calculates the cyclomatic complexity for a single function."""
    visitor = ComplexityVisitor()
    visitor.visit(function_node)
    # Complexity is baseline 1 plus decision points.
    return 1 + visitor.decision_points

def calculate_module_complexity(module_path: str) -> int:
    """
    Calculates the cyclomatic complexity for a module.
    For each top-level function, complexity = 1 + decision points.
    Then adds a module overhead of 1.
    """
    with open(module_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=module_path)
    total = 0
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            total += calculate_function_complexity(node)
    # Add 1 for module overhead.
    return total + 1

def calculate_cyclomatic_complexity_for_module(module_path: str) -> int:
    """Wrapper to calculate cyclomatic complexity for the module."""
    try:
        return calculate_module_complexity(module_path)
    except Exception as e:
        print(f"Error parsing module {module_path}: {str(e)}")
        return -1
