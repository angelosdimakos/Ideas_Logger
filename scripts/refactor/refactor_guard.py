import os
from typing import Optional, Dict
import json
import re

from scripts.refactor.ast_extractor import extract_class_methods, compare_class_methods
from scripts.refactor.complexity_analyzer import calculate_function_complexity_map
from scripts.refactor.coverage_parser import parse_coverage_xml_to_method_hits
from scripts.refactor.method_line_ranges import extract_method_line_ranges


class RefactorGuard:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            "max_complexity": 10,
            "ignore_files": [],
            "ignore_dirs": [],
        }
        self.coverage_hits = {}

    def analyze_tests(self, refactored_path: str, test_file_path: Optional[str] = None) -> Dict:
        missing_tests = []
        if test_file_path and os.path.exists(test_file_path):
            with open(test_file_path, "r", encoding="utf-8") as f:
                test_code = f.read()
            classes = extract_class_methods(refactored_path)
            for cls in classes:
                for method in cls.methods:
                    pattern = r"\b" + re.escape(method) + r"\b"
                    if not re.search(pattern, test_code):
                        missing_tests.append({"class": cls.class_name, "method": method})
        return {"missing_tests": missing_tests}

    def analyze_module(
        self, original_path: str, refactored_path: str, test_file_path: Optional[str] = None
    ) -> Dict:
        result = {"method_diff": {}, "complexity": {}, "missing_tests": []}

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
                result["method_diff"][cls_name] = {
                    "missing": list(orig_info.methods.keys()),
                    "added": [],
                }

        for cls_name, ref_info in ref_classes_dict.items():
            if cls_name not in orig_classes_dict:
                result["method_diff"][cls_name] = {
                    "missing": [],
                    "added": list(ref_info.methods.keys()),
                }

        result["missing_tests"] = self.analyze_tests(
            refactored_path, test_file_path=test_file_path
        ).get("missing_tests", [])
        complexity_map = calculate_function_complexity_map(refactored_path)

        # 🔗 Auto-load coverage if available
        try:
            method_ranges = extract_method_line_ranges(refactored_path)
            coverage_hits = parse_coverage_xml_to_method_hits("coverage.xml", method_ranges)
            self.attach_coverage_hits(coverage_hits)
        except Exception as e:
            print(f"⚠️ Failed to enrich with coverage: {e}")

        if self.coverage_hits:
            enriched_map = {}
            for method, score in complexity_map.items():
                coverage_info = self.coverage_hits.get(method, {})
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
                method: {"complexity": score, "coverage": "N/A", "hits": "N/A", "lines": "N/A"}
                for method, score in complexity_map.items()
            }

        return result

    def attach_coverage_hits(self, coverage_data):
        if not coverage_data:
            return
        self.coverage_hits = coverage_data

    def analyze_directory_recursive(
        self, original_dir: str, refactored_dir: str
    ) -> Dict[str, Dict]:
        summary = {}
        for root, _, files in os.walk(original_dir):
            for filename in files:
                if not filename.endswith(".py"):
                    continue
                rel_path = os.path.relpath(os.path.join(root, filename), original_dir)
                orig_path = os.path.join(original_dir, rel_path)
                ref_path = os.path.join(refactored_dir, rel_path)
                if not os.path.exists(ref_path):
                    continue
                summary[rel_path] = self.analyze_module(orig_path, ref_path)
        return summary
