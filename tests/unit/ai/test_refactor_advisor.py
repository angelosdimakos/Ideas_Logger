"""
Test suite for llm_refactor_advisor.py module.

This test suite validates the functionality for loading audit reports and building refactor prompts.
"""

import pytest
import json
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the module to test
from scripts.ai.llm_refactor_advisor import load_audit, extract_top_offenders, build_refactor_prompt


class TestLLMRefactorAdvisor:
    """Tests for the llm_refactor_advisor module."""

    @pytest.fixture
    def sample_audit_data(self):
        """Create sample audit data for testing."""
        return {
            "app/models.py": {
                "linting": {
                    "quality": {
                        "mypy": {"errors": ["Error 1", "Error 2"]},
                        "pydocstyle": {"functions": {"func1": ["Issue 1"], "func2": ["Issue 2", "Issue 3"]}}
                    }
                },
                "coverage": {
                    "complexity": {
                        "method1": {"complexity": 8, "coverage": 0.75},
                        "method2": {"complexity": 12, "coverage": 0.5}
                    }
                }
            },
            "app/views.py": {
                "linting": {
                    "quality": {
                        "mypy": {"errors": ["Error 3", "Error 4", "Error 5"]},
                        "pydocstyle": {"functions": {"view1": ["Issue 4"]}}
                    }
                },
                "coverage": {
                    "complexity": {
                        "view_method1": {"complexity": 15, "coverage": 0.3},
                        "view_method2": {"complexity": 6, "coverage": 0.9}
                    }
                }
            },
            "app/utils.py": {
                "linting": {
                    "quality": {
                        "mypy": {"errors": []},
                        "pydocstyle": {"functions": {}}
                    }
                },
                "coverage": {
                    "complexity": {
                        "util_method1": {"complexity": 3, "coverage": 1.0},
                        "util_method2": {"complexity": 4, "coverage": 0.95}
                    }
                }
            }
        }

    @pytest.fixture
    def temp_audit_file(self, sample_audit_data):
        """Create a temporary audit file for testing."""
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
            json.dump(sample_audit_data, f)
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        config = MagicMock()
        config.persona = "reviewer"
        config.prompts_by_subcategory = {
            "Refactor Advisor": "You are a refactor advisor. Help improve this code.",
            "Tooling & Automation": "You are a tooling expert. Analyze this data.",
            "_default": "Default prompt."
        }
        return config

    def test_load_audit(self, temp_audit_file, sample_audit_data):
        """Test loading an audit from a file."""
        loaded_audit = load_audit(temp_audit_file)
        assert loaded_audit == sample_audit_data

    def test_extract_top_offenders(self, sample_audit_data):
        """Test extracting top offenders based on metrics."""
        offenders = extract_top_offenders(sample_audit_data, top_n=2)

        # Should return 2 items since top_n=2
        assert len(offenders) == 2

        # First item should be the worst file (app/views.py has more mypy errors and worse coverage)
        assert offenders[0][0] == "app/views.py"
        assert offenders[1][0] == "app/models.py"

        # Verify each item has the right metrics
        for file_path, score, errors, lint_issues, cx, cov in offenders:
            assert isinstance(score, float)
            assert isinstance(errors, list)
            assert isinstance(lint_issues, int)
            assert isinstance(cx, float)
            assert isinstance(cov, float)

    def test_extract_top_offenders_empty_report(self):
        """Test extracting top offenders from an empty report."""
        empty_report = {}
        offenders = extract_top_offenders(empty_report, top_n=5)

        # Should return an empty list
        assert offenders == []

    def test_build_refactor_prompt(self, mock_config):
        """Test building a refactor prompt based on identified offenders."""
        offenders = [
            ("app/views.py", 25.5, ["Error 1", "Error 2", "Error 3"], 1, 10.5, 0.6),
            ("app/models.py", 18.2, ["Error 4", "Error 5"], 3, 9.0, 0.7)
        ]

        with patch('scripts.ai.llm_refactor_advisor.get_prompt_template',
                   return_value="You are a refactor advisor.") as mock_get_template:
            with patch('scripts.ai.llm_refactor_advisor.apply_persona', return_value="Personalized prompt") as mock_apply_persona:
                result = build_refactor_prompt(offenders, mock_config, "Refactor Advisor")

                # Verify get_prompt_template and apply_persona were called
                mock_get_template.assert_called_once_with("Refactor Advisor", mock_config)

                # Check content in prompt before mocking
                prompt_arg = mock_apply_persona.call_args[0][0]
                assert "You are a refactor advisor." in prompt_arg
                assert "app/views.py" in prompt_arg
                assert "app/models.py" in prompt_arg
                assert "Score=25.5" in prompt_arg
                assert "Score=18.2" in prompt_arg

                # Check final result
                assert result == "Personalized prompt"