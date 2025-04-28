"""
AI and External Service Mocking Fixtures

This module provides fixtures for mocking AI components and external services
used in the application during testing.
"""
import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from typing import Any


# ===========================
# 🔪 OLLAMA AI MOCKING
# ===========================
@pytest.fixture(autouse=True)
def mock_ollama() -> None:
    """
    Mocks the ollama library functions for testing.
    """
    with patch("ollama.generate") as mock_generate, patch("ollama.chat") as mock_chat:
        mock_generate.return_value = {"response": "Mock summary"}
        mock_chat.return_value = {"message": {"content": "Mock fallback summary"}}
        yield mock_generate, mock_chat


# ===========================
# 🧬 MOCK TRANSFORMERS
# ===========================
@pytest.fixture(autouse=True)
def mock_sentence_transformer(monkeypatch: Any) -> None:
    """
    Mocks the sentence transformer for testing.

    Args:
        monkeypatch (Any): The monkeypatch object to use for patching.
    """
    mock_model = MagicMock()
    mock_model.encode.side_effect = lambda texts, **kwargs: np.array([[0.1] * 384 for _ in texts])
    monkeypatch.setattr(
        "scripts.indexers.base_indexer.SentenceTransformer", lambda *a, **kw: mock_model
    )


# ===========================
# 🔒 MOCKED AI SUMMARIZER
# ===========================
@pytest.fixture(scope="function", autouse=True)
def patch_aisummarizer(monkeypatch: Any) -> None:
    """
    Patches the AI summarizer for testing.

    Args:
        monkeypatch (Any): The monkeypatch object to use for patching.
    """
    mock_ai = MagicMock()
    mock_ai.summarize_entries_bulk.return_value = "Mocked summary"
    mock_ai._fallback_summary.return_value = "Fallback summary used."
    monkeypatch.setattr("scripts.ai.ai_summarizer.AISummarizer", lambda: mock_ai)


@pytest.fixture
def mock_failed_summarizer() -> Any:
    """
    Mocks a failed summarizer.

    Returns:
        Any: The mocked failed summarizer.
    """

    class FailingSummarizer:
        def summarize_entries_bulk(self, entries, subcategory):
            raise Exception("Simulated failure")

    return FailingSummarizer()