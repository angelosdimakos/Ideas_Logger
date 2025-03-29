import ast
import os
from typing import List, Dict, Optional

class ClassMethodInfo:
    def __init__(self, class_name: str):
        self.class_name = class_name
        self.methods: Dict[str, Optional[int]] = {}  # method name -> line number

    def add_method(self, name: str, lineno: Optional[int]):
        self.methods[name] = lineno

    def __repr__(self):
        return f"{self.class_name}: {list(self.methods.keys())}"


def extract_class_methods(file_path: str) -> List[ClassMethodInfo]:
    """Parse a Python file and extract all class methods."""
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=file_path)

    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_info = ClassMethodInfo(node.name)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    class_info.add_method(item.name, item.lineno)
            classes.append(class_info)
    return classes


def compare_class_methods(original: ClassMethodInfo, refactored: ClassMethodInfo) -> Dict[str, List[str]]:
    """Compare methods between original and refactored class versions."""
    missing = [m for m in original.methods if m not in refactored.methods]
    added = [m for m in refactored.methods if m not in original.methods]
    return {"missing": missing, "added": added}


def analyze_project_structure(original_dir: str, refactored_dir: str) -> Dict[str, Dict[str, List[str]]]:
    """Compare original vs refactored project and detect method-level changes per class."""
    summary = {}
    for filename in os.listdir(original_dir):
        if not filename.endswith(".py") or filename.startswith("test"):
            continue

        orig_path = os.path.join(original_dir, filename)
        ref_path = os.path.join(refactored_dir, filename)

        if not os.path.exists(ref_path):
            continue

        orig_classes = {cls.class_name: cls for cls in extract_class_methods(orig_path)}
        ref_classes = {cls.class_name: cls for cls in extract_class_methods(ref_path)}

        for class_name, orig_info in orig_classes.items():
            ref_info = ref_classes.get(class_name)
            if not ref_info:
                summary[class_name] = {"missing": list(orig_info.methods.keys()), "added": []}
            else:
                summary[class_name] = compare_class_methods(orig_info, ref_info)

    return summary



def calculate_cyclomatic_complexity(node):
    complexity = 1
    complexity += _calculate_node_complexity(node)
    for child in ast.iter_child_nodes(node):
        complexity += calculate_cyclomatic_complexity(child)
    return complexity

def _calculate_node_complexity(node):
    complexity = 0
    if isinstance(node, (ast.If, ast.For, ast.While)):
        complexity += 1
        complexity += _calculate_node_complexity(node.test)
        complexity += sum(_calculate_node_complexity(child) for child in node.body)
        complexity += sum(_calculate_node_complexity(child) for child in node.orelse)
    elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
        complexity += len(node.body)
        complexity += sum(_calculate_node_complexity(child) for child in node.body)
    return complexity

def calculate_cyclomatic_complexity_for_module(module):
    try:
        with open(module, 'r') as f:
            tree = ast.parse(f.read())
        return calculate_cyclomatic_complexity(tree)
    except Exception as e:
        print(f"Error parsing module {module}: {str(e)}")
        return None