"""
conftest.py

This module contains configuration and fixtures for pytest testing.

It includes:
- Helper functions for managing Tkinter in headless environments.
- Mocking utilities for various libraries and components used in tests.
- Fixtures for creating temporary directories, files, and configurations.
- Functions to ensure integrity and prevent unwanted writes during testing.

Usage:
- This module is automatically discovered by pytest and the defined fixtures will be available in tests.
- Customization of fixtures can be done through monkeypatching as needed.

Note: Ensure that all necessary dependencies are installed to use the mocking and fixture functionalities.
"""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import numpy as np
import pytest
import tkinter as _tk
from typing import Any
import sys
import os
from contextlib import contextmanager

# ── 1. force_headless_tk  ─────────────────────────────────────
def _force_headless_tk() -> bool:
    """
    Ensure Tk works in headless CI.
    • If $DISPLAY exists → no-op.
    • If not, try xvfb :0; if that fails, monkey-patch tk.Tk with MagicMock.
    Returns True if *real* GUI is available, False if mocked.
    """
    if sys.platform.startswith("linux") and "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"          # let xvfb-run claim :0
    try:
        _tk.Tk().destroy()
        return True                           # real GUI
    except Exception:
        _tk.Tk = MagicMock()
        return False                          # GUI mocked

GUI_AVAILABLE = _force_headless_tk()

# ── 2. Context helper for ad-hoc tests (optional use) ─────────
@contextmanager
def tk_safe():
    """
    Yields (root, gui_ok):
        root   -> a Tk() instance (real or mocked)
        gui_ok -> bool flag (True if real GUI)
    """
    root = _tk.Tk()
    try:
        yield root, GUI_AVAILABLE
    finally:
        try:
            root.destroy()
        except Exception:
            pass

# ── 3. Auto-fixture: flush Tk event-loop between tests ────────
@pytest.fixture(autouse=True)
def flush_tk_events():
    yield
    try:
        if _tk._default_root:
            _tk._default_root.update_idletasks()
    except Exception:
        pass

# ── 4. Auto-fixture: stub blocking dialogs / file pickers ─────
@pytest.fixture(autouse=True)
def patch_blocking_dialogs(monkeypatch):
    import tkinter.messagebox as mb
    import tkinter.filedialog as fd
    monkeypatch.setattr(mb, "showwarning", lambda *a, **k: None)
    monkeypatch.setattr(fd, "askopenfilename",
                        lambda *a, **k: "/tmp/dummy.txt")
    yield
# ──────────────────────────────────────────────────────────────

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

@pytest.fixture
def mock_raw_log_file(temp_dir: Path) -> Path:
    """
    Mocks a raw log file for testing.

    Args:
        temp_dir (Path): The temporary directory for the mock file.

    Returns:
        Path: The path to the mock raw log file.
    """
    path = temp_dir / "logs" / "zephyrus_log.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    content = {
        "2024-01-01": {
            "Test": {
                "Subtest": [
                    {"timestamp": "2024-01-01 10:00:00", "content": "Test entry A"},
                    {"timestamp": "2024-01-01 10:01:00", "content": "Test entry B"},
                ]
            }
        }
    }
    path.write_text(json.dumps(content), encoding="utf-8")
    return path

@pytest.fixture
def sample_lint_file(tmp_path: Path) -> str:
    """
    Provides a sample lint file for testing.

    Args:
        tmp_path (Path): The temporary path to create the sample file.

    Returns:
        str: The path to the sample lint file.
    """
    file = tmp_path / "flake8.txt"
    file.write_text("scripts/core/core.py:10:1: F401 unused import\nscripts/main.py:5:5: E225 missing whitespace")
    return str(file)

@pytest.fixture
def sample_refactor_file(tmp_path: Path) -> str:
    """
    Provides a sample refactor file for testing.

    Args:
        tmp_path (Path): The temporary path to create the sample file.

    Returns:
        str: The path to the sample refactor file.
    """
    file = tmp_path / "refactor_audit.json"
    data = {
        "scripts/core/core.py": {
            "complexity": {
                "func_a": {"score": 5},
                "func_b": {"score": 10}
            }
        },
        "scripts/gui/gui.py": {
            "complexity": {
                "gui_main": {"score": 7}
            }
        }
    }
    file.write_text(json.dumps(data), encoding="utf-8-sig")
    return str(file)

@pytest.fixture
def real_lint_artifact() -> str:
    """
    Provides a real lint artifact for testing.

    Returns:
        str: The real lint artifact.
    """
    return Path("tests/test_data/real_lint_output.txt").read_text()


@pytest.fixture
def mock_correction_summaries_file(temp_dir: Path) -> Path:
    """
    Mocks a correction summaries file for testing.

    Args:
        temp_dir (Path): The temporary directory for the mock file.

    Returns:
        Path: The path to the mock correction summaries file.
    """
    content = {
        "global": {
            "Test": {
                "Subtest": [
                    {"corrected_summary": "Test summary A"},
                    {"original_summary": "Test summary B"}
                ]
            }
        }
    }
    path = temp_dir / "logs" / "correction_summaries.json"
    path.write_text(json.dumps(content), encoding="utf-8")
    return path



# ===========================
# 📁 TEMP DIR + CONFIG FIXTURES
# ===========================
@pytest.fixture(scope="function")
def temp_dir(tmp_path: Path) -> Path:
    """
    Creates a temporary directory for testing.

    Args:
        tmp_path (Path): The temporary path to create the directory.

    Returns:
        Path: The path to the created temporary directory.
    """
    paths = [tmp_path / "logs", tmp_path / "exports", tmp_path / "vector_store"]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
    return tmp_path

@pytest.fixture
def temp_script_dir(temp_dir: Path) -> str:
    """
    Creates a temporary script directory for testing.

    Args:
        temp_dir (Path): The temporary directory for the script.

    Returns:
        str: The path to the created temporary script directory.
    """
    return str(temp_dir)  # Just returns the temp path as a string


@pytest.fixture
def temp_config_file(temp_dir: Path) -> Path:
    """
    Creates a temporary config file for testing.

    Args:
        temp_dir (Path): The temporary directory for the config file.

    Returns:
        Path: The path to the created temporary config file.
    """
    config = build_test_config(temp_dir)
    config_path = temp_dir / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return config_path


# ===========================
# 🦢 TEST CONFIG PATCHER
# ===========================
@pytest.fixture(scope="function", autouse=True)
def patch_config_and_paths(monkeypatch: Any, temp_dir: Path) -> None:
    """
    Patches the configuration and paths for testing.

    Args:
        monkeypatch (Any): The monkeypatch object to use for patching.
        temp_dir (Path): The temporary directory for the configuration.
    """
    config = build_test_config(temp_dir)
    monkeypatch.setattr("scripts.config.config_loader.load_config", lambda config_path=None: config)
    monkeypatch.setattr("scripts.config.config_loader.get_absolute_path", lambda rel: str(Path(rel).resolve()))


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


# ===========================
# 🧠 CORE LOGGER FIXTURE
# ===========================
@pytest.fixture
def logger_core(temp_dir: Path) -> Any:
    """
    Creates a logger core for testing.

    Args:
        temp_dir (Path): The temporary directory for the logger core.

    Returns:
        Any: The logger core.
    """
    from scripts.core.core import ZephyrusLoggerCore
    return ZephyrusLoggerCore(script_dir=temp_dir)  # ✅ correct usage




# ===========================
# 🔀 STATE CLEANUP FIXTURES
# ===========================
@pytest.fixture
def clean_summary_tracker(logger_core: Any) -> None:
    """
    Cleans the summary tracker for testing.

    Args:
        logger_core (Any): The logger core to clean.
    """
    logger_core.summary_tracker.tracker_file.write_text("{}", encoding="utf-8")
    yield


@pytest.fixture(autouse=True)
def reset_config_manager() -> None:
    """
    Resets the configuration manager for testing.
    """
    from scripts.config.config_manager import ConfigManager
    ConfigManager.reset()
    yield
    ConfigManager.reset()


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
    monkeypatch.setattr("scripts.indexers.base_indexer.SentenceTransformer", lambda *a, **kw: mock_model)


# ===========================
# 🧱 INDEXER AUTLOAD BLOCKERS
# ===========================



@pytest.fixture(autouse=True)
def stub_indexers(monkeypatch: Any, mock_raw_log_file: Any, mock_correction_summaries_file: Any, temp_dir: Path) -> None:
    """
    Stubs indexers for testing.

    Args:
        monkeypatch (Any): The monkeypatch object to use for patching.
        mock_raw_log_file (Any): The mocked raw log file.
        mock_correction_summaries_file (Any): The mocked correction summaries file.
        temp_dir (Path): The temporary directory for the indexers.
    """
    class DummyEmbeddingModel:
        def encode(self, texts, convert_to_numpy=True):
            return np.array([[0.1] * 384 for _ in texts])

    def mock_init_summary(self, *args, **kwargs):
        self.paths = kwargs.get("paths") if "paths" in kwargs else kwargs.get("index_root")
        self.index = None
        self.metadata = []
        self.embedding_model = DummyEmbeddingModel()
        self.summaries_path = mock_correction_summaries_file
        self.index_path = temp_dir / "vector_store" / "summary_index.faiss"
        self.metadata_path = temp_dir / "vector_store" / "summary_metadata.pkl"

    def mock_init_raw(self, *args, **kwargs):
        self.paths = kwargs.get("paths") if "paths" in kwargs else kwargs.get("index_root")
        self.index = None
        self.metadata = []
        self.embedding_model = DummyEmbeddingModel()
        self.log_path = mock_raw_log_file
        self.index_path = temp_dir / "vector_store" / "raw_index.faiss"
        self.metadata_path = temp_dir / "vector_store" / "raw_metadata.pkl"

    monkeypatch.setattr("scripts.indexers.summary_indexer.SummaryIndexer.__init__", mock_init_summary)
    monkeypatch.setattr("scripts.indexers.raw_log_indexer.RawLogIndexer.__init__", mock_init_raw)






# ===========================
# 🛡 CONFIG GENERATOR
# ===========================
def build_test_config(temp_dir: Path) -> dict:
    """
    Builds a test configuration.

    Args:
        temp_dir (Path): The temporary directory for the configuration.

    Returns:
        dict: The test configuration.
    """
    def safe_path(p):
        return str(temp_dir / p)

    return {
        "mode": "test",
        "use_gui": False,
        "interface_theme": "dark",
        "batch_size": 5,
        "autosave_interval": 10,
        "log_level": "DEBUG",
        "summarization": True,
        "llm_provider": "ollama",
        "llm_model": "mistral",
        "openai_model": "gpt-4",
        "api_keys": {"openai": "test-key"},
        "embedding_model": "all-MiniLM-L6-v2",
        "faiss_top_k": 5,
        "force_summary_tracker_rebuild": True,
        "log_format": "json",
        "markdown_export": True,
        "default_tags": ["test"],
        "use_templates": True,
        "persona": "test_persona",
        "category_structure": {
            "Test": ["Subtest"],
            "SequentialTest": ["Flow"],
            "FallbackTest": ["Flow"],
            "IntegrationTest": ["Workflow"],
            "FAISS": ["Check"]
        },
        "prompts_by_subcategory": {
            "Subtest": "Test prompt",
            "Flow": "Summarize the flow of events.",
            "Workflow": "Summarize the integration workflow.",
            "Check": "Summarize log behavior for index check."
        },
        "test_mode": True,
        "logs_dir": safe_path("logs"),
        "export_dir": safe_path("exports"),
        "vector_store_dir": safe_path("vector_store"),
        "correction_summaries_path": safe_path("logs/correction_summaries.json"),
        "raw_log_path": safe_path("logs/zephyrus_log.json"),
        "faiss_index_path": safe_path("vector_store/summary_index.faiss"),
        "faiss_metadata_path": safe_path("vector_store/summary_metadata.pkl"),
        "raw_log_index_path": safe_path("vector_store/raw_index.faiss"),
        "raw_log_metadata_path": safe_path("vector_store/raw_metadata.pkl"),
        "test_logs_dir": safe_path("logs"),
        "test_vector_store_dir": safe_path("vector_store"),
        "test_export_dir": safe_path("exports"),
        "test_correction_summaries_path": safe_path("logs/test_corrections.json"),
        "test_raw_log_path": safe_path("logs/test_raw_log.json"),
        "test_summary_tracker_path": safe_path("logs/test_summary_tracker.json"),
        "plugin_dir": safe_path("plugins"),
        "remote_sync": False,
        "enable_debug_logging": True,
        "strict_offline_mode": True,
    }


# ===========================
# 🐧 CONFTEXT CANARY
# ===========================
@pytest.fixture(autouse=True, scope="session")
def watch_conftest_integrity() -> None:
    """
    Watches the integrity of the conftest.py file.
    """
    original_path = Path(__file__)
    if not original_path.exists():
        raise RuntimeError("🔥 CRITICAL: conftest.py is missing before test session starts!")

    yield

    if not original_path.exists():
        raise RuntimeError("🛑 ALERT: conftest.py was deleted during test run!")


# ===========================
# 🫯 GUARDRAILS
# ===========================
@pytest.fixture(autouse=True)
def prevent_production_path_writes(monkeypatch: Any) -> None:
    """
    Prevents writes to production paths.

    Args:
        monkeypatch (Any): The monkeypatch object to use for patching.
    """
    original_open = open

    def guarded_open(file, mode='r', *args, **kwargs):
        file_path = str(file)
        if ("zephyrus_log.json" in file_path or "correction_summaries.json" in file_path) and "test" not in file_path:
            raise PermissionError(f"❌ Blocked access to production file during test: {file_path}")
        return original_open(file, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", guarded_open)


SAFE_DIRS = {".git", ".venv", ".pytest_cache", "htmlcov", "__pycache__", "site-packages", ".mypy_cache", ".vscode"}
SAFE_EXTS = {
    ".py", ".pyc", ".pyo", ".ini", ".toml", ".md", ".zip", ".exe", ".html",
    ".json", ".coverage", ".coveragerc", ".txt", ".spec", ".log"
}

@pytest.fixture(scope="session", autouse=True)
def assert_all_output_in_temp(tmp_path_factory: Any) -> None:
    """
    Asserts all output is in the temporary directory.

    Args:
        tmp_path_factory (Any): The temporary path factory.
    """
    tmp_root = tmp_path_factory.getbasetemp().resolve()
    root_dir = Path(".").resolve()

    # Take a snapshot of the files BEFORE test run
    before = {p.resolve() for p in root_dir.rglob("*") if p.is_file()}

    yield  # let the tests run

    # Take a snapshot AFTER test run
    after = {p.resolve() for p in root_dir.rglob("*") if p.is_file()}
    new_files = after - before

    for path in new_files:
        relative = path.relative_to(root_dir)

        # ✅ Skip safe locations
        if (
            any(part in SAFE_DIRS for part in relative.parts)
            or path.suffix in SAFE_EXTS
            or tmp_root in path.parents
            or str(relative).startswith("tests/mock_data/")
            or relative.name.startswith(".coverage.")  # ✅ Ignore xdist coverage fragments
        ):
            continue

        raise AssertionError(f"🚨 Test output leaked outside tmp dir: {relative}")


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
