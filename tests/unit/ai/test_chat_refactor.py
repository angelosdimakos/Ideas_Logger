"""
Test suite for chat_refactor.py module.

This test suite validates that the chat refactor functionality works correctly,
focusing on loading reports and building contextual prompts.
"""

import pytest
import json
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the module to test
from scripts.ai.chat_refactor import load_report, build_contextual_prompt


class TestChatRefactor:
    """Tests for the chat_refactor module."""

    @pytest.fixture
    def sample_report(self):
        """Create a sample report for testing."""
        return {
            "app/models.py": {
                "severity_score": 25.5,
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
                "severity_score": 35.2,
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
            }
        }

    @pytest.fixture
    def temp_report_file(self, sample_report):
        """Create a temporary report file for testing."""
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
            json.dump(sample_report, f)
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        config = MagicMock()
        config.persona = "default"
        return config

    def test_load_report(self, temp_report_file, sample_report):
        """Test loading a report from a file."""
        loaded_report = load_report(temp_report_file)
        assert loaded_report == sample_report

    def test_build_contextual_prompt(self, sample_report, mock_config):
        """Test building a contextual prompt with the report data."""
        query = "What's the worst file?"

        with patch('scripts.ai.chat_refactor.apply_persona', return_value="Personalized prompt") as mock_apply_persona:
            result = build_contextual_prompt(query, sample_report, mock_config)

            # Verify apply_persona was called with the right arguments
            mock_apply_persona.assert_called_once()

            # Check for specific content in the prompt (before mocking)
            prompt_arg = mock_apply_persona.call_args[0][0]
            assert "You are an AI assistant helping engineers" in prompt_arg
            assert "app/views.py" in prompt_arg  # should be first (highest severity)
            assert "app/models.py" in prompt_arg
            assert f"Q: {query}" in prompt_arg

            # Check final result
            assert result == "Personalized prompt"

    def test_build_contextual_prompt_empty_report(self, mock_config):
        """Test building a contextual prompt with an empty report."""
        query = "What's the worst file?"
        empty_report = {}

        result = build_contextual_prompt(query, empty_report, mock_config)

        # Even with empty report, should return a valid prompt
        assert query in result
        assert "Here is a summary of the most risky files:" in result
        # The summary should be empty, but the prompt structure is still valid

    def test_build_contextual_prompt_incomplete_data(self, mock_config):
        """Test building a contextual prompt with incomplete data in the report."""
        query = "What's the worst file?"
        incomplete_report = {
            "app/incomplete.py": {
                "severity_score": 15.0
                # Missing linting and coverage data
            }
        }

        result = build_contextual_prompt(query, incomplete_report, mock_config)

        # Should handle missing data gracefully
        assert query in result
        assert "app/incomplete.py" in result
        # Should not raise exceptions when accessing missing fields