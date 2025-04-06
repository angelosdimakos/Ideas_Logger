# complexity_analyzer.py
import ast

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.function_scores = {}  # {"ClassName.method": complexity}
        self.current_class = None

    def visit_ClassDef(self, node):
        previous_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = previous_class

    def visit_FunctionDef(self, node):
        complexity = self._calculate_complexity(node)
        name = node.name
        full_name = f"{self.current_class}.{name}" if self.current_class else name
        self.function_scores[full_name] = complexity
        self.generic_visit(node)

    def _calculate_complexity(self, node):
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.BoolOp, ast.ExceptHandler)):  # common decision points
                complexity += 1
        return complexity

def calculate_function_complexity_map(file_path: str) -> dict:
    """Returns a dict of function names to complexity scores."""
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()

    tree = ast.parse(source)
    visitor = ComplexityVisitor()
    visitor.visit(tree)
    return visitor.function_scores

def calculate_module_complexity(module_path: str) -> int:
    """
    Calculates the total cyclomatic complexity for a module.
    Adds a base score of 1 to the sum of all function/method complexities.
    """
    try:
        scores = calculate_function_complexity_map(module_path)
        return sum(scores.values()) + 1  # +1 module overhead
    except Exception as e:
        print(f"Error parsing module {module_path}: {str(e)}")
        return -1

def calculate_cyclomatic_complexity_for_module(module_path: str) -> int:
    """Wrapper to calculate total cyclomatic complexity for the module."""
    return calculate_module_complexity(module_path)