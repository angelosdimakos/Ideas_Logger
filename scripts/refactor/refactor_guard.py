import os
from typing import Optional, Union, Dict
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
        self.coverage_hits = {}  # Store coverage hits in this attribute

    def analyze_module(self, original_path: str, refactored_path: str) -> Dict:
        result = {"method_diff": {}, "complexity": {}}

        if not original_path.strip():
            original_path = refactored_path

        original_classes = extract_class_methods(original_path)
        refactored_classes = extract_class_methods(refactored_path)
        orig_classes_dict = {cls.class_name: cls for cls in original_classes}
        ref_classes_dict = {cls.class_name: cls for cls in refactored_classes}

        for cls_name, orig_info in orig_classes_dict.items():
            if cls_name in ref_classes_dict:
                diff = compare_class_methods(orig_info, ref_classes_dict[cls_name])
                result["method_diff"][cls_name] = diff
            else:
                result["method_diff"][cls_name] = {"missing": list(orig_info.methods.keys()), "added": []}

        for cls_name, ref_info in ref_classes_dict.items():
            if cls_name not in orig_classes_dict:
                result["method_diff"][cls_name] = {"missing": [], "added": list(ref_info.methods.keys())}

        # Detailed complexity per function/method
        complexity_map = calculate_function_complexity_map(refactored_path)

        # ⬇️ Enrich complexity map with coverage info if available
        if self.coverage_hits:
            enriched_map = {}

            for method, score in complexity_map.items():
                coverage_info = self.coverage_hits.get(method, {})

                # Fallback: match ".method" suffix if not found
                if not coverage_info:
                    for k in self.coverage_hits:
                        if k.endswith(f".{method}"):
                            coverage_info = self.coverage_hits[k]
                            break

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

    def attach_coverage_hits(self, coverage_tree):
        """
        Injects coverage data (parsed from coverage.xml) into internal state
        so methods can be enriched with coverage info.
        """
        if coverage_tree is None:
            return

        self.coverage_hits = {}

        for class_ in coverage_tree.findall(".//class"):
            filename = class_.get("filename")
            for line in class_.findall("lines/line"):
                number = int(line.get("number"))
                hits = int(line.get("hits"))
                key = f"{filename}:{number}"
                self.coverage_hits[key] = hits

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

            coverage = hits / total_lines if total_lines else 0.0
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
