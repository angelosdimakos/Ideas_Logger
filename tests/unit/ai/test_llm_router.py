"""
Test suite for llm_router.py module.

This test suite validates the functionality for retrieving prompt templates and applying personas to prompts.
"""

import pytest
from unittest.mock import patch, MagicMock

# Import the module to test
from scripts.ai.llm_router import get_prompt_template, apply_persona


class TestLLMRouter:
    """Tests for the llm_router module."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        config = MagicMock()
        config.prompts_by_subcategory = {
            "Code Review": "You are reviewing code. Be critical but fair.",
            "Module Functionality": "Analyze this module's functionality.",
            "Tooling & Automation": "Help with tooling and automation.",
            "_default": "Default prompt when category not found."
        }
        return config

    def test_get_prompt_template_known_subcategory(self, mock_config):
        """Test getting a prompt template for a known subcategory."""
        prompt = get_prompt_template("Code Review", mock_config)
        assert prompt == "You are reviewing code. Be critical but fair."

        prompt = get_prompt_template("Tooling & Automation", mock_config)
        assert prompt == "Help with tooling and automation."

    def test_get_prompt_template_unknown_subcategory(self, mock_config):
        """Test getting a prompt template for an unknown subcategory (should use default)."""
        prompt = get_prompt_template("Unknown Category", mock_config)
        assert prompt == "Default prompt when category not found."

    def test_get_prompt_template_without_config(self):
        """Test getting a prompt template without providing a config."""
        with patch('scripts.ai.llm_router.ConfigManager.load_config') as mock_load_config:
            # Create a mock config to be returned by load_config
            mock_config = MagicMock()
            mock_config.prompts_by_subcategory = {
                "_default": "Default from auto-loaded config."
            }
            mock_load_config.return_value = mock_config

            # Test that it loads the config when not provided
            prompt = get_prompt_template("Any Category")

            # Verify config was loaded
            mock_load_config.assert_called_once()

            # Verify default prompt was used
            assert prompt == "Default from auto-loaded config."

    def test_apply_persona_default(self):
        """Test applying the default persona to a prompt."""
        prompt = "Base prompt text."
        result = apply_persona(prompt, "default")
        assert result == "Base prompt text."  # No modification for default

    def test_apply_persona_reviewer(self):
        """Test applying the reviewer persona to a prompt."""
        prompt = "Base prompt text."
        result = apply_persona(prompt, "reviewer")
        assert result == "Base prompt text.\n\nRespond like a senior code reviewer. Be terse and blunt."

    def test_apply_persona_mentor(self):
        """Test applying the mentor persona to a prompt."""
        prompt = "Base prompt text."
        result = apply_persona(prompt, "mentor")
        assert result == "Base prompt text.\n\nRespond like a mentor. Provide suggestions with empathy and reasoning."

    def test_apply_persona_planner(self):
        """Test applying the planner persona to a prompt."""
        prompt = "Base prompt text."
        result = apply_persona(prompt, "planner")
        assert result == "Base prompt text.\n\nProvide next steps like a project planner."

    def test_apply_persona_unknown(self):
        """Test applying an unknown persona to a prompt."""
        prompt = "Base prompt text."
        result = apply_persona(prompt, "unknown_persona")
        assert result == "Base prompt text."  # Should not modify for unknown personas