import ast
from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel, Field


# -------------------- Pydantic Models --------------------

class StrictnessEntry(BaseModel):
    name: str
    file: str
    start: int
    end: int
    asserts: int
    mocks: int
    raises: int
    branches: int
    length: int
    strictness_score: float = Field(ge=0.0, le=1.0, description="Strictness score between 0 and 1.")


class StrictnessReport(BaseModel):
    tests: List[StrictnessEntry]
    imports: Dict[str, List[str]] = Field(default_factory=dict)  # filename -> list of imports

    def to_json(self, indent: int = 2) -> str:
        return self.json(indent=indent)

    def save(self, path: Path):
        path.write_text(self.to_json(), encoding="utf-8")
        print(f"✅ Strictness report saved to: {path}")


# -------------------- Analysis Logic --------------------

def parse_ast_tree(filepath: Path):
    """Parse a Python file into an AST tree."""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    return ast.parse(source), filepath.stem  # Also return normalized file stem


def extract_test_functions_from_tree(tree, file_stem: str) -> List[dict]:
    """Extract test functions and methods from an AST tree."""
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for method in node.body:
                if isinstance(method, ast.FunctionDef):
                    start = method.lineno
                    end = getattr(method, "end_lineno", start)
                    full_name = f"{node.name}.{method.name}"
                    functions.append({
                        "name": full_name,  # ✅ Preserve original name here
                        "start": start,
                        "end": end,
                        "path": file_stem
                    })
        elif isinstance(node, ast.FunctionDef) and node.name.startswith("test"):
            start = node.lineno
            end = getattr(node, "end_lineno", start)
            functions.append({
                "name": node.name,  # ✅ Preserve original name here
                "start": start,
                "end": end,
                "path": file_stem
            })
    return functions



def extract_imports_from_tree(tree) -> List[str]:
    """Extract imported modules (flat and from) from AST tree, including full dotted path for project code."""
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)  # Full name
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)  # Full dotted path
    return sorted(imports)


def normalize_test_name(name: str, remove_test_prefix: bool = False) -> str:
    """
    Normalize test function/method names to reduce duplication.

    Args:
        name: The original test name, e.g., "TestConfigLoader.test_get_effective_config".
        remove_test_prefix: If True, removes 'test_' prefix for looser matching.

    Returns:
        Normalized name as a lowercase string.
    """
    # Handle class.method or module.class.method
    base_name = name.split('.')[-1].lower()

    if remove_test_prefix:
        if base_name.startswith("test_"):
            base_name = base_name[5:]
        elif base_name.startswith("test"):
            base_name = base_name[4:]

    # Remove underscores and common suffixes
    base_name = base_name.replace("_", "")
    if base_name.endswith("test"):
        base_name = base_name[:-4]

    return base_name






def analyze_strictness(lines: List[str], func: dict) -> StrictnessEntry:
    """Analyze the strictness of a test function based on its content."""
    segment = lines[func["start"] - 1: func["end"]]
    joined = "\n".join(segment)

    asserts = sum(1 for line in segment if "assert" in line)
    mocks = joined.count("mock") + joined.count("MagicMock")
    raises = joined.count("pytest.raises") + joined.count("self.assertRaises")

    branches = sum(
        1 for line in segment
        if line.strip().startswith(("if ", "for ", "while "))
    )

    length = max(1, func["end"] - func["start"] + 1)
    strictness = round((asserts * 1.5 + raises + 0.3 * mocks + 0.5 * branches) / length, 2)
    strictness = min(strictness, 1.0)  # Ensure within [0, 1]

    return StrictnessEntry(
        name=func["name"],
        file=func["path"],
        start=func["start"],
        end=func["end"],
        asserts=asserts,
        mocks=mocks,
        raises=raises,
        branches=branches,
        length=length,
        strictness_score=strictness
    )


def scan_test_directory(tests_path: Path) -> StrictnessReport:
    """Scan a directory for test files, extract test functions, and compute strictness scores."""
    print("🔎 Scanning test files and analyzing strictness...")
    test_files = [tests_path] if tests_path.is_file() else list(tests_path.rglob("test_*.py"))

    results = []
    imports_map = {}

    for test_file in test_files:
        with open(test_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        tree, file_stem = parse_ast_tree(test_file)
        funcs = extract_test_functions_from_tree(tree, file_stem)
        imports = extract_imports_from_tree(tree)
        imports_map[file_stem] = imports

        for func in funcs:
            analysis = analyze_strictness(lines, func)
            results.append(analysis)

    return StrictnessReport(tests=results, imports=imports_map)



# -------------------- CLI Entry Point --------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Static analysis of test strictness using Pydantic.")
    parser.add_argument("--tests", required=True, help="Path to test suite directory or file.")
    parser.add_argument("--output", help="Path to save the strictness report (JSON).")
    args = parser.parse_args()

    tests_path = Path(args.tests)
    report = scan_test_directory(tests_path)

    if args.output:
        out_path = Path(args.output)
        report.save(out_path)
    else:
        print(report.to_json())
