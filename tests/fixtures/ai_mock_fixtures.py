"""
AI and External Service Mocking Fixtures

This module provides fixtures for mocking AI components and external services
used in the application during testing.
"""
import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from typing import Any
import types
import sys
import importlib


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
def mock_sentence_transformer():
    """
    Provide a fully-mocked SentenceTransformer for *all* tests:

    • Registers a fake ``sentence_transformers`` package in ``sys.modules``
    • Exposes the same mock on ``scripts.indexers.base_indexer`` so that
      helpers can patch it with ``patch("scripts.indexers.base_indexer.SentenceTransformer")``.
    """
    # ---- build the fake model ----
    mock_model = MagicMock()
    mock_model.encode.side_effect = lambda texts, **kw: np.array([[0.1] * 384 for _ in texts])

    # ---- create fake external package ----
    fake_pkg = types.ModuleType("sentence_transformers")
    fake_pkg.SentenceTransformer = lambda *a, **kw: mock_model

    # Make *every* import of sentence_transformers resolve to our fake module
    sys.modules["sentence_transformers"] = fake_pkg

    # Also expose the attribute on BaseIndexer early, so tests that patch it can find it
    base_indexer = importlib.import_module("scripts.indexers.base_indexer")
    base_indexer.SentenceTransformer = fake_pkg.SentenceTransformer

    yield

    # ---- optional cleanup (rarely necessary in autouse fixture) ----
    # sys.modules.pop("sentence_transformers", None)

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