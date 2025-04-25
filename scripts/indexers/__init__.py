"""
The `indexers` module provides classes and utilities for building, managing, and searching vector indexes over log and summary data.

Core features include:
- Construction of FAISS indexes for both raw log entries and summarized corrections.
- Support for semantic search using SentenceTransformer embeddings.
- Management of index and metadata persistence for efficient retrieval.
- Utilities for rebuilding, updating, and searching indexes across different data granularities.

This module enables fast and flexible semantic search over structured and unstructured idea logs, supporting downstream applications such as idea retrieval, analytics, and intelligent querying.
"""
