import unittest
import json
from pathlib import Path
from scripts.refactor.strictness_analyzer import (
    extract_test_functions,
    analyze_strictness,
    attach_coverage_from_merged_report,
    compute_strictness_score,
)

class TestCoverageMapper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Resolve the absolute paths reliably regardless of working directory
        base_dir = Path(__file__).parent.parent.parent
        merged_report_path = base_dir / "fixtures" / "merged_report.json"
        cls.test_file_path = base_dir / "unit" / "ai" / "test_ai_summarizer.py"

        if not merged_report_path.exists():
            raise FileNotFoundError(f"Merged report not found at: {merged_report_path.resolve()}")
        if not cls.test_file_path.exists():
            raise FileNotFoundError(f"Test file not found at: {cls.test_file_path.resolve()}")

        cls.merged_report = json.loads(merged_report_path.read_text(encoding="utf-8"))
        cls.test_lines = cls.test_file_path.read_text(encoding="utf-8").splitlines()

    def test_extract_test_functions(self):
        funcs = extract_test_functions(self.test_file_path)
        self.assertTrue(funcs, "No test functions extracted.")
        for func in funcs:
            self.assertIn("test", func["name"])
            self.assertTrue(func["start"] <= func["end"])

    def test_analyze_strictness_metrics(self):
        funcs = extract_test_functions(self.test_file_path)
        analyzed = [analyze_strictness(self.test_lines, f) for f in funcs]
        for result in analyzed:
            self.assertIn("asserts", result)
            self.assertIn("branches", result)
            self.assertGreaterEqual(result["length"], 1)

    def test_attach_coverage_data(self):
        funcs = extract_test_functions(self.test_file_path)
        analyzed = [analyze_strictness(self.test_lines, f) for f in funcs]
        attach_coverage_from_merged_report(analyzed, self.merged_report)
        for result in analyzed:
            self.assertIn("coverage_hits", result)
            self.assertIn("coverage_hit_ratio", result)
            self.assertIsInstance(result["covers_prod_methods"], list)

    def test_strictness_score_exact_calculation(self):
        results = [{
            "asserts": 5,  # Max capped at 5, so assertion_factor = 1.0
            "coverage_hit_ratio": 0.8,  # coverage_factor = 0.8
            "covers_prod_methods": [{"complexity": 4}]  # avg_complexity = 4, complexity_factor = 1 + (4/15) = 1.2667
        }]
        compute_strictness_score(results)

        expected_assertion_factor = 1.0
        expected_coverage_factor = 0.8
        expected_complexity_factor = 1 + (4 / 15)  # ≈ 1.2667
        expected_score = round(expected_assertion_factor * expected_coverage_factor * expected_complexity_factor, 3)  # ≈ 1.013

        result = results[0]
        self.assertAlmostEqual(result["strictness_score"], expected_score, places=3)
        self.assertEqual(result["strictness_grade"], "A")

    def test_full_pipeline_with_exact_values(self):
        funcs = extract_test_functions(self.test_file_path)
        analyzed = [analyze_strictness(self.test_lines, f) for f in funcs]
        attach_coverage_from_merged_report(analyzed, self.merged_report)
        compute_strictness_score(analyzed)

        for result in analyzed:
            print(f"Test: {result['name']}, Strictness: {result['strictness_score']}, Grade: {result['strictness_grade']}")
            self.assertTrue(0.0 <= result["strictness_score"] <= 1.5)
            self.assertIn(result["strictness_grade"], {"A", "B", "C", "D"})

    def test_irrelevant_test_case_mapping(self):
        # Introduce a dummy test case that should not map to AISummarizer
        irrelevant_test = {
            "name": "test_unrelated_feature",
            "file": "tests/unit/ci_analyzer/test_ci_severity.py",
            "start": 1,
            "end": 5,
            "asserts": 2,
            "mocks": 0,
            "raises": 0,
            "branches": 1,
            "length": 5,
        }
        analyzed = [irrelevant_test]
        attach_coverage_from_merged_report(analyzed, self.merged_report)
        compute_strictness_score(analyzed)

        result = analyzed[0]
        # Since this test should have no valid prod method coverage, coverage should be 0
        self.assertEqual(result["coverage_hit_ratio"], 0.0)
        self.assertEqual(result["coverage_hits"], 0)
        self.assertEqual(result["strictness_score"], 0.0)
        self.assertEqual(result["strictness_grade"], "D")
        self.assertFalse(result["covers_prod_methods"], "This irrelevant test should not cover any production methods.")

if __name__ == "__main__":
    unittest.main()
