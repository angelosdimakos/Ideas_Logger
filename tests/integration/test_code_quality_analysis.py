"""
Integration test suite for code quality analysis modules.

This test suite validates that the entire pipeline works correctly with realistic data,
from severity calculation through to final report generation.
"""

import unittest
import os
import json
import tempfile
from pathlib import Path

# Import modules to test
from scripts.ci_analyzer.severity_index import compute_severity_index
from scripts.ci_analyzer.metrics_summary import generate_metrics_summary
from scripts.ci_analyzer.drilldown import generate_top_offender_drilldowns
from scripts.ci_analyzer.severity_audit import generate_header_block, generate_severity_table, main


class TestIntegration(unittest.TestCase):
    """Integration tests for the code quality analysis pipeline."""

    def setUp(self):
        """Set up test data and temporary files."""
        # Create a realistic sample report
        self.sample_report = {
            "app/models.py": {
                "coverage": {
                    "complexity": {
                        "User.__init__": {"complexity": 3, "coverage": 1.0},
                        "User.validate_password": {"complexity": 12, "coverage": 0.6},
                        "User.get_profile": {"complexity": 5, "coverage": 0.8}
                    }
                },
                "docstrings": {
                    "functions": [
                        {"name": "User.__init__", "description": "Initialize the user object",
                         "args": "email, password", "returns": "None"},
                        {"name": "User.validate_password", "description": "Validate password against requirements",
                         "args": "password", "returns": "bool"},
                        {"name": "User.get_profile", "description": "", "args": "", "returns": ""}
                    ]
                },
                "linting": {
                    "quality": {
                        "mypy": {"errors": [
                            "app/models.py:45: error: Argument 2 to \"validate_password\" has incompatible type \"None\"; expected \"str\""]},
                        "pydocstyle": {"functions": {"User.get_profile": [
                            {"code": "D401", "message": "First line should be in imperative mood"}]}}
                    }
                }
            },
            "app/views.py": {
                "coverage": {
                    "complexity": {
                        "login_view": {"complexity": 8, "coverage": 0.9},
                        "register_view": {"complexity": 15, "coverage": 0.5},
                        "profile_view": {"complexity": 6, "coverage": 0.0}
                    }
                },
                "docstrings": {
                    "functions": [
                        {"name": "login_view", "description": "Handle user login", "args": "request",
                         "returns": "HttpResponse"},
                        {"name": "register_view", "description": "Handle user registration", "args": "", "returns": ""},
                        {"name": "profile_view", "description": "Display user profile", "args": "request, user_id",
                         "returns": "HttpResponse"}
                    ]
                },
                "linting": {
                    "quality": {
                        "mypy": {"errors": [
                            "app/views.py:28: error: Incompatible return value type",
                            "app/views.py:42: error: Argument 1 to \"authenticate\" has incompatible type"
                        ]},
                        "pydocstyle": {"functions": {}}
                    }
                }
            },
            "app/utils.py": {
                "coverage": {
                    "complexity": {
                        "format_date": {"complexity": 2, "coverage": 1.0},
                        "calculate_stats": {"complexity": 7, "coverage": 0.7}
                    }
                },
                "docstrings": {
                    "functions": [
                        {"name": "format_date", "description": "Format a date to a string", "args": "date, format_str",
                         "returns": "str"},
                        {"name": "calculate_stats", "description": "Calculate user statistics", "args": "user_data",
                         "returns": "dict"}
                    ]
                },
                "linting": {
                    "quality": {
                        "mypy": {"errors": []},
                        "pydocstyle": {"functions": {}}
                    }
                }
            }
        }

        # Create a temporary directory and file for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.report_path = os.path.join(self.temp_dir.name, "test_report.json")
        self.output_path = os.path.join(self.temp_dir.name, "test_report.md")

        # Write the sample report to a file
        with open(self.report_path, "w", encoding="utf-8") as f:
            json.dump(self.sample_report, f)

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def test_full_pipeline(self):
        """Test the full report generation pipeline."""
        # Compute severity index
        severity_df = compute_severity_index(self.sample_report)

        # Verify severity index contains expected data
        self.assertEqual(len(severity_df), 3)  # Three files

        # The file with most issues should be app/views.py (2 mypy errors, high complexity, missing test)
        self.assertEqual(severity_df.iloc[0]["File"], "app/views.py")

        # Generate report components
        header = generate_header_block(severity_df, self.sample_report)
        table = generate_severity_table(severity_df)
        metrics = generate_metrics_summary(self.sample_report)
        drilldown = generate_top_offender_drilldowns(severity_df, self.sample_report, top_n=2)

        # Verify header content
        self.assertIn("# 📊 CI Code Quality Audit Report", header)
        self.assertIn("Files analyzed             | `3`", header)
        self.assertIn("**Top risk file**          | `app/views.py`", header)

        # Verify table content
        self.assertIn("## 🧨 Severity Rankings (Top 10)", table)
        self.assertIn("`app/views.py`", table)
        self.assertIn("`app/models.py`", table)

        # Verify metrics content
        self.assertIn("Total methods audited: **8**", metrics)
        self.assertIn("🚫 Methods missing tests: **1**", metrics)  # profile_view has 0 coverage
        self.assertIn("🔺 High-complexity methods (≥10): **2**", metrics)  # User.validate_password and register_view

        # Verify drilldown content
        self.assertIn("## 🔎 Top Offenders: Detailed Analysis", drilldown)
        self.assertIn("<summary>🔍 `app/views.py`</summary>", drilldown)
        self.assertIn("<summary>🔍 `app/models.py`</summary>", drilldown)
        self.assertNotIn("<summary>🔍 `app/utils.py`</summary>", drilldown)  # Should not be in top 2

        # Create final report
        final_report = f"{header}\n\n{table}\n\n{metrics}\n\n{drilldown}"
        Path(self.output_path).write_text(final_report, encoding="utf-8")

        # Verify the report file exists and has content
        self.assertTrue(os.path.exists(self.output_path))
        with open(self.output_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertGreater(len(content), 1000)  # Report should be substantial

    def test_main_function(self):
        """Test the main function with command line arguments."""
        import sys
        from io import StringIO

        # Capture stdout
        stdout_backup = sys.stdout
        sys.stdout = StringIO()

        try:
            # Call main with args
            sys.argv = [
                "severity_audit.py",
                "--audit", self.report_path,
                "--output", self.output_path,
                "--top", "2"
            ]
            main()

            # Check if the report was created
            self.assertTrue(os.path.exists(self.output_path))

            # Check stdout
            output = sys.stdout.getvalue()
            self.assertIn("✅ CI audit report written to:", output)

            # Check report content
            with open(self.output_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("# 📊 CI Code Quality Audit Report", content)
                self.assertIn("## 🔎 Top Offenders: Detailed Analysis", content)
                self.assertIn("`app/views.py`", content)
                self.assertIn("`app/models.py`", content)
        finally:
            # Restore stdout
            sys.stdout = stdout_backup


class TestEdgeCases(unittest.TestCase):
    """Tests for handling edge cases in the code quality analysis."""

    def test_empty_report(self):
        """Test handling an empty report with no files."""
        empty_report = {}

        # Should not raise exceptions
        severity_df = compute_severity_index(empty_report)
        self.assertEqual(len(severity_df), 0)

        metrics = generate_metrics_summary(empty_report)
        self.assertIn("Total methods audited: **0**", metrics)

        # With empty DataFrame, should still generate valid content
        header = generate_header_block(severity_df, empty_report)
        self.assertIn("Files analyzed             | `0`", header)

        table = generate_severity_table(severity_df)
        self.assertIn("## 🧨 Severity Rankings (Top 10)", table)

        drilldown = generate_top_offender_drilldowns(severity_df, empty_report)
        self.assertIn("## 🔎 Top Offenders: Detailed Analysis", drilldown)

    def test_missing_data_fields(self):
        """Test handling files with missing data fields."""
        incomplete_report = {
            "app/incomplete.py": {
                # Missing coverage data
                "docstrings": {
                    "functions": [
                        {"name": "test_func", "description": "Test function", "args": "None", "returns": "None"}
                    ]
                },
                # Missing linting data
            },
            "app/partial.py": {
                "coverage": {
                    # Empty complexity data
                    "complexity": {}
                },
                "linting": {
                    "quality": {
                        # Missing mypy data
                        "pydocstyle": {"functions": {}}
                    }
                }
                # Missing docstrings data
            }
        }

        # Should not raise exceptions
        severity_df = compute_severity_index(incomplete_report)
        self.assertEqual(len(severity_df), 2)

        # All scores should be 0 or close to 0
        for _, row in severity_df.iterrows():
            self.assertLessEqual(row["Severity Score"], 0.01)

        metrics = generate_metrics_summary(incomplete_report)
        self.assertIn("Total methods audited: **0**", metrics)

        drilldown = generate_top_offender_drilldowns(severity_df, incomplete_report)
        self.assertIn("<summary>🔍 `app/incomplete.py`</summary>", drilldown)
        self.assertIn("<summary>🔍 `app/partial.py`</summary>", drilldown)


if __name__ == '__main__':
    unittest.main()