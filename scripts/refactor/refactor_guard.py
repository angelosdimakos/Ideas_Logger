# refactor_guard.py
import os
from typing import Optional, Union, Dict
import json
import re
import os
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

        # ⬇️ Try to enrich complexity map with coverage info
        tree = parse_coverage_with_debug(verbose=False)
        if tree:
            coverage_data = extract_coverage_hits(tree)
            enriched_map = {}

            for method, score in complexity_map.items():
                coverage_info = coverage_data.get(method, {})

                # Fallback: match ".method" suffix if not found
                if not coverage_info:
                    for k in coverage_data:
                        if k.endswith(f".{method}"):
                            coverage_info = coverage_data[k]
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

    def analyze_directory(self, original_dir: str, refactored_dir: str) -> Dict[str, Dict]:
        summary = {}
        for filename in os.listdir(original_dir):
            if not filename.endswith(".py") or any(ignored in filename for ignored in self.config.get("ignore_files", [])):
                continue
            orig_path = os.path.join(original_dir, filename)
            ref_path = os.path.join(refactored_dir, filename)
            if not os.path.exists(ref_path):
                continue
            summary[filename] = self.analyze_module(orig_path, ref_path)
        return summary

    def analyze_tests(self, refactored_path: str, test_file_path: Optional[str] = None) -> Dict:
        missing_tests = []
        if test_file_path and os.path.exists(test_file_path):
            with open(test_file_path, 'r', encoding='utf-8') as f:
                test_code = f.read()
            classes = extract_class_methods(refactored_path)
            for cls in classes:
                for method in cls.methods:
                    pattern = r'\b' + re.escape(method) + r'\b'
                    if not re.search(pattern, test_code):
                        missing_tests.append({"class": cls.class_name, "method": method})
        return {"missing_tests": missing_tests}

    def analyze_refactor_changes(self, original_path: str, refactored_path: str, test_file_path: Optional[str] = None, as_string: bool = True) -> Union[str, Dict]:
        structured_result = {
            "summary": {},
            "missing_tests": [],
            "renamed_candidates": []
        }

        if os.path.isdir(original_path) and os.path.isdir(refactored_path):
            structured_result["summary"] = self.analyze_directory_recursive(original_path, refactored_path)
        else:
            structured_result["summary"] = self.analyze_module(original_path, refactored_path)

        test_results = self.analyze_tests(refactored_path, test_file_path)
        structured_result["missing_tests"] = test_results.get("missing_tests", [])

        for class_name, diff in structured_result["summary"].items():
            if isinstance(diff, dict) and "method_diff" in diff:
                method_diff = diff["method_diff"]
                for cls, changes in method_diff.items():
                    missing = changes.get("missing", [])
                    added = changes.get("added", [])
                    if len(missing) == 1 and len(added) == 1:
                        structured_result["renamed_candidates"].append({
                            "file": class_name,
                            "class": cls,
                            "from": missing[0],
                            "to": added[0]
                        })
            elif isinstance(diff, dict):
                missing = diff.get("missing", [])
                added = diff.get("added", [])
                if len(missing) == 1 and len(added) == 1:
                    structured_result["renamed_candidates"].append({
                        "file": original_path,
                        "class": class_name,
                        "from": missing[0],
                        "to": added[0]
                    })

        return json.dumps(structured_result, indent=2) if as_string else structured_result

    def analyze_directory_recursive(self, original_dir: str, refactored_dir: str) -> Dict[str, Dict]:
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
                return ET.parse(path)
            except ET.ParseError as e:
                if verbose:
                    print(f"❌ Failed to parse {path}: {e}")
                continue
        else:
            if verbose:
                print(f"🔍 Tried: {path} — Not found.")

        if verbose:
            print("⚠️ No valid coverage.xml found. Skipping coverage injection.")
        return None

def extract_coverage_hits(tree: ET.ElementTree) -> Dict[str, Dict]:
    """
    Parses a coverage.xml ElementTree and returns a mapping:
    { "filename.Class.method": {hits: int, lines: int, coverage: float}, ... }
    """
    coverage_data = {}
    root = tree.getroot()

    for class_tag in root.findall(".//class"):
        class_name = class_tag.attrib.get("name", "")
        filename = class_tag.attrib.get("filename", "").replace("\\", "/")

        for method_tag in class_tag.findall(".//method"):
            method_name = method_tag.attrib.get("name", "")
            full_name = f"{class_name}.{method_name}"

            lines = method_tag.findall("lines/line")
            total_lines = len(lines)
            hit_lines = sum(1 for l in lines if int(l.attrib.get("hits", "0")) > 0)

            if total_lines == 0:
                continue  # Skip empty methods

            coverage_data[full_name] = {
                "hits": hit_lines,
                "lines": total_lines,
                "coverage": round(hit_lines / total_lines, 2)
            }

    return coverage_data
