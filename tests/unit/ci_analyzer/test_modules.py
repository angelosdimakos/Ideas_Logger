"""
Test suite for the code quality analysis modules.

This test suite contains unit tests for:
- visuals.py - Testing risk emojis and bar rendering
- severity_index.py - Testing severity score calculation
- metrics_summary.py - Testing metrics summary generation
- drilldown.py - Testing detailed report generation
- severity_audit.py - Testing audit report generation
"""

import unittest
import pandas as pd
from unittest.mock import patch, mock_open, MagicMock

# Import modules to test
from scripts.ci_analyzer.visuals import risk_emoji, render_bar
from scripts.ci_analyzer.severity_index import compute_severity, compute_severity_index
from scripts.ci_analyzer.metrics_summary import generate_metrics_summary
from scripts.ci_analyzer.drilldown import generate_top_offender_drilldowns
from scripts.ci_analyzer.severity_audit import format_priority, generate_header_block, generate_severity_table, main


class TestVisuals(unittest.TestCase):
    """Test the visual representation functions."""

    def test_risk_emoji(self):
        """Test that risk_emoji returns appropriate emojis for different scores."""
        self.assertEqual(risk_emoji(95), "🟢")  # High score should return green
        self.assertEqual(risk_emoji(85), "🟡")  # Medium score should return yellow
        self.assertEqual(risk_emoji(60), "🔴")  # Low score should return red

    def test_render_bar(self):
        """Test that render_bar returns correct visual representation."""
        # Test full bar
        self.assertEqual(render_bar(100), "▓" * 20)

        # Test empty bar
        self.assertEqual(render_bar(0), "░" * 20)

        # Test partial bar
        self.assertEqual(render_bar(50), "▓" * 10 + "░" * 10)

        # Test custom width
        self.assertEqual(render_bar(50, width=10), "▓" * 5 + "░" * 5)


class TestSeverityIndex(unittest.TestCase):
    """Test the severity index calculation functions."""

    def test_compute_severity_empty_file(self):
        """Test computing severity for an empty file."""
        result = compute_severity("empty.py", {})
        self.assertEqual(result["File"], "empty.py")
        self.assertEqual(result["Mypy Errors"], 0)
        self.assertEqual(result["Lint Issues"], 0)
        self.assertEqual(result["Avg Complexity"], 0)
        self.assertEqual(result["Avg Coverage %"], 100.0)
        self.assertEqual(result["Severity Score"], 0.0)

    def test_compute_severity_with_data(self):
        """Test computing severity with actual data."""
        mock_data = {
            "coverage": {
                "complexity": {
                    "func1": {"complexity": 5, "coverage": 0.75},
                    "func2": {"complexity": 10, "coverage": 0.5}
                }
            },
            "linting": {
                "quality": {
                    "mypy": {"errors": ["error1", "error2"]},
                    "pydocstyle": {"functions": {"func1": ["issue1"], "func2": ["issue1", "issue2"]}}
                }
            }
        }

        result = compute_severity("test.py", mock_data)
        self.assertEqual(result["File"], "test.py")
        self.assertEqual(result["Mypy Errors"], 2)
        self.assertEqual(result["Lint Issues"], 3)
        self.assertEqual(result["Avg Complexity"], 7.5)
        self.assertEqual(result["Avg Coverage %"], 62.5)

        # Score = 2.0*2 + 1.5*3 + 1.0*7.5 + 2.0*(1.0-0.625) = 4 + 4.5 + 7.5 + 0.75 = 16.75
        self.assertEqual(result["Severity Score"], 16.75)

    def test_compute_severity_index(self):
        """Test computing a severity index for multiple files."""
        mock_report_data = {
            "file1.py": {
                "coverage": {"complexity": {"func1": {"complexity": 3, "coverage": 1.0}}},
                "linting": {"quality": {"mypy": {"errors": []}, "pydocstyle": {"functions": {}}}}
            },
            "file2.py": {
                "coverage": {"complexity": {"func1": {"complexity": 10, "coverage": 0.5}}},
                "linting": {
                    "quality": {"mypy": {"errors": ["error1"]}, "pydocstyle": {"functions": {"func1": ["issue1"]}}}}
            }
        }

        df = compute_severity_index(mock_report_data)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)

        # file2.py should be first (higher severity)
        self.assertEqual(df.iloc[0]["File"], "file2.py")
        self.assertEqual(df.iloc[1]["File"], "file1.py")


class TestMetricsSummary(unittest.TestCase):
    """Test the metrics summary generation."""

    def test_generate_metrics_summary_empty(self):
        """Test generating a metrics summary with empty data."""
        summary = generate_metrics_summary({})
        self.assertIn("Total methods audited: **0**", summary)
        self.assertIn("🚫 Methods missing tests: **0**", summary)
        self.assertIn("🔺 High-complexity methods (≥10): **0**", summary)
        self.assertIn("📚 Methods missing docstrings: **0**", summary)
        self.assertIn("🧼 Linter issues detected: **0**", summary)

    def test_generate_metrics_summary_with_data(self):
        """Test generating a metrics summary with actual data."""
        mock_data = {
            "file1.py": {
                "coverage": {
                    "complexity": {
                        "func1": {"complexity": 15, "coverage": 0.0},
                        "func2": {"complexity": 5, "coverage": 1.0}
                    }
                },
                "docstrings": {
                    "functions": [
                        {"name": "func1", "description": "", "args": "Documented", "returns": "Documented"},
                        {"name": "func2", "description": "Documented", "args": "Documented", "returns": "Documented"}
                    ]
                },
                "linting": {
                    "quality": {
                        "mypy": {"errors": ["error1"]},
                        "pydocstyle": {"functions": {"func1": ["issue1", "issue2"]}}
                    }
                }
            }
        }

        summary = generate_metrics_summary(mock_data)
        self.assertIn("Total methods audited: **2**", summary)
        self.assertIn("🚫 Methods missing tests: **1**", summary)
        self.assertIn("🔺 High-complexity methods (≥10): **1**", summary)
        self.assertIn("📚 Methods missing docstrings: **1**", summary)
        self.assertIn("🧼 Linter issues detected: **3**", summary)


class TestDrilldown(unittest.TestCase):
    """Test the top offender drilldown generation."""

    def test_generate_top_offender_drilldowns(self):
        """Test generating drilldowns for top offenders."""
        mock_severity_df = pd.DataFrame([
            {"File": "file1.py", "Severity Score": 20},
            {"File": "file2.py", "Severity Score": 15},
            {"File": "file3.py", "Severity Score": 10},
        ])

        mock_report_data = {
            "file1.py": {
                "linting": {
                    "quality": {
                        "mypy": {"errors": ["error1"]},
                        "pydocstyle": {"functions": {
                            "func1": [{"code": "D400", "message": "First line should end with a period"}]}}
                    }
                },
                "coverage": {
                    "complexity": {
                        "func1": {"complexity": 8, "coverage": 0.4}
                    }
                },
                "docstrings": {
                    "functions": [
                        {"name": "func1", "description": "Test function", "args": "None", "returns": "None"}
                    ]
                }
            },
            "file2.py": {},
            "file3.py": {}
        }

        drilldown = generate_top_offender_drilldowns(mock_severity_df, mock_report_data, top_n=2)

        # Check for expected content
        self.assertIn("## 🔎 Top Offenders: Detailed Analysis", drilldown)
        self.assertIn("<summary>🔍 `file1.py`</summary>", drilldown)
        self.assertIn("<summary>🔍 `file2.py`</summary>", drilldown)
        self.assertNotIn("<summary>🔍 `file3.py`</summary>", drilldown)  # Should only include top 2

        # Check for specific details
        self.assertIn("**❗ MyPy Errors:**", drilldown)
        self.assertIn("- error1", drilldown)
        self.assertIn("**🧼 Pydocstyle Issues:**", drilldown)
        self.assertIn("- `func1`: D400 — First line should end with a period", drilldown)
        self.assertIn("**📉 Complexity & Coverage Issues:**", drilldown)
        self.assertIn("- `func1`: Complexity = 8, Coverage = 40.0%", drilldown)
        self.assertIn("**📚 Function Descriptions:**", drilldown)
        self.assertIn("- `func1`: Test function", drilldown)


class TestSeverityAudit(unittest.TestCase):
    """Test the severity audit report generation."""

    def test_format_priority(self):
        """Test priority level formatting based on severity score."""
        self.assertEqual(format_priority(35), "🔥 High")
        self.assertEqual(format_priority(25), "⚠️ Medium")
        self.assertEqual(format_priority(10), "✅ Low")

    def test_generate_header_block(self):
        """Test generating the header block for the audit report."""
        mock_severity_df = pd.DataFrame([
            {"File": "worst.py", "Mypy Errors": 3, "Lint Issues": 2},
            {"File": "ok.py", "Mypy Errors": 0, "Lint Issues": 0},
        ])

        mock_report_data = {
            "worst.py": {
                "coverage": {
                    "complexity": {
                        "func1": {"complexity": 10, "coverage": 0.5},
                        "func2": {"complexity": 5, "coverage": 0.0}
                    }
                },
                "docstrings": {
                    "functions": [
                        {"name": "func1", "description": "", "args": "", "returns": ""},
                        {"name": "func2", "description": "Test", "args": "Test", "returns": "Test"}
                    ]
                },
                "linting": {
                    "quality": {
                        "mypy": {"errors": ["error1", "error2", "error3"]},
                        "pydocstyle": {"functions": {"func1": [{"code": "D400", "message": "Test"}],
                                                     "func2": [{"code": "D400", "message": "Test"}]}}
                    }
                }
            },
            "ok.py": {}
        }

        header = generate_header_block(mock_severity_df, mock_report_data)

        # Check for expected content
        self.assertIn("# 📊 CI Code Quality Audit Report", header)
        self.assertIn("Files analyzed             | `2`", header)
        self.assertIn("Files with issues          | `1`", header)
        self.assertIn("**Top risk file**          | `worst.py`", header)
        self.assertIn("Methods audited            | `2`", header)
        self.assertIn("Missing tests              | `1`", header)
        self.assertIn("Missing docstrings         | `1`", header)
        self.assertIn("Linter issues              | `5`", header)  # 3 mypy + 2 pydocstyle

    def test_generate_severity_table(self):
        """Test generating the severity table for the audit report."""
        mock_severity_df = pd.DataFrame([
            {
                "File": "test.py",
                "Mypy Errors": 2,
                "Lint Issues": 3,
                "Avg Complexity": 8.5,
                "Avg Coverage %": 75.0,
                "Severity Score": 20.5
            }
        ])

        table = generate_severity_table(mock_severity_df)

        # Check for expected content
        self.assertIn("## 🧨 Severity Rankings (Top 10)", table)
        self.assertIn("| File | 🔣 Mypy | 🧼 Lint | 📉 Cx | 📊 Cov | 📈 Score | 🎯 Priority |", table)
        self.assertIn("| `test.py` | 2 | 3 | 8.5", table)
        self.assertIn("20.5 | ⚠️ Medium |", table)  # Medium priority for score 20.5

    @patch('scripts.ci_analyzer.severity_audit.argparse.ArgumentParser')
    @patch('scripts.ci_analyzer.severity_audit.compute_severity_index')
    @patch('scripts.ci_analyzer.severity_audit.generate_header_block')
    @patch('scripts.ci_analyzer.severity_audit.generate_severity_table')
    @patch('scripts.ci_analyzer.severity_audit.generate_metrics_summary')
    @patch('scripts.ci_analyzer.severity_audit.generate_top_offender_drilldowns')
    @patch('scripts.ci_analyzer.severity_audit.Path')
    @patch('builtins.open', new_callable=mock_open, read_data='{"test.py": {}}')
    @patch('builtins.print')
    def test_main(self, mock_print, mock_file_open, mock_path, mock_drilldown, mock_metrics,
                  mock_table, mock_header, mock_severity, mock_argparse):
        """Test the main function that generates the full report."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.audit = "test_report.json"
        mock_args.output = "test_output.md"
        mock_args.top = 3

        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_argparse.return_value = mock_parser

        mock_severity.return_value = pd.DataFrame([{"File": "test.py"}])
        mock_header.return_value = "# Header"
        mock_table.return_value = "## Table"
        mock_metrics.return_value = "## Metrics"
        mock_drilldown.return_value = "## Drilldown"

        # Execute
        main()

        # Verify
        mock_file_open.assert_called_once_with("test_report.json", "r", encoding="utf-8")
        mock_severity.assert_called_once()
        mock_header.assert_called_once()
        mock_table.assert_called_once()
        mock_metrics.assert_called_once()
        mock_drilldown.assert_called_once()

        # Check that write_text was called with the concatenated report
        mock_path.return_value.write_text.assert_called_once_with(
            "# Header\n\n## Table\n\n## Metrics\n\n## Drilldown",
            encoding="utf-8"
        )

        # Check that print was called
        mock_print.assert_called_once_with("✅ CI audit report written to: test_output.md")


if __name__ == '__main__':
    unittest.main()