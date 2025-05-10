"""
Tests for llm_optimization.py functions.

This module contains tests for the LLM optimization helper functions used to
process files and build prompts for refactoring suggestions.
"""
import os
import pytest
from unittest.mock import patch, MagicMock, call
import numpy as np
import sys
import importlib.util
from pathlib import Path
from scripts.config.config_manager import ConfigManager

# Adjust this path to match your project structure
# Assuming the script is in scripts/ai/llm_optimization.py
MODULE_PATH = Path(__file__).parents[3] / "scripts" / "ai" / "llm_optimization.py"

# Dynamically import the module
spec = importlib.util.spec_from_file_location("llm_optimization", MODULE_PATH)
llm_optimization = importlib.util.module_from_spec(spec)
spec.loader.exec_module(llm_optimization)

# Import functions from the module
summarize_file_data_for_llm = llm_optimization.summarize_file_data_for_llm
extract_top_issues = llm_optimization.extract_top_issues
build_refactor_prompt = llm_optimization.build_refactor_prompt
build_strategic_recommendations_prompt = llm_optimization.build_strategic_recommendations_prompt
compute_severity = llm_optimization.compute_severity

@pytest.fixture
def mock_config():
    mock = MagicMock()
    mock.persona = "concise"  # Or whatever persona you're testing
    mock.prompts_by_subcategory = {
        "Refactor Suggestions": "Use this refactor suggestion template.",
        "_default": "Default prompt template."
    }
    return mock


@pytest.fixture
def sample_report_data():
    return [
        ("test_module.py", 8.5, ["Error 1", "Error 2"], 3, 7.2, 85.0),
        ("another_module.py", 6.0, ["Error A"], 1, 5.5, 90.0)
    ]


class TestSummarizeFileData:
    """Tests for summarize_file_data_for_llm function."""

    def test_summarize_file_data_with_complete_data(self):
        """Test file data summarization with complete input data."""
        # Prepare test data
        file_data = {
            "coverage": {
                "complexity": {
                    "func1": {"complexity": 5, "coverage": 0.8},
                    "func2": {"complexity": 10, "coverage": 0.5}
                }
            },
            "linting": {
                "quality": {
                    "mypy": {"errors": ["Error 1", "Error 2", "Error 3"]}
                }
            },
            "docstrings": {
                "functions": [
                    {"name": "func1", "description": "A function description"},
                    {"name": "func2", "description": ""},
                    {"name": "func3", "description": "Another description"}
                ]
            }
        }
        file_path = "/path/to/test_file.py"

        # Run the function
        result = summarize_file_data_for_llm(file_data, file_path)

        # Verify results
        assert result["file"] == "test_file.py"
        assert result["full_path"] == file_path
        assert result["complexity"] == 7.5  # (5 + 10) / 2
        assert result["coverage"] == 65.0  # (0.8 + 0.5) / 2 * 100
        assert result["mypy_errors"] == 3
        assert result["docstring_ratio"] == "2/3"
        assert isinstance(result["top_issues"], list)
        assert len(result["top_issues"]) <= 3

    def test_summarize_empty_file_data(self):
        """Test file data summarization with empty data."""
        empty_data = {}
        file_path = "/path/to/empty.py"

        result = summarize_file_data_for_llm(empty_data, file_path)

        assert result["file"] == "empty.py"
        assert result["complexity"] == 0
        assert result["coverage"] == 0
        assert result["mypy_errors"] == 0
        assert result["docstring_ratio"] == "0/0"
        assert result["top_issues"] == []

    def test_summarize_partial_data(self):
        """Test file data summarization with partial data."""
        partial_data = {
            "coverage": {
                "complexity": {
                    "func1": {"complexity": 6, "coverage": 0.75}
                }
            },
            "docstrings": {
                "functions": [
                    {"name": "func1", "description": "A description"}
                ]
            }
        }
        file_path = "/path/to/partial.py"

        result = summarize_file_data_for_llm(partial_data, file_path)

        assert result["file"] == "partial.py"
        assert result["complexity"] == 6.0
        assert result["coverage"] == 75.0
        assert result["mypy_errors"] == 0
        assert result["docstring_ratio"] == "1/1"


class TestExtractTopIssues:
    """Tests for extract_top_issues function."""

    def test_extract_no_issues(self):
        """Test extracting issues from file with no issues."""
        empty_data = {}
        issues = extract_top_issues(empty_data)
        assert issues == []

    def test_extract_mypy_errors(self):
        """Test extracting MyPy errors."""
        data_with_mypy = {
            "linting": {
                "quality": {
                    "mypy": {"errors": ["Missing type annotation", "Incompatible type"]}
                }
            }
        }
        issues = extract_top_issues(data_with_mypy)
        assert len(issues) == 1
        assert "MyPy error:" in issues[0]

    def test_extract_high_complexity(self):
        """Test extracting high complexity functions."""
        data_with_complexity = {
            "coverage": {
                "complexity": {
                    "complex_func": {"complexity": 15, "coverage": 0.9},
                    "simple_func": {"complexity": 3, "coverage": 0.9}
                }
            }
        }
        issues = extract_top_issues(data_with_complexity)
        assert len(issues) == 1
        assert "High complexity:" in issues[0]
        assert "complex_func" in issues[0]

    def test_extract_low_coverage(self):
        """Test extracting low coverage functions."""
        data_with_low_coverage = {
            "coverage": {
                "complexity": {
                    "uncovered_func": {"complexity": 5, "coverage": 0.3},
                    "covered_func": {"complexity": 5, "coverage": 0.9}
                }
            }
        }
        issues = extract_top_issues(data_with_low_coverage)
        assert len(issues) == 1
        assert "Low coverage:" in issues[0]
        assert "uncovered_func" in issues[0]

    def test_extract_multiple_issues_with_limit(self):
        """Test extracting multiple issues with max_issues limit."""
        data_with_many_issues = {
            "linting": {
                "quality": {
                    "mypy": {"errors": ["Error 1", "Error 2"]}
                }
            },
            "coverage": {
                "complexity": {
                    "complex_func": {"complexity": 15, "coverage": 0.9},
                    "uncovered_func": {"complexity": 5, "coverage": 0.3}
                }
            }
        }

        # Limit to just 2
        issues = extract_top_issues(data_with_many_issues, max_issues=2)
        assert len(issues) == 2

        # Test with all issues
        issues = extract_top_issues(data_with_many_issues, max_issues=5)
        assert len(issues) == 3


class TestBuildRefactorPrompt:
    """Tests for build_refactor_prompt function."""

    def test_build_refactor_prompt_verbose(self, mock_config, sample_report_data):
        """Test refactor prompt generation with verbose output."""
        # Create mocks for the imported functions
        with patch.object(llm_optimization, 'get_prompt_template') as mock_get_template:
            with patch.object(llm_optimization, 'apply_persona') as mock_apply_persona:
                # Configure mocks
                mock_get_template.return_value = "Template content"
                mock_apply_persona.return_value = "Final Prompt Output"

                # Act
                result = build_refactor_prompt(
                    sample_report_data,
                    config=mock_config,
                    verbose=True
                )

                # Assert
                mock_get_template.assert_called_once_with("Refactor Suggestions", mock_config)
                mock_apply_persona.assert_called_once_with("Template content", "concise")
                assert "Files needing attention" in result

    def test_build_refactor_prompt_condensed(self, mock_config, sample_report_data):
        """Test refactor prompt generation with condensed output."""
        # Create mocks for the imported functions
        with patch.object(llm_optimization, 'get_prompt_template') as mock_get_template:
            with patch.object(llm_optimization, 'apply_persona') as mock_apply_persona:
                # Configure mocks
                mock_get_template.return_value = "Condensed Template"
                mock_apply_persona.return_value = "Final Condensed Output"

                # Act
                result = build_refactor_prompt(
                    sample_report_data,
                    config=mock_config,
                    verbose=False
                )

                # Assert
                mock_get_template.assert_called_once_with("Refactor Suggestions", mock_config)
                mock_apply_persona.assert_called_once_with("Condensed Template", "concise")
                assert "Files needing attention" in result

    def test_build_refactor_prompt_with_limit(self):
        """Test limiting the number of files in the refactor prompt."""
        # Setup mocks via patching
        with patch.object(llm_optimization, 'get_prompt_template') as mock_get_template:
            with patch.object(llm_optimization, 'apply_persona') as mock_apply_persona:
                # Configure mocks
                mock_get_template.return_value = "Template content"
                mock_apply_persona.return_value = "Persona applied template"

                # Create test data with more files than the limit
                offenders = [
                    (f"file{i}.py", i + 5.0, [f"Error {i}"], i, i/2 + 5, 80.0 - i*5)
                    for i in range(1, 40)  # 39 files
                ]
                config = MagicMock()
                config.persona = "concise"

                # Run function with limit=10
                result = build_refactor_prompt(offenders, config, limit=10)

                # Count occurrences of "file" to ensure we're only showing 10
                file_mentions = [line for line in result.split("\n") if "- file" in line]
                assert len(file_mentions) <= 10


class TestBuildStrategicRecommendationsPrompt:
    """Tests for build_strategic_recommendations_prompt function."""

    def test_build_strategic_recommendations(self):
        """Test building strategic recommendations prompt."""
        # Test data
        severity_data = [
            {"Full Path": "/path/to/severe1.py", "Severity Score": 20.5,
             "Mypy Errors": 10, "Avg Complexity": 15, "Avg Coverage %": 30},
            {"Full Path": "/path/to/severe2.py", "Severity Score": 18.2,
             "Mypy Errors": 5, "Avg Complexity": 12, "Avg Coverage %": 45},
            {"Full Path": "/path/to/severe3.py", "Severity Score": 15.7,
             "Mypy Errors": 3, "Avg Complexity": 8, "Avg Coverage %": 55},
            {"Full Path": "/path/to/severe4.py", "Severity Score": 12.3,
             "Mypy Errors": 2, "Avg Complexity": 6, "Avg Coverage %": 65},
            {"Full Path": "/path/to/severe5.py", "Severity Score": 10.1,
             "Mypy Errors": 1, "Avg Complexity": 5, "Avg Coverage %": 70},
            {"Full Path": "/path/to/ok.py", "Severity Score": 5.0,
             "Mypy Errors": 0, "Avg Complexity": 3, "Avg Coverage %": 90}
        ]

        summary_metrics = {
            "total_tests": 120,
            "avg_strictness": 0.75,
            "avg_severity": 8.5,
            "coverage": 68,
            "missing_docs": 15,
            "high_severity_tests": 25,
            "medium_severity_tests": 45,
            "low_severity_tests": 50
        }

        # Run function
        result = build_strategic_recommendations_prompt(severity_data, summary_metrics)

        # Verify result structure and content
        assert "provide 3-5 strategic recommendations" in result
        assert "Total Tests: 120" in result
        assert "Average Severity: 8.5" in result
        assert "Top 5 most severe issues:" in result
        assert "severe1.py (Score: 20.5)" in result
        assert "Files with type errors: " in result
        assert "Files with high complexity: " in result
        assert "Files with low coverage: " in result

    def test_build_strategic_recommendations_with_limit(self):
        """Test building strategic recommendations prompt with file limit."""
        # Create many files
        severity_data = [
            {"Full Path": f"/path/to/file{i}.py", "Severity Score": 20.0 - i,
             "Mypy Errors": 10 - i if i < 10 else 0,
             "Avg Complexity": 15 - i if i < 15 else 1,
             "Avg Coverage %": 30 + i*2}
            for i in range(40)  # 40 files
        ]

        summary_metrics = {
            "total_tests": 120,
            "avg_strictness": 0.75,
            "avg_severity": 8.5,
            "coverage": 68,
            "missing_docs": 15,
            "high_severity_tests": 25,
            "medium_severity_tests": 45,
            "low_severity_tests": 50
        }

        # Run function with limit=5
        result = build_strategic_recommendations_prompt(severity_data, summary_metrics, limit=5)

        # Verify only 5 files were considered in the groupings
        file_mentions = result.count("file0.py") + result.count("file1.py") + \
                       result.count("file2.py") + result.count("file3.py") + \
                       result.count("file4.py")
        assert file_mentions > 0
        assert "file39.py" not in result  # Last file should not be included


class TestComputeSeverity:
    """Tests for compute_severity function."""

    def test_compute_severity_with_complete_data(self):
        """Test severity computation with complete data."""
        # Test data
        file_path = "/path/to/complex_file.py"
        content = {
            "coverage": {
                "complexity": {
                    "func1": {"complexity": 8, "coverage": 0.6},
                    "func2": {"complexity": 12, "coverage": 0.4}
                }
            },
            "linting": {
                "quality": {
                    "mypy": {"errors": ["Error 1", "Error 2", "Error 3"]},
                    "pydocstyle": {"functions": {
                        "func1": ["Missing docstring"],
                        "func2": ["Missing return", "Missing param"]
                    }}
                }
            }
        }

        # Run function
        result = compute_severity(file_path, content)

        # Verify result
        assert result["File"] == "complex_file.py"
        assert result["Full Path"] == file_path
        assert result["Mypy Errors"] == 3
        assert result["Lint Issues"] == 3  # 1 + 2
        assert result["Avg Complexity"] == 10.0  # (8 + 12) / 2
        assert result["Avg Coverage %"] == 50.0  # (0.6 + 0.4) / 2 * 100

        # Verify severity score calculation
        expected_score = (
            2.0 * 3 +  # mypy errors
            1.5 * 3 +  # lint issues
            2.0 * 10.0 +  # complexity
            2.0 * (1.0 - 0.5)  # coverage
        )
        assert result["Severity Score"] == round(expected_score, 2)

    def test_compute_severity_with_empty_data(self):
        """Test severity computation with empty data."""
        file_path = "/path/to/empty_file.py"
        content = {}

        result = compute_severity(file_path, content)

        assert result["File"] == "empty_file.py"
        assert result["Mypy Errors"] == 0
        assert result["Lint Issues"] == 0
        assert result["Avg Complexity"] == 0
        assert result["Avg Coverage %"] == 100.0  # Default to 100% when no data
        assert result["Severity Score"] == 0.0

    def test_compute_severity_partial_data(self):
        """Test severity computation with partial data."""
        file_path = "/path/to/partial_file.py"
        content = {
            "coverage": {
                "complexity": {
                    "func1": {"complexity": 5, "coverage": 0.8}
                }
            },
            "linting": {
                "quality": {
                    "mypy": {"errors": []}
                }
            }
        }

        result = compute_severity(file_path, content)

        assert result["File"] == "partial_file.py"
        assert result["Mypy Errors"] == 0
        assert result["Lint Issues"] == 0
        assert result["Avg Complexity"] == 5.0
        assert result["Avg Coverage %"] == 80.0

        # Verify severity score with partial data
        expected_score = (
            2.0 * 0 +  # no mypy errors
            1.5 * 0 +  # no lint issues
            2.0 * 5.0 +  # complexity
            2.0 * (1.0 - 0.8)  # coverage
        )
        assert result["Severity Score"] == round(expected_score, 2)