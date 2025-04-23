"""
The `ai` module provides AI-powered summarization utilities for text entries using large language models (LLMs).

Core features include:
- Generating concise summaries for individual or multiple text entries.
- Supporting subcategory-specific prompts for context-aware summarization.
- Configurable model selection and prompt templates, loaded at initialization.
- Fallback to the Ollama chat API for summarization if the primary LLM fails.
- Designed for seamless integration into workflows requiring automated, high-quality text summarization.

This module enables flexible and robust summarization capabilities for downstream applications such as log analysis, reporting, and intelligent querying.
"""
