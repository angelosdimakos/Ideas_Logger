import os
from typing import Optional, Dict
import json
import re
import xml.etree.ElementTree as ET

from scripts.refactor.ast_extractor import extract_class_methods, compare_class_methods
from scripts.refactor.complexity_analyzer import calculate_function_complexity_map

class RefactorGuard:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            "max_complexity": 10,
            "ignore_files": [],
            "ignore_dirs": [],
        }
        # Store flattened coverage hits: {method_name: {coverage, hits, lines}}
        self.coverage_hits = {}

    def analyze_tests(self, refactored_path: str, test_file_path: Optional[str] = None) -> Dict:
        """
        Analyzes if tests exist for methods in the refactored code.
        """
        missing_tests = []

        # Only analyze if a test file is provided
        if test_file_path and os.path.exists(test_file_path):
            with open(test_file_path, 'r', encoding='utf-8') as f:
                test_code = f.read()

            # Extract the classes and methods from the refactored code
            classes = extract_class_methods(refactored_path)

            for cls in classes:
                for method in cls.methods:
                    pattern = r'\b' + re.escape(method) + r'\b'
                    if not re.search(pattern, test_code):
                        missing_tests.append({"class": cls.class_name, "method": method})

        return {"missing_tests": missing_tests}

    def analyze_module(self, original_path: str, refactored_path: str, test_file_path: Optional[str] = None) -> Dict:
        result = {"method_diff": {}, "complexity": {}, "missing_tests": []}

        if not original_path.strip():
            original_path = refactored_path

        # Extract methods from both original and refactored code
        original_classes = extract_class_methods(original_path)
        refactored_classes = extract_class_methods(refactored_path)
        orig_classes_dict = {cls.class_name: cls for cls in original_classes}
        ref_classes_dict = {cls.class_name: cls for cls in refactored_classes}

        # Detect method differences between original and refactored versions
        for cls_name, orig_info in orig_classes_dict.items():
            if cls_name in ref_classes_dict:
                diff = compare_class_methods(orig_info, ref_classes_dict[cls_name])
                result["method_diff"][cls_name] = diff
            else:
                result["method_diff"][cls_name] = {"missing": list(orig_info.methods.keys()), "added": []}

        for cls_name, ref_info in ref_classes_dict.items():
            if cls_name not in orig_classes_dict:
                result["method_diff"][cls_name] = {"missing": [], "added": list(ref_info.methods.keys())}

        # Check for missing tests using the provided test file path
        missing_tests_result = self.analyze_tests(refactored_path, test_file_path=test_file_path)
        result["missing_tests"] = missing_tests_result.get("missing_tests", [])

        # Detailed complexity per function/method
        complexity_map = calculate_function_complexity_map(refactored_path)

        # ⬇️ Enrich complexity map with coverage info if available
        if self.coverage_hits:
            enriched_map = {}
            for method, score in complexity_map.items():
                coverage_info = self.coverage_hits.get(method, {})
                # Fallback: if key not found and method contains a dot,
                # use the simple method name (portion after the dot)
                if not coverage_info and "." in method:
                    simple_method = method.split(".")[-1]
                    coverage_info = self.coverage_hits.get(simple_method, {})
                enriched_map[method] = {
                    "complexity": score,
                    "coverage": coverage_info.get("coverage", "N/A"),
                    "hits": coverage_info.get("hits", "N/A"),
                    "lines": coverage_info.get("lines", "N/A"),
                }
            result["complexity"] = enriched_map
        else:
            result["complexity"] = {
                method: {
                    "complexity": score,
                    "coverage": "N/A",
                    "hits": "N/A",
                    "lines": "N/A"
                } for method, score in complexity_map.items()
            }

        return result

    def attach_coverage_hits(self, coverage_data):
        """
        Injects coverage data (parsed from coverage.xml) into internal state.
        The coverage_data should be the dictionary returned from extract_coverage_hits.
        This method flattens the data to map method names to their coverage info.
        """
        if not coverage_data:
            return

        flat_coverage = {}
        # Flatten from {file_path: {method: {coverage, hits, lines}}} to {method: {coverage, hits, lines}}
        for file_path, methods in coverage_data.items():
            for method_name, data in methods.items():
                flat_coverage[method_name] = data
        self.coverage_hits = flat_coverage

# Function to parse the coverage data and return the hits
def parse_coverage_with_debug(possible_paths=None, verbose=True):
    if possible_paths is None:
        possible_paths = [
            "coverage.xml",
            "htmlcov/coverage.xml",
            "reports/coverage.xml",
            "scripts/coverage.xml"
        ]

    for path in possible_paths:
        if os.path.exists(path):
            if verbose:
                print(f"✅ Found coverage report at: {path}")
            try:
                tree = ET.parse(path)
                root = tree.getroot()
                return extract_coverage_hits(root, verbose=verbose)
            except ET.ParseError as e:
                if verbose:
                    print(f"❌ Failed to parse {path}: {e}")
                continue

    if verbose:
        print("⚠️ No valid coverage.xml found. Skipping coverage injection.")
    return {}

def extract_coverage_hits(root, verbose=False):
    result = {}

    for class_el in root.findall(".//class"):
        file_path = class_el.attrib.get("filename")
        if not file_path:
            continue
        methods = {}
        for method in class_el.findall("methods/method"):
            method_name = method.attrib.get("name")
            hits = 0
            total_lines = 0

            for line in method.findall("lines/line"):
                total_lines += 1
                if int(line.attrib.get("hits", 0)) > 0:
                    hits += 1

            if total_lines == 0:
                continue

            coverage = hits / total_lines
            methods[method_name] = {
                "coverage": coverage,
                "hits": hits,
                "lines": total_lines
            }

        if methods:
            result[file_path] = methods

    if verbose:
        print(f"📄 Parsed coverage for {len(result)} files.")
    return result
