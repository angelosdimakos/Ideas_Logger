import os
import ast
import fnmatch
import logging
from typing import Optional, Dict, Any, List

from scripts.refactor.ast_extractor import extract_class_methods, compare_class_methods
from scripts.refactor.complexity_analyzer import calculate_function_complexity_map
from scripts.refactor.coverage_parser import parse_coverage_xml_to_method_hits
from scripts.refactor.method_line_ranges import extract_method_line_ranges

logger = logging.getLogger(__name__)


class AnalysisError(Exception):
    """Raised when an error occurs during analysis."""

    pass


class RefactorGuard:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {
            "max_complexity": 10,
            "ignore_files": [],
            "ignore_dirs": [],
        }
        # initialize coverage_hits so we can always safely test it
        self.coverage_hits: Dict[str, Any] = {}

    def analyze_tests(
        self, refactored_path: str, test_file_path: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Parse the test file’s AST to find which methods are exercised.
        Returns a list of {"class": class_name, "method": method_name}
        for any public method that is NOT called in the tests.
        """
        # If no test file provided or it doesn’t exist,
        # treat it as “no tests” (so all methods will be flagged).
        if not test_file_path or not os.path.exists(test_file_path):
            tree = None
        else:
            try:
                with open(test_file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=test_file_path)
            except (SyntaxError, IOError) as e:
                logger.warning(f"Could not parse tests at {test_file_path}: {e}")
                tree = None

        called_methods = set()
        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    if isinstance(func, ast.Attribute):
                        called_methods.add(func.attr)
                    elif isinstance(func, ast.Name):
                        called_methods.add(func.id)

        missing = []
        for cls in extract_class_methods(refactored_path):
            for method in cls.methods:
                # If parse failed (tree is None), called_methods is empty → all methods missing
                if method not in called_methods:
                    missing.append({"class": cls.class_name, "method": method})

        return missing

    def analyze_module(
        self, original_path: str, refactored_path: str, test_file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare original vs refactored:
          - method_diff: added/missing methods
          - missing_tests: public methods lacking test calls
          - complexity: cyclomatic complexity + potential coverage hits
        """
        result: Dict[str, Any] = {
            "method_diff": {},
            "missing_tests": [],
            "complexity": {},
        }

        if not original_path.strip() or os.path.abspath(original_path) == os.path.abspath(
            refactored_path
        ):
            orig_infos = {}
        else:
            orig_infos = {c.class_name: c for c in extract_class_methods(original_path)}

        ref_infos = {c.class_name: c for c in extract_class_methods(refactored_path)}

        # removed or changed
        for name, orig in orig_infos.items():
            if name in ref_infos:
                result["method_diff"][name] = compare_class_methods(orig, ref_infos[name])
            else:
                result["method_diff"][name] = {"missing": list(orig.methods), "added": []}
        # newly added
        for name, refc in ref_infos.items():
            if name not in orig_infos:
                result["method_diff"][name] = {"missing": [], "added": list(refc.methods)}

        # 2) Missing tests
        result["missing_tests"] = self.analyze_tests(refactored_path, test_file_path)

        # 3) Complexity
        try:
            complexity_map = calculate_function_complexity_map(refactored_path)
        except Exception as e:
            raise AnalysisError(f"Failed complexity analysis: {e}")

        # 4) Coverage enrichment (optional)
        try:
            method_ranges = extract_method_line_ranges(refactored_path)
            coverage_data = parse_coverage_xml_to_method_hits(
                "coverage.xml", method_ranges, source_file_path=refactored_path
            )
            # stash for potential reuse
            self.attach_coverage_hits(coverage_data)
        except Exception as e:
            logger.warning(f"Failed to enrich with coverage: {e}")

        # 5) Build final complexity dict
        # 5) Build final complexity dict (use simple method names as keys)
        def _simple_name(qual: str) -> str:
            return qual.split(".")[-1]

        if self.coverage_hits:
            enriched: Dict[str, Any] = {}
            for qual, score in complexity_map.items():
                key = _simple_name(qual)
                info = self.coverage_hits.get(qual, {})
                if not info and "." in qual:
                    info = self.coverage_hits.get(key, {})
                enriched[key] = {
                    "complexity": score,
                    "coverage": info.get("coverage", "N/A"),
                    "hits": info.get("hits", "N/A"),
                    "lines": info.get("lines", "N/A"),
                }
            result["complexity"] = enriched
        else:
            result["complexity"] = {
                _simple_name(m): {
                    "complexity": sc,
                    "coverage": "N/A",
                    "hits": "N/A",
                    "lines": "N/A",
                }
                for m, sc in complexity_map.items()
            }

        return result

    def attach_coverage_hits(self, coverage_data: Dict[str, Any]) -> None:
        """Store coverage hits for later enrichment."""
        if coverage_data:
            self.coverage_hits = coverage_data

    def analyze_directory_recursive(
        self, original_dir: str, refactored_dir: str, test_dir: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Walk original_dir for .py files (respecting ignore_files/ignore_dirs),
        and run analyze_module on each pair under refactored_dir, optionally
        passing along per-file test paths from test_dir.
        """
        summary: Dict[str, Dict[str, Any]] = {}
        ignore_files = self.config.get("ignore_files", [])
        ignore_dirs = set(self.config.get("ignore_dirs", []))

        for root, dirs, files in os.walk(original_dir):
            # skip ignored directories
            rel_root = os.path.relpath(root, original_dir)
            for d in list(dirs):
                if d in ignore_dirs or fnmatch.fnmatch(os.path.join(rel_root, d), d):
                    dirs.remove(d)

            for fn in files:
                if not fn.endswith(".py"):
                    continue
                rel_path = os.path.relpath(os.path.join(root, fn), original_dir)
                if any(fnmatch.fnmatch(rel_path, pat) for pat in ignore_files):
                    continue

                orig = os.path.join(original_dir, rel_path)
                ref = os.path.join(refactored_dir, rel_path)
                if not os.path.exists(ref):
                    continue

                test_path = None
                if test_dir:
                    # 1) Try same relative path: tests/foo.py
                    candidate = os.path.join(test_dir, rel_path)
                    if os.path.exists(candidate):
                        test_path = candidate
                    else:
                        # 2) Try tests/test_<name>.py
                        base = os.path.basename(rel_path)  # "foo.py"
                        test_name = f"test_{base}"  # "test_foo.py"
                        candidate2 = os.path.join(test_dir, test_name)
                        if os.path.exists(candidate2):
                            test_path = candidate2

                summary[rel_path] = self.analyze_module(orig, ref, test_file_path=test_path)

        return summary
