"""
Test suite for module_docstring_summarizer.py.

This test suite validates the functionality for summarizing module docstrings.
"""

import pytest
import json
import tempfile
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the module to test
from scripts.ai.module_docstring_summarizer import summarize_module, run


class TestModuleDocstringSummarizer:
    """Tests for the module_docstring_summarizer module."""

    @pytest.fixture
    def sample_report(self):
        """Create a sample report for testing."""
        return {
            "app/models.py": {
                "docstrings": {
                    "functions": [
                        {"name": "User.__init__", "description": "Initialize the user object",
                         "args": "email, password", "returns": "None"},
                        {"name": "User.validate_password", "description": "Validate password against requirements",
                         "args": "password", "returns": "bool"},
                        {"name": "User.get_profile", "description": "", "args": "", "returns": ""}
                    ]
                }
            },
            "app/views.py": {
                "docstrings": {
                    "functions": [
                        {"name": "login_view", "description": "Handle user login", "args": "request",
                         "returns": "HttpResponse"},
                        {"name": "register_view", "description": "Handle user registration", "args": "", "returns": ""},
                    ]
                }
            },
            "app/utils.py": {
                "docstrings": {
                    "functions": []
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
    def mock_ai_summarizer(self):
        """Create a mock AI summarizer for testing."""
        summarizer = MagicMock()
        summarizer.summarize_entry.return_value = "This module handles user authentication and profile management."
        return summarizer

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        config = MagicMock()
        config.persona = "mentor"
        config.prompts_by_subcategory = {
            "Module Functionality": "Summarize the module's purpose based on these function descriptions:",
            "_default": "Default prompt."
        }
        return config

    def test_summarize_module_with_docstrings(self, mock_ai_summarizer, mock_config):
        """Test summarizing a module with valid docstrings."""
        file_path = "app/models.py"
        doc_entries = [
            {"name": "User.__init__", "description": "Initialize the user object", "args": "email, password",
             "returns": "None"},
            {"name": "User.validate_password", "description": "Validate password against requirements",
             "args": "password", "returns": "bool"},
        ]

        with patch('scripts.ai.module_docstring_summarizer.get_prompt_template',
                   return_value="Summarize this module:") as mock_get_template:
            with patch('scripts.ai.module_docstring_summarizer.apply_persona',
                       return_value="Personalized prompt") as mock_apply_persona:
                result = summarize_module(file_path, doc_entries, mock_ai_summarizer, mock_config)

                # Verify get_prompt_template and apply_persona were called
                mock_get_template.assert_called_once_with("Module Functionality", mock_config)

                # Check arguments passed to apply_persona
                prompt_arg = mock_apply_persona.call_args[0][0]
                assert "Summarize this module:" in prompt_arg
                assert "User.__init__" in prompt_arg
                assert "User.validate_password" in prompt_arg
                assert "Initialize the user object" in prompt_arg

                # Check that summarizer was called with the right arguments
                mock_ai_summarizer.summarize_entry.assert_called_once_with(
                    "Personalized prompt",
                    subcategory="Module Functionality"
                )

                # Check final result
                assert result == "This module handles user authentication and profile management."

    def test_summarize_module_empty_docstrings(self, mock_ai_summarizer, mock_config):
        """Test summarizing a module with no docstrings."""
        file_path = "app/empty.py"
        doc_entries = []

        result = summarize_module(file_path, doc_entries, mock_ai_summarizer, mock_config)

        # Should return a default message for empty docstrings
        assert result == "No docstrings found."

        # Summarizer should not be called
        mock_ai_summarizer.summarize_entry.assert_not_called()

    def test_summarize_module_missing_descriptions(self, mock_ai_summarizer, mock_config):
        """Test summarizing a module with docstrings that have missing descriptions."""
        file_path = "app/partial.py"
        doc_entries = [
            {"name": "function1", "description": "", "args": "arg1", "returns": "None"},
            {"name": "function2", "description": None, "args": "arg2", "returns": "bool"},
        ]

        result = summarize_module(file_path, doc_entries, mock_ai_summarizer, mock_config)

        # Should summarize based on available data
        assert result == "This module handles user authentication and profile management."

        # Function descriptions should be handled gracefully in the prompt
        call_args = mock_ai_summarizer.summarize_entry.call_args[0][0]
        assert "function1" in call_args
        assert "function2" in call_args
        # But the descriptions should be empty
        assert "`function1`: " in call_args
        assert "`function2`: " in call_args

    @patch('builtins.print')
    def test_main_function(self, mock_print, temp_report_file, sample_report):
        """Test the main function processing a report file."""
        with patch('scripts.ai.module_docstring_summarizer.ConfigManager.load_config') as mock_load_config:
            with patch('scripts.ai.module_docstring_summarizer.AISummarizer') as mock_summarizer_class:
                # Setup mocks
                mock_config = MagicMock()
                mock_summarizer = MagicMock()
                mock_summarizer.summarize_entry.return_value = "Module summary"

                mock_load_config.return_value = mock_config
                mock_summarizer_class.return_value = mock_summarizer

                # Call main with the temp file
                old_argv = sys.argv
                try:
                    sys.argv = ['module_docstring_summarizer.py', temp_report_file]
                    run(temp_report_file)
                finally:
                    sys.argv = old_argv

                # Check that config and summarizer were initialized
                mock_load_config.assert_called_once()
                mock_summarizer_class.assert_called_once()

                # Check that summarize_module was called for each file with docstrings
                assert mock_summarizer.summarize_entry.call_count == 2  # for models.py and views.py

                # Check printed output - match the actual format from the run function
                mock_print.assert_any_call("\napp/models.py\nModule summary")
                mock_print.assert_any_call("\napp/views.py\nModule summary")
                # app/utils.py has no functions, so it shouldn't be processed
                # app/utils.py has no functions, so it shouldn't be processed