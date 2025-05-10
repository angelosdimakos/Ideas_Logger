import unittest
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import patch, mock_open
import textwrap
import json

from scripts.refactor.strictness_analyzer import (
    extract_test_functions,
    analyze_strictness,
    compute_strictness_score,
    attach_coverage_hits,
    map_test_to_prod_path,
    scan_test_directory,
    main,
)


class TestStrictnessAnalyzer(unittest.TestCase):

    def test_extract_test_functions(self):
        src = textwrap.dedent("""
            def test_one():
                pass

            def helper():
                pass

            def test_two():
                pass
        """)
        with patch("builtins.open", mock_open(read_data=src)):
            funcs = extract_test_functions(Path("dummy.py"))
        names = [f["name"] for f in funcs]
        self.assertEqual(names, ["test_one", "test_two"])
        # line numbers should reflect the dedented source
        self.assertEqual(funcs[0]["start"], 2)
        self.assertEqual(funcs[0]["end"], 3)
        self.assertEqual(funcs[1]["start"], 8)
        self.assertEqual(funcs[1]["end"], 9)

    def test_analyze_strictness(self):
        lines = [
            "def test_x():",             #1
            "    assert a",              #2
            "    if cond:",              #3
            "        pass",              #4
            "    mock_obj.foo()",        #5
            "    with pytest.raises(Exception):",  #6
            "        pass",              #7
            "    for i in []:",          #8
            "        pass",              #9
        ]
        func = {"name": "test_x", "start": 1, "end": 9, "path": "f.py"}
        r = analyze_strictness(lines, func)
        self.assertEqual(r["asserts"], 1)
        self.assertEqual(r["branches"], 2)   # one 'if', one 'for'
        self.assertEqual(r["mocks"], 1)
        self.assertEqual(r["raises"], 1)
        self.assertEqual(r["length"], 9)
        self.assertEqual(r["file"], "f.py")

    def test_compute_strictness_score(self):
        results = [{
            "asserts": 5,  # Max influence after normalization
            "coverage_hit_ratio": 0.8,
            "covers_prod_methods": [{"complexity": 4}]  # Moderate complexity
        }]
        scored_results = compute_strictness_score(results)

        # Compute expected score manually
        # assertion_factor = 1.0 (capped at 5 asserts)
        # coverage_factor = 0.8
        # complexity_factor = 1 + (4 / 15) = 1.2667 -> capped to 1.2667
        # strictness_score = 1.0 * 0.8 * 1.2667 = ~1.013 (rounded to 1.013)

        self.assertAlmostEqual(scored_results[0]["strictness_score"], 1.013, places=3)
        self.assertEqual(scored_results[0]["strictness_grade"], "A")

    def test_attach_coverage_hits(self):
        results = [{
            "name": "t1", "file": "a.py", "start": 1, "end": 3, "length": 3,
            "asserts": 1, "raises": 0, "mocks": 0, "branches": 0
        }]
        key = Path("a.py").resolve().as_posix()
        coverage_data = {key: {
            "t1": {
                "hits": 2,
                "lines": 3,
                "coverage": 0.666,
                "covered_lines": [1, 2],
                "missing_lines": [3]
            }
        }}

        attach_coverage_hits(results, coverage_data)

        self.assertAlmostEqual(results[0]["coverage_hit_ratio"], 0.666, places=2)
        self.assertEqual(results[0]["covers_prod_methods"][0]["hits"], 2)
        self.assertEqual(results[0]["covers_prod_methods"][0]["lines"], 3)

    def test_map_test_to_prod_path_basic(self):
        test_root = Path("tests")
        src_root = Path("src")
        with patch("pathlib.Path.exists", return_value=True):
            p = map_test_to_prod_path(Path("tests/test_mod.py"), test_root, src_root)
            self.assertEqual(p, Path("src/mod.py"))

    def test_map_test_to_prod_path_rglob(self):
        test_root = Path("tests")
        src_root = Path("src")
        with patch("pathlib.Path.exists", return_value=False), \
             patch("pathlib.Path.rglob", return_value=[Path("src/foo/bar.py")]):
            p = map_test_to_prod_path(Path("tests/any/test_bar.py"), test_root, src_root)
            self.assertEqual(p, Path("src/foo/bar.py"))

    def test_scan_test_directory(self):
        # Simulated in-memory file system with 3 test files, including the missing fixture
        fs = {
            "tests/test_a.py": "def test_func1(): pass",
            "tests/sub/test_b.py": "def test_func2(): pass",
            "tests/fixtures/test_data_fixtures.py": "def test_fixture(): pass",  # Added missing fixture file
        }

        def mo(fp, *a, **k):
            normalized_fp = str(fp).replace("\\", "/")
            data = fs.get(normalized_fp)
            if data is None:
                raise KeyError(f"File not found in mock FS: {normalized_fp}")
            return mock_open(read_data=data)(fp, *a, **k)

        with patch("builtins.open", side_effect=mo), \
                patch("pathlib.Path.rglob", return_value=[Path(p) for p in fs.keys()]), \
                patch("scripts.refactor.strictness_analyzer.extract_test_functions") as mock_extract, \
                patch("scripts.refactor.strictness_analyzer.analyze_strictness") as mock_analyze:
            # Provide one response per discovered file
            mock_extract.side_effect = [
                [{"name": "test_func1", "start": 1, "end": 2, "path": "tests/test_a.py"}],
                [{"name": "test_func2", "start": 1, "end": 2, "path": "tests/sub/test_b.py"}],
                [{"name": "test_fixture", "start": 1, "end": 2, "path": "tests/fixtures/test_data_fixtures.py"}],
            ]
            mock_analyze.side_effect = [
                {"name": "test_func1", "file": "tests/test_a.py", "start": 1, "end": 2, "asserts": 0, "raises": 0,
                 "mocks": 0, "branches": 0, "length": 1},
                {"name": "test_func2", "file": "tests/sub/test_b.py", "start": 1, "end": 2, "asserts": 0, "raises": 0,
                 "mocks": 0, "branches": 0, "length": 1},
                {"name": "test_fixture", "file": "tests/fixtures/test_data_fixtures.py", "start": 1, "end": 2,
                 "asserts": 0, "raises": 0, "mocks": 0, "branches": 0, "length": 1},
            ]

            out = scan_test_directory(Path("tests"))

            # Validate outputs
            self.assertEqual(len(out), 3)
            self.assertEqual(out[0]["name"], "test_func1")
            self.assertEqual(out[1]["name"], "test_func2")
            self.assertEqual(out[2]["name"], "test_fixture")

            # Validate mocks were called exactly as expected
            self.assertEqual(mock_extract.call_count, 3)
            self.assertEqual(mock_analyze.call_count, 3)

    def test_main_smoke(self):
        # just verify it calls write_text once, no crash
        with patch("scripts.refactor.strictness_analyzer.scan_test_directory", return_value=[]), \
             patch("scripts.refactor.strictness_analyzer.parse_json_coverage", return_value={}), \
             patch("scripts.refactor.strictness_analyzer.attach_coverage_hits"), \
             patch("scripts.refactor.strictness_analyzer.map_tests_to_prod_code"), \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.write_text") as wt:
            main("tests","src","cov.json","out.json")
            wt.assert_called_once()


if __name__ == "__main__":
    unittest.main()
