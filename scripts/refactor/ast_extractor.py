# ast_extractor.py
import ast
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
