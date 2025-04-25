# 📄 Docstring Coverage Report


## `__init__.py`
- 📦 Module docstring: ❌

## `conftest.py`
- 📦 Module docstring: ❌

### Functions:
- `_force_headless_tk`: ✅ → `Ensure Tk works in headless CI.
• If $DISPLAY exists → no-op.
• If not, try xvfb...`
- `tk_safe`: ✅ → `Yields (root, gui_ok):
    root   -> a Tk() instance (real or mocked)
    gui_ok...`
- `flush_tk_events`: ❌
- `patch_blocking_dialogs`: ❌
- `mock_ollama`: ✅ → `Mocks the ollama library functions for testing....`
- `mock_raw_log_file`: ✅ → `Mocks a raw log file for testing.

Args:
    temp_dir (Path): The temporary dire...`
- `sample_lint_file`: ✅ → `Provides a sample lint file for testing.

Args:
    tmp_path (Path): The tempora...`
- `sample_refactor_file`: ✅ → `Provides a sample refactor file for testing.

Args:
    tmp_path (Path): The tem...`
- `real_lint_artifact`: ✅ → `Provides a real lint artifact for testing.

Returns:
    str: The real lint arti...`
- `mock_correction_summaries_file`: ✅ → `Mocks a correction summaries file for testing.

Args:
    temp_dir (Path): The t...`
- `temp_dir`: ✅ → `Creates a temporary directory for testing.

Args:
    tmp_path (Path): The tempo...`
- `temp_script_dir`: ✅ → `Creates a temporary script directory for testing.

Args:
    temp_dir (Path): Th...`
- `temp_config_file`: ✅ → `Creates a temporary config file for testing.

Args:
    temp_dir (Path): The tem...`
- `patch_config_and_paths`: ✅ → `Patches the configuration and paths for testing.

Args:
    monkeypatch (Any): T...`
- `patch_aisummarizer`: ✅ → `Patches the AI summarizer for testing.

Args:
    monkeypatch (Any): The monkeyp...`
- `logger_core`: ✅ → `Creates a logger core for testing.

Args:
    temp_dir (Path): The temporary dir...`
- `clean_summary_tracker`: ✅ → `Cleans the summary tracker for testing.

Args:
    logger_core (Any): The logger...`
- `reset_config_manager`: ✅ → `Resets the configuration manager for testing....`
- `mock_sentence_transformer`: ✅ → `Mocks the sentence transformer for testing.

Args:
    monkeypatch (Any): The mo...`
- `stub_indexers`: ✅ → `Stubs indexers for testing.

Args:
    monkeypatch (Any): The monkeypatch object...`
- `build_test_config`: ✅ → `Builds a test configuration.

Args:
    temp_dir (Path): The temporary directory...`
- `watch_conftest_integrity`: ✅ → `Watches the integrity of the conftest.py file....`
- `prevent_production_path_writes`: ✅ → `Prevents writes to production paths.

Args:
    monkeypatch (Any): The monkeypat...`
- `assert_all_output_in_temp`: ✅ → `Asserts all output is in the temporary directory.

Args:
    tmp_path_factory (A...`
- `mock_failed_summarizer`: ✅ → `Mocks a failed summarizer.

Returns:
    Any: The mocked failed summarizer....`

## `scripts\__init__.py`
- 📦 Module docstring: ❌

## `scripts\ai\__init__.py`
- 📦 Module docstring: ✅

## `scripts\ai\ai_summarizer.py`
- 📦 Module docstring: ✅

### Classes:
- `AISummarizer`: ✅ → `AISummarizer provides methods to generate summaries for single or multiple text ...`

## `scripts\ci_analyzer\__init__.py`
- 📦 Module docstring: ❌

## `scripts\ci_analyzer\ci_trends.py`
- 📦 Module docstring: ✅

### Functions:
- `load_audit`: ✅ → `Loads and returns audit data from a JSON file.

Args:
    path (str): Path to th...`
- `extract_metrics`: ✅ → `Extracts summary metrics from an audit dictionary, including total files, method...`
- `compare_metrics`: ✅ → `Calculate the difference between corresponding metrics in two dictionaries.

Arg...`
- `save_metrics`: ✅ → `Save the provided metrics dictionary as a JSON file to the specified output path...`
- `load_previous_metrics`: ✅ → `Loads previous metrics from a JSON file at the specified path.

Args:
    path (...`
- `print_comparison`: ✅ → `Displays a comparison of CI metrics, indicating the change for each metric with ...`
- `main`: ✅ → `Parses command-line arguments to load audit data, extract and compare CI metrics...`

## `scripts\ci_analyzer\cli.py`
- 📦 Module docstring: ✅

## `scripts\ci_analyzer\insights\__init__.py`
- 📦 Module docstring: ❌

## `scripts\ci_analyzer\insights\descriptive_insights.py`
- 📦 Module docstring: ✅

### Functions:
- `generate_complexity_insights`: ✅ → `Generate a summary of code complexity insights from an audit report.

Analyzes m...`
- `generate_testing_insights`: ✅ → `Generate a list of formatted testing insights based on audit metadata.

Analyzes...`
- `generate_quality_insights`: ✅ → `Generate a summary of code quality insights from an audit report.

Analyzes lint...`
- `generate_diff_insights`: ✅ → `Generate a summary of code quality insights from an audit report.

Analyzes lint...`

## `scripts\ci_analyzer\insights\overview.py`
- 📦 Module docstring: ✅

### Functions:
- `generate_overview_insights`: ✅ → `Generate a summary of audit insights, including test coverage, code complexity, ...`

## `scripts\ci_analyzer\insights\prime_suspects.py`
- 📦 Module docstring: ✅

### Functions:
- `generate_prime_insights`: ✅ → `Analyzes audit data to extract and summarize the most frequent Flake8, Pydocstyl...`

## `scripts\ci_analyzer\orchestrator.py`
- 📦 Module docstring: ✅

### Functions:
- `backup_audit_file`: ✅ → `Creates a timestamped backup of the specified audit file in the 'audit_backups' ...`
- `load_audit`: ✅ → `Loads audit data from a JSON file after creating a timestamped backup.

Args:
  ...`
- `header_block`: ✅ → `Returns a formatted Markdown header block for the CI audit summary,
including me...`
- `generate_ci_summary`: ✅ → `Generate a comprehensive CI audit summary report as a Markdown-formatted string....`
- `save_summary`: ✅ → `Saves the provided markdown string to a file at the specified path.

Args:
    m...`
- `main`: ✅ → `Parses command-line arguments to load audit data, generate a CI summary report, ...`

## `scripts\ci_analyzer\utils\__ini__.py`
- 📦 Module docstring: ❌

## `scripts\ci_analyzer\utils\visuals.py`
- 📦 Module docstring: ✅

### Functions:
- `render_bar`: ✅ → `Render a visual bar for scores between 0–100.
E.g. 🟩🟩🟩🟨⬜⬜⬜⬜⬜⬜...`
- `risk_emoji`: ✅ → `Return a risk emoji based on score....`

## `scripts\config\__init__.py`
- 📦 Module docstring: ✅

## `scripts\config\config_loader.py`
- 📦 Module docstring: ✅

### Functions:
- `setup_logging`: ✅ → `Configures centralized logging with a default INFO level and a standard log form...`
- `load_config`: ✅ → `Safely load the config file from the config folder.
If it doesn't exist or has e...`
- `get_config_value`: ✅ → `Retrieve a configuration value by key.

Args:
    config (dict): The configurati...`
- `get_absolute_path`: ✅ → `Build an absolute path from a project-root-relative path.

Args:
    relative_pa...`
- `is_test_mode`: ✅ → `Check if 'test_mode' is enabled in the configuration.

This function verifies wh...`
- `get_effective_config`: ✅ → `Loads the configuration from the specified path and overrides paths with test-sa...`

## `scripts\config\config_manager.py`
- 📦 Module docstring: ✅

### Classes:
- `AppConfig`: ✅ → `Configuration model for application settings.

Defines all configurable paramete...`
- `ConfigManager`: ✅ → `Manages application configuration loading, caching, and validation.

Provides me...`

## `scripts\config\constants.py`
- 📦 Module docstring: ✅

## `scripts\config\logging_setup.py`
- 📦 Module docstring: ✅

### Functions:
- `setup_logging`: ✅ → `Sets up application-wide logging configuration.

Initializes the root logger wit...`

## `scripts\core\__init__.py`
- 📦 Module docstring: ❌

## `scripts\core\core.py`
- 📦 Module docstring: ✅

### Classes:
- `ZephyrusLoggerCore`: ✅ → `ZephyrusLoggerCore manages logging, summarization, and search for categorized en...`

## `scripts\core\log_manager.py`
- 📦 Module docstring: ✅

### Classes:
- `LogManager`: ❌

## `scripts\core\summary_tracker.py`
- 📦 Module docstring: ✅

### Classes:
- `SummaryTracker`: ✅ → `SummaryTracker manages the loading, initialization, and tracking of summary data...`

## `scripts\dev_commit.py`
- 📦 Module docstring: ❌

### Functions:
- `get_current_branch`: ✅ → `Returns the name of the current Git branch.

Returns:
    str: The current branc...`
- `get_modified_files`: ✅ → `Returns a list of files modified (but not yet committed) in the current Git work...`
- `is_valid_branch_name`: ✅ → `Checks if the provided branch name is valid according to Git naming conventions....`
- `generate_suggested_branch_name`: ✅ → `Generates a suggested branch name based on modified files and the current date.
...`
- `switch_to_new_branch`: ✅ → `Prompts the user to create and switch to a new Git branch.
Suggests a branch nam...`

## `scripts\gui\__init__.py`
- 📦 Module docstring: ❌

## `scripts\gui\app.py`
- 📦 Module docstring: ❌

### Classes:
- `ZephyrusLoggerApp`: ✅ → `Core Application Class that initializes the main window,
sets up the style manag...`

## `scripts\gui\base\__init__.py`
- 📦 Module docstring: ❌

## `scripts\gui\base\base_panel.py`
- 📦 Module docstring: ✅

### Classes:
- `BasePanel`: ✅ → `BasePanel provides common functionality for all UI panels.
Inherits from ttk.Fra...`

## `scripts\gui\base\base_tab.py`
- 📦 Module docstring: ✅

### Classes:
- `BaseTab`: ✅ → `BaseTab provides a common structure for major tabs in the application.
Inherits ...`

## `scripts\gui\gui.py`
- 📦 Module docstring: ❌

### Classes:
- `ZephyrusLoggerGUI`: ❌

## `scripts\gui\gui_controller.py`
- 📦 Module docstring: ✅

### Classes:
- `GUIController`: ✅ → `GUIController manages the interaction between the GUI and the logging core.

Att...`

## `scripts\gui\gui_logging.py`
- 📦 Module docstring: ✅

### Classes:
- `GUILogHandler`: ✅ → `A logging handler that appends log messages to a Tkinter Text widget....`

## `scripts\gui\panels\__init__.py`
- 📦 Module docstring: ❌

## `scripts\gui\panels\action_panel.py`
- 📦 Module docstring: ✅

### Classes:
- `ActionPanel`: ✅ → `ActionPanel hosts buttons for actions such as summarizing or rebuilding.

Attrib...`

## `scripts\gui\panels\coverage_panel.py`
- 📦 Module docstring: ✅

### Classes:
- `CoveragePanel`: ✅ → `CoveragePanel displays coverage metrics in a tree view.

Attributes:
    frame (...`

## `scripts\gui\panels\entry_panel.py`
- 📦 Module docstring: ✅

### Classes:
- `EntryPanel`: ✅ → `EntryPanel provides the interface for creating new log entries.

Attributes:
   ...`

## `scripts\gui\panels\log_panel.py`
- 📦 Module docstring: ✅

### Classes:
- `LogPanel`: ✅ → `LogPanel manages the display area for logs.

Attributes:
    frame (ttk.LabelFra...`

## `scripts\gui\style_manager.py`
- 📦 Module docstring: ✅

### Classes:
- `StyleManager`: ✅ → `Manages application-wide styles for tkinter and ttk.

This class can be extended...`

## `scripts\gui\tabs\__init__.py`
- 📦 Module docstring: ❌

## `scripts\gui\tabs\main_tab.py`
- 📦 Module docstring: ✅

### Classes:
- `MainTab`: ✅ → `MainTab is the primary tab for logging functionality.
It organizes child panels:...`

## `scripts\gui\widget_factory.py`
- 📦 Module docstring: ✅

### Classes:
- `WidgetFactory`: ✅ → `Factory for creating common widgets with standardized styling.

This class provi...`

## `scripts\indexers\__init__.py`
- 📦 Module docstring: ✅

## `scripts\indexers\base_indexer.py`
- 📦 Module docstring: ✅

### Classes:
- `BaseIndexer`: ❌

## `scripts\indexers\raw_log_indexer.py`
- 📦 Module docstring: ✅

### Classes:
- `RawLogIndexer`: ✅ → `Builds a FAISS index from raw entries in zephyrus_log.json.

This class is used ...`

## `scripts\indexers\summary_indexer.py`
- 📦 Module docstring: ✅

### Classes:
- `SummaryIndexer`: ✅ → `Builds a FAISS index from summarized entries in correction_summaries.json....`

## `scripts\main.py`
- 📦 Module docstring: ✅

### Functions:
- `bootstrap`: ✅ → `Bootstraps the Zephyrus Logger application.

Args:
    start_gui (bool, optional...`

## `scripts\paths.py`
- 📦 Module docstring: ❌

### Classes:
- `ZephyrusPaths`: ✅ → `Dataclass for managing and resolving all Zephyrus project file and directory pat...`

## `scripts\refactor\__init__.py`
- 📦 Module docstring: ✅

## `scripts\refactor\ast_extractor.py`
- 📦 Module docstring: ✅

### Classes:
- `ClassMethodInfo`: ✅ → `Holds information about methods in a single class.

Attributes:
    class_name (...`

### Functions:
- `extract_class_methods`: ✅ → `Extracts all classes and their methods from a Python file, including method star...`
- `compare_class_methods`: ✅ → `Compare two ClassMethodInfo objects and return which methods are missing in the ...`

## `scripts\refactor\complexity_analyzer.py`
- 📦 Module docstring: ✅

### Classes:
- `ComplexityVisitor`: ✅ → `Visits each top-level function or method definition and computes
its cyclomatic ...`

### Functions:
- `calculate_function_complexity_map`: ✅ → `Parses the given Python file and returns a mapping from function/method
full nam...`
- `calculate_module_complexity`: ✅ → `Sum all function/method complexities in the module and add 1 overhead.

Args:
  ...`
- `calculate_cyclomatic_complexity_for_module`: ✅ → `Deprecated alias for calculate_module_complexity.

Issues a DeprecationWarning a...`

## `scripts\refactor\coverage_parser.py`
- 📦 Module docstring: ✅

### Functions:
- `parse_coverage_xml_to_method_hits`: ✅ → `Parse coverage XML and map line-level coverage to method-level stats for a singl...`

## `scripts\refactor\method_line_ranges.py`
- 📦 Module docstring: ✅

### Classes:
- `MethodRangeVisitor`: ✅ → `Collects start and end line numbers for each function or async method,
keyed by ...`

### Functions:
- `extract_method_line_ranges`: ✅ → `Parses a Python file and returns a dict mapping each function or method
to its (...`

## `scripts\refactor\quality_checker.py`
- 📦 Module docstring: ✅

### Functions:
- `safe_print`: ✅ → `Safely prints a message, handling potential Unicode encoding errors.

Args:
    ...`
- `_normalize`: ✅ → `Normalizes a file path to a relative path within the project.

Args:
    path (s...`
- `run_command`: ✅ → `Executes a command and saves the output to a specified path.

Args:
    cmd (Seq...`
- `run_black`: ✅ → `Runs the Black code formatter on the project.

Returns:
    int: The return code...`
- `run_flake8`: ✅ → `Runs Flake8 for linting the project.

Returns:
    int: The return code of the F...`
- `run_mypy`: ✅ → `Runs MyPy for type checking the project.

Returns:
    int: The return code of t...`
- `run_pydocstyle`: ✅ → `Runs Pydocstyle for checking compliance with Python docstring conventions.

Retu...`
- `run_coverage_xml`: ✅ → `Runs coverage analysis and generates an XML report.

Returns:
    int: The retur...`
- `_read_report`: ✅ → `Reads a report from the specified path and returns its content as a string.

Arg...`
- `_add_flake8_quality`: ✅ → `Adds Flake8 quality data to the quality report.

Args:
    quality (Dict[str, Di...`
- `_add_black_quality`: ✅ → `Adds Black quality data to the quality report.

Args:
    quality (Dict[str, Dic...`
- `_add_mypy_quality`: ✅ → `Adds MyPy quality data to the quality report.

Args:
    quality (Dict[str, Dict...`
- `_add_pydocstyle_quality`: ✅ → `Adds Pydocstyle quality data to the quality report.

Args:
    quality (Dict[str...`
- `_add_coverage_quality`: ✅ → `Adds coverage quality data to the quality report.

Args:
    quality (Dict[str, ...`
- `merge_into_refactor_guard`: ✅ → `Merges quality reports into a refactor audit JSON file.

Args:
    audit_path (s...`
- `merge_reports`: ✅ → `Merge two refactor guard audit JSON files into a single report.
Later entries ov...`

## `scripts\refactor\refactor_guard.py`
- 📦 Module docstring: ✅

### Classes:
- `AnalysisError`: ✅ → `Raised when an error occurs during analysis....`
- `RefactorGuard`: ✅ → `A class for analyzing and validating Python code refactoring.

Attributes:
    c...`

### Functions:
- `print_human_readable`: ✅ → `Print human-readable audit, filtered by CLI flags in args.

Args:
    audit (Dic...`

## `scripts\refactor\refactor_guard_cli.py`
- 📦 Module docstring: ✅

### Functions:
- `parse_args`: ✅ → `Parses command-line arguments for the RefactorGuard CLI.

Returns:
    argparse....`
- `handle_merge`: ✅ → `Handles the merging of audit reports based on the provided arguments.

Args:
   ...`
- `handle_full_scan`: ✅ → `Performs a full scan of the specified directories or files.

Args:
    args (arg...`
- `handle_single_file`: ✅ → `Handles the analysis of a single file for auditing.

Args:
    args (argparse.Na...`
- `main`: ✅ → `Main entry point for the RefactorGuard CLI.

This function orchestrates the comm...`

## `scripts\utils\__init__.py`
- 📦 Module docstring: ❌

## `scripts\utils\complexity_summary.py`
- 📦 Module docstring: ✅

### Functions:
- `analyze_complexity`: ✅ → `Analyzes code complexity from a JSON audit file and prints a summary.

Parameter...`
- `run_analysis`: ✅ → `Analyzes method complexity across files and prints a summary report.

Args:
    ...`

## `scripts\utils\docstring_linter.py`
- 📦 Module docstring: ✅

### Classes:
- `DocstringAnalyzer`: ❌
- `DocstringAuditCLI`: ❌

## `scripts\utils\enrich_refactor.py`
- 📦 Module docstring: ✅

### Functions:
- `safe_print`: ✅ → `Prints a message safely, handling UnicodeEncodeError by removing non-ASCII chara...`
- `enrich_refactor_audit`: ✅ → `Enriches a refactor audit file with linting and coverage data.

Generates missin...`

## `scripts\utils\file_utils.py`
- 📦 Module docstring: ❌

### Functions:
- `sanitize_filename`: ✅ → `Return *name* stripped of illegal chars and truncated to 100 chars....`
- `get_timestamp`: ✅ → `Current time as ``YYYY‑MM‑DD_HH‑MM‑SS``....`
- `_to_path`: ✅ → `Internal: coerce *p* to ``Path`` exactly once....`
- `safe_path`: ✅ → `Ensure ``path.parent`` exists; return ``Path``....`
- `write_json`: ❌
- `read_json`: ❌
- `safe_read_json`: ❌
- `make_backup`: ❌
- `zip_python_files`: ✅ → `Zip all ``.py`` files under *root_dir* (recursively), excluding any directory wh...`

## `scripts\utils\git_utils.py`
- 📦 Module docstring: ✅

### Functions:
- `get_changed_files`: ✅ → `Returns a list of changed Python files compared to the specified Git base branch...`
- `interactive_commit_flow`: ✅ → `Guides the user through an interactive Git commit and push process.

Prompts to ...`
- `get_current_branch`: ✅ → `Returns the name of the current Git branch as a string.

Executes a Git command ...`

## `scripts\utils\gui_helpers.py`
- 📦 Module docstring: ✅

### Functions:
- `validate_log_input`: ✅ → `Returns False if the input is empty, None, or just whitespace.
Logs a warning if...`
- `get_current_date`: ✅ → `Returns the current date as a string in 'YYYY-MM-DD' format.

:return: Current d...`
- `get_current_timestamp`: ✅ → `Returns the current date and time as a formatted string (YYYY-MM-DD HH:MM:SS)....`
- `clear_text_input`: ✅ → `Clears all text from the given Tkinter text entry widget.

Args:
    entry_widge...`
- `update_status_label`: ✅ → `Update the text and foreground color of a Tkinter label widget.

Args:
    label...`
- `get_selected_option`: ✅ → `Returns the currently selected option from a Tkinter menu variable, or a default...`
- `append_log_entry`: ✅ → `Appends a log entry with a timestamp and content to the specified log file, orga...`
- `get_category_options`: ✅ → `Retrieves a list of category names from a JSON file at the given path.

Args:
  ...`
- `create_status_label`: ✅ → `Create and pack a status label widget in the given root window.

Args:
    root:...`
- `create_log_frame`: ✅ → `Creates and returns a disabled scrolled text widget within a frame for logging p...`
- `log_message`: ✅ → `Appends a timestamped message to the provided Tkinter text widget for logging pu...`
- `create_dropdown_menu`: ✅ → `Creates a labeled dropdown menu (OptionMenu) in the given Tkinter frame.

Args:
...`
- `create_button`: ✅ → `Creates and returns a Tkinter Button widget with customizable text, command, siz...`
- `show_messagebox`: ✅ → `Displays a message box with the specified icon, title, and message using tkinter...`
- `create_text_entry`: ✅ → `Creates a text entry widget for user input.

Args:
    root (tk.Tk or tk.Frame):...`
- `format_summary_results`: ✅ → `Formats a list of result items into a readable summary string.

Each result can ...`
- `format_raw_results`: ✅ → `Formats a list of raw result items into a readable string.

Each result is proce...`
- `display_message`: ✅ → `Displays an informational message box....`
- `display_error`: ✅ → `Displays an error message box....`
- `format_coverage_data`: ✅ → `Formats the structured coverage data into a readable string grouped by main cate...`

## `scripts\utils\link_summaries_to_raw_logs.py`
- 📦 Module docstring: ✅

### Functions:
- `flatten_raw_entries`: ✅ → `Flatten raw log entries for a given main category and subcategory across all dat...`
- `inject_entries_into_summaries`: ✅ → `Injects corresponding raw log entries into each batch of correction summaries ba...`

## `scripts\utils\zip_util.py`
- 📦 Module docstring: ✅

### Functions:
- `main`: ✅ → `Parses command-line arguments to zip all .py files in a project, excluding speci...`

## `tests\__init__.py`
- 📦 Module docstring: ❌

## `tests\integration\__init__.py`
- 📦 Module docstring: ❌

## `tests\mock_data\__init__.py`
- 📦 Module docstring: ❌

## `tests\mocks\__init__.py`
- 📦 Module docstring: ❌

## `tests\smoke\__init__.py`
- 📦 Module docstring: ❌

## `tests\unit\__init__.py`
- 📦 Module docstring: ❌

## `tests\unit\ai\__init__.py`
- 📦 Module docstring: ❌

## `tests\unit\ci_analyzer\__ini__.py`
- 📦 Module docstring: ❌

## `tests\unit\config\__init__.py`
- 📦 Module docstring: ❌

## `tests\unit\core\__init__.py`
- 📦 Module docstring: ❌

## `tests\unit\gui\__init__.py`
- 📦 Module docstring: ❌

## `tests\unit\indexers\__init__.py`
- 📦 Module docstring: ❌

## `tests\unit\refactor\__init__.py`
- 📦 Module docstring: ❌

## `tests\unit\utils\__init__.py`
- 📦 Module docstring: ❌