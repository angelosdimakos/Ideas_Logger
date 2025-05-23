# 📊 CI Code Quality Audit Report

## Executive Summary

| Metric                     | Value    | Visual |
|----------------------------|----------|--------|
| Files analyzed             | `160`    |     |
| Files with issues          | `66`     |     |
| **Top risk file**          | `kg/modules/visualization.py` |     |
| Methods audited            | `350`    |     |
| Missing tests              | `76`    | ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░ 🟡 |
| Missing docstrings         | `287`    | ▓▓▓░░░░░░░░░░░░░░░░░ 🔴 |
| Linter issues              | `244`    | ▓▓▓▓▓▓░░░░░░░░░░░░░░ 🔴 |



## 🧨 Severity Rankings (Top 10)

| File | 🔣 Mypy | 🧼 Lint | 📉 Cx | 📊 Cov | 📈 Score | 🎯 Priority |
|------|--------|--------|------|--------|----------|-------------|
| `kg/modules/visualization.py` | 13 | 1 | 4.62 🟢 | 50.8% ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░ | 33.11 | 🔥 High |
| `ai/llm_optimization.py` | 10 | 2 | 7.33 🟢 | 99.4% ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░ | 30.34 | 🔥 High |
| `gui/gui_helpers.py` | 9 | 4 | 2.25 🟢 | 27.0% ▓▓▓▓▓░░░░░░░░░░░░░░░ | 27.71 | ⚠️ Medium |
| `refactor/parsers/docstring_parser.py` | 5 | 5 | 5.0 🟢 | 93.6% ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░ | 22.63 | ⚠️ Medium |
| `unified_code_assistant/prompt_builder.py` | 5 | 2 | 9.5 🟢 | 100.0% ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ | 22.5 | ⚠️ Medium |
| `ai/module_idea_generator.py` | 6 | 1 | 7.6 🟢 | 63.8% ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░ | 21.82 | ⚠️ Medium |
| `utils/file_utils.py` | 5 | 5 | 3.89 🟢 | 93.0% ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░ | 21.53 | ⚠️ Medium |
| `refactor/refactor_guard.py` | 0 | 5 | 11.83 🟡 | 60.3% ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░ | 20.13 | ⚠️ Medium |
| `unified_code_assistant/assistant_cli.py` | 3 | 2 | 9.5 🟢 | 37.1% ▓▓▓▓▓▓▓░░░░░░░░░░░░░ | 19.76 | ⚠️ Medium |
| `ai/llm_refactor_advisor.py` | 7 | 0 | 5.0 🟢 | 91.7% ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░ | 19.17 | ⚠️ Medium |


## 📊 Summary Metrics

- Total methods audited: **350**
- 🚫 Methods missing tests: **76**
- 🔺 High-complexity methods (≥10): **29**
- 📚 Methods missing docstrings: **287**
- 🧼 Linter issues detected: **244**




## 🔎 Top Offenders: Detailed Analysis

<details>
<summary>🔍 `kg/modules/visualization.py`</summary>


**❗ MyPy Errors:**
- scripts/kg/modules/visualization.py:17: error: Function is missing a return type annotation  [no-untyped-def]
- scripts/kg/modules/visualization.py:35: error: "Figure" has no attribute "graph"  [attr-defined]
- scripts/kg/modules/visualization.py:38: error: Need type annotation for "layers"  [var-annotated]
- scripts/kg/modules/visualization.py:42: error: Need type annotation for "modules" (hint: "modules: dict[<type>, <type>] = ...")  [var-annotated]
- scripts/kg/modules/visualization.py:94: error: Missing type parameters for generic type "list"  [type-arg]
- scripts/kg/modules/visualization.py:94: error: Missing type parameters for generic type "tuple"  [type-arg]
- scripts/kg/modules/visualization.py:119: error: Missing type parameters for generic type "tuple"  [type-arg]
- scripts/kg/modules/visualization.py:128: error: "Figure" has no attribute "graph"  [attr-defined]
- scripts/kg/modules/visualization.py:141: error: Name "plt.Axes" is not defined  [name-defined]
- scripts/kg/modules/visualization.py:142: error: Missing type parameters for generic type "list"  [type-arg]
- scripts/kg/modules/visualization.py:143: error: Missing type parameters for generic type "tuple"  [type-arg]
- scripts/kg/modules/visualization.py:155: error: "Figure" has no attribute "graph"  [attr-defined]
- scripts/kg/modules/visualization.py:202: error: Missing type parameters for generic type "list"  [type-arg]

**🧼 Pydocstyle Issues:**
- `_handle_remaining_nodes`: D205 — 1 blank line required between summary line and description (found 0)

**📉 Complexity & Coverage Issues:**
- `GraphVisualizer.visualize_graph`: Complexity = 10, Coverage = 0.0%
- `GraphVisualizer._handle_remaining_nodes`: Complexity = 6, Coverage = 21.1%
- `GraphVisualizer._draw_module_rectangles`: Complexity = 8, Coverage = 0.0%
- `GraphVisualizer._get_node_colors`: Complexity = 3, Coverage = 0.0%

**📚 Function Descriptions:**
- `__init__`: Initialize the visualizer.
  - Args: None
  - Returns: None
- `visualize_graph`: Visualize the graph with complexity scores.
  - Args: graph: The graph to visualize.
complexity_scores: A dictionary of complexity scores for nodes.
title: The title of the visualization.
  - Returns: None
- `_position_nodes_in_layers`: Position nodes in horizontal layers by type.
  - Args: layers: Dictionary of node types and their nodes.
  - Returns: Dictionary of node positions.
- `_handle_remaining_nodes`: Add positions for any nodes that weren't positioned in the initial layout.
This modifies the pos dictionary in-place.
  - Args: pos: Dictionary of node positions to update.
  - Returns: None
- `_draw_module_rectangles`: Draw colored rectangles around modules based on complexity.
  - Args: ax: Matplotlib axes to draw on.
modules: Dictionary of module nodes.
pos: Dictionary of node positions.
complexity_scores: Dictionary of complexity scores.
  - Returns: None
- `_get_node_colors`: Get node colors based on node type and module complexity.
  - Args: graph: The knowledge graph.
complexity_scores: Dictionary of complexity scores.
  - Returns: List of colors for each node.
- `_get_complexity_color`: Get the color representation based on the complexity score.
  - Args: score: The complexity score.
  - Returns: The color corresponding to the complexity score.
- `_shorten_label`: Shorten a label for display purposes.
  - Args: name: The label to shorten.
  - Returns: The shortened label.

</details>

<details>
<summary>🔍 `ai/llm_optimization.py`</summary>


**❗ MyPy Errors:**
- scripts/ai/llm_optimization.py:57: error: Missing type parameters for generic type "Dict"  [type-arg]
- scripts/ai/llm_optimization.py:76: error: Missing type parameters for generic type "dict"  [type-arg]
- scripts/ai/llm_optimization.py:83: error: Missing type parameters for generic type "dict"  [type-arg]
- scripts/ai/llm_optimization.py:84: error: Missing type parameters for generic type "dict"  [type-arg]
- scripts/ai/llm_optimization.py:85: error: Missing type parameters for generic type "dict"  [type-arg]
- scripts/ai/llm_optimization.py:110: error: Missing type parameters for generic type "dict"  [type-arg]
- scripts/ai/llm_optimization.py:148: error: Missing type parameters for generic type "list"  [type-arg]
- scripts/ai/llm_optimization.py:235: error: Need type annotation for "file_prefixes" (hint: "file_prefixes: dict[<type>, <type>] = ...")  [var-annotated]
- scripts/ai/llm_optimization.py:348: error: Missing type parameters for generic type "list"  [type-arg]
- scripts/ai/llm_optimization.py:379: error: Missing type parameters for generic type "list"  [type-arg]

**🧼 Pydocstyle Issues:**
- `build_refactor_prompt`: D208 — Docstring is over-indented
- `build_strategic_recommendations_prompt`: D208 — Docstring is over-indented

**📉 Complexity & Coverage Issues:**
- `_categorise_issues`: Complexity = 9, Coverage = 100.0%
- `summarize_file_data_for_llm`: Complexity = 7, Coverage = 100.0%
- `extract_top_issues`: Complexity = 11, Coverage = 100.0%
- `build_strategic_recommendations_prompt`: Complexity = 15, Coverage = 95.0%
- `compute_severity`: Complexity = 9, Coverage = 100.0%
- `_summarise_offenders`: Complexity = 7, Coverage = 100.0%
- `_format_offender_block`: Complexity = 6, Coverage = 100.0%

**📚 Function Descriptions:**
- `_mean`: Calculates the mean of a list of floats.
Returns 0.0 if the list is empty.
  - Args: None
  - Returns: None
- `_categorise_issues`: Returns a summary of how many files fall into each major code quality issue category.
The summary includes counts of files with more than 5 type errors, average complexity greater than 7, and average coverage below 60%.
  - Args: None
  - Returns: None
- `summarize_file_data_for_llm`: Generates a summary dictionary of code quality metrics for a single file.
Extracts and computes average complexity, coverage percentage, MyPy error count, and docstring completeness from nested file data. Returns a dictionary with legacy-compatible keys, including the file name, full path, rounded metrics, docstring ratio, and a list of up to three top issues.
  - Args: None
  - Returns: None
- `extract_top_issues`: Extracts up to a specified number of top code quality issues from file data.
The function prioritizes the first MyPy error, the first function with high complexity (complexity > 10), and the first function with low coverage (coverage < 50%), returning formatted issue descriptions.
  - Args: file_data: Dictionary containing code quality metrics for a file.
max_issues: Maximum number of issues to extract.
  - Returns: A list of formatted strings describing the top issues found in the file.
- `build_refactor_prompt`: Builds an LLM prompt requesting strategic refactoring suggestions for a list of offender files.
The prompt summarizes up to `limit` files with significant code quality issues, applies a persona and template from the configuration, and includes both a summary and detailed offender information. The resulting prompt instructs the LLM to focus on identifying refactoring patterns rather than file-specific advice.
  - Args: offenders: List of tuples containing file details and metrics for files needing refactoring.
config: Configuration object providing persona and prompt template.
verbose: If True, includes detailed information for each file; otherwise, provides a concise summary.
limit: Maximum number of offender files to include in the prompt.
  - Returns: A formatted prompt string for use with an LLM.
- `build_strategic_recommendations_prompt`: Constructs a detailed prompt for an LLM to generate strategic, actionable recommendations for improving code quality and test coverage based on severity data and summary metrics.
The prompt summarizes the distribution of key issues (high complexity, low coverage, type errors), highlights problematic modules with multiple severe files, and lists the top offenders. It instructs the LLM to provide specific, non-generic recommendations tied directly to the identified files and modules, prioritizing complexity, coverage, type errors, and documentation.
  - Args: severity_data: List of dictionaries containing per-file severity metrics and scores.
summary_metrics: Overall codebase metrics, either as a formatted string or a dictionary.
limit: Maximum number of top offender files to include in the summary (default: 30).
  - Returns: A formatted prompt string for use with an LLM, emphasizing targeted, codebase-specific recommendations.
- `compute_severity`: Calculates a weighted severity score and summary metrics for a single module.
The severity score combines counts of MyPy errors, pydocstyle lint issues, average function complexity, and lack of test coverage using fixed weights. Returns a dictionary with the file name, full path, error and issue counts, average complexity, average coverage percentage, and the computed severity score.
  - Args: None
  - Returns: None
- `_summarise_offenders`: Aggregates a list of offender files into a summary of key code quality issues.
Counts and lists up to five example files for each of the following categories: high complexity (complexity > 8), low coverage (coverage < 50%), and many type errors (more than 5 type errors). Returns a formatted multiline string summarizing the counts and sample file names per category.
  - Args: None
  - Returns: None
- `_fmt`: Formats a list of strings as a comma-separated string, truncating with '...' if more than five items.
  - Args: lst: List of strings to format.
  - Returns: A string of up to five comma-separated items from the list, followed by '...' if the list contains more than five items.
- `_format_offender_block`: Formats offender file details into a summary block for inclusion in LLM prompts.
If verbose is True, returns a detailed multiline summary for each file including severity score, error counts, complexity, coverage, and sample errors. Otherwise, returns a concise single-line summary per file.
  - Args: None
  - Returns: None

</details>

<details>
<summary>🔍 `gui/gui_helpers.py`</summary>


**❗ MyPy Errors:**
- scripts/gui/gui_helpers.py:88: error: Call to untyped function "get" in typed context  [no-untyped-call]
- scripts/gui/gui_helpers.py:118: error: Missing type parameters for generic type "list"  [type-arg]
- scripts/gui/gui_helpers.py:151: error: Missing type parameters for generic type "tuple"  [type-arg]
- scripts/gui/gui_helpers.py:185: error: Missing type parameters for generic type "list"  [type-arg]
- scripts/gui/gui_helpers.py:201: error: Argument 2 to "OptionMenu" has incompatible type "Variable"; expected "StringVar"  [arg-type]
- scripts/gui/gui_helpers.py:209: error: Function "builtins.callable" is not valid as a type  [valid-type]
- scripts/gui/gui_helpers.py:267: error: Missing type parameters for generic type "list"  [type-arg]
- scripts/gui/gui_helpers.py:297: error: Missing type parameters for generic type "list"  [type-arg]
- scripts/gui/gui_helpers.py:340: error: Missing type parameters for generic type "dict"  [type-arg]

**🧼 Pydocstyle Issues:**
- `validate_log_input`: D205 — 1 blank line required between summary line and description (found 0)
- `get_current_timestamp`: D200 — One-line docstring should fit on one line with quotes (found 3)
- `display_message`: D200 — One-line docstring should fit on one line with quotes (found 3)
- `display_error`: D200 — One-line docstring should fit on one line with quotes (found 3)

**📉 Complexity & Coverage Issues:**
- `clear_text_input`: Complexity = 1, Coverage = 0.0%
- `update_status_label`: Complexity = 1, Coverage = 0.0%
- `create_status_label`: Complexity = 1, Coverage = 0.0%
- `create_log_frame`: Complexity = 1, Coverage = 0.0%
- `log_message`: Complexity = 1, Coverage = 0.0%
- `create_dropdown_menu`: Complexity = 1, Coverage = 0.0%
- `create_button`: Complexity = 1, Coverage = 0.0%
- `show_messagebox`: Complexity = 4, Coverage = 0.0%
- `create_text_entry`: Complexity = 1, Coverage = 0.0%
- `format_summary_results`: Complexity = 7, Coverage = 0.0%
- `format_raw_results`: Complexity = 6, Coverage = 0.0%
- `display_message`: Complexity = 1, Coverage = 0.0%
- `display_error`: Complexity = 1, Coverage = 0.0%
- `format_coverage_data`: Complexity = 4, Coverage = 0.0%

**📚 Function Descriptions:**
- `validate_log_input`: Returns False if the input is empty, None, or just whitespace.
Logs a warning if invalid.
  - Args: None
  - Returns: None
- `get_current_date`: Returns the current date as a string in 'YYYY-MM-DD' format.
:return: Current date as a string.
:rtype: str
  - Args: None
  - Returns: None
- `get_current_timestamp`: Returns the current date and time as a formatted string (YYYY-MM-DD HH:MM:SS).
  - Args: None
  - Returns: None
- `clear_text_input`: Clears all text from the given Tkinter text entry widget.
  - Args: entry_widget: The Tkinter text widget to be cleared.
  - Returns: None
- `update_status_label`: Update the text and foreground color of a Tkinter label widget.
  - Args: label (tk.Label): The label widget to update.
message (str): The text to display on the label.
color (str, optional): The text color. Defaults to "blue".
  - Returns: None
- `get_selected_option`: Returns the currently selected option from a Tkinter menu variable, or a default value if none is selected.
  - Args: menu_var: A Tkinter variable associated with a menu widget.
default (str, optional): The value to return if no option is selected. Defaults to "General".
  - Returns: str: The selected option or the default value.
- `append_log_entry`: Appends a log entry with a timestamp and content to the specified log file, organizing entries by date, category, and subcategory.
  - Args: log_file (str): Path to the JSON log file.
date (str): Date key for the log entry (YYYY-MM-DD).
category (str): Category under which to store the entry.
subcategory (str): Subcategory under the category.
entry_text (str): The content of the log entry.
  - Returns: None
- `get_category_options`: Retrieves a list of category names from a JSON file at the given path.
  - Args: categories_json_path (str): Path to the JSON file containing categories.
  - Returns: list: List of category names, or an empty list if reading fails.
- `create_status_label`: Create and pack a status label widget in the given root window.
  - Args: root: The parent Tkinter widget.
status_var: A Tkinter StringVar to display as the label's text.
  - Returns: The created Label widget.
- `create_log_frame`: Creates and returns a disabled scrolled text widget within a frame for logging purposes in a Tkinter GUI.
  - Args: root: The parent Tkinter widget.
  - Returns: tuple: (log_text, log_frame) where log_text is the ScrolledText widget and log_frame is the containing Frame.
- `log_message`: Appends a timestamped message to the provided Tkinter text widget for logging purposes.
  - Args: log_text_widget (tkinter.Text): The text widget where the log message will be displayed.
message (str): The message to log.
  - Returns: None
- `create_dropdown_menu`: Creates a labeled dropdown menu (OptionMenu) in the given Tkinter frame.
  - Args: frame: The parent Tkinter frame to place the dropdown menu in.
label_text: The text to display as the label next to the dropdown.
variable: A Tkinter variable to store the selected option.
options: A list of options to display in the dropdown menu.
  - Returns: The created Tkinter OptionMenu widget.
- `create_button`: Creates and returns a Tkinter Button widget with customizable text, command, size, and colors.
  - Args: frame: The parent widget where the button will be placed.
text (str): The label displayed on the button.
command (callable): The function to be called when the button is clicked.
width (int, optional): The width of the button. Defaults to 15.
height (int, optional): The height of the button. Defaults to 2.
bg (str, optional): The background color of the button. Defaults to "#4CAF50".
fg (str, optional): The text color of the button. Defaults to "white".
  - Returns: tk.Button: The configured Button widget.
- `show_messagebox`: Displays a message box with the specified icon, title, and message using tkinter.
  - Args: icon (str): Type of message box to display ('info', 'warning', or 'error').
title (str): The title of the message box window.
message (str): The message to display in the message box.
  - Returns: None
- `create_text_entry`: Creates a text entry widget for user input.
  - Args: root (tk.Tk or tk.Frame): The parent widget.
height (int): Number of lines tall.
width (int): Number of characters wide.
  - Returns: tk.Text: A configured Text widget.
- `format_summary_results`: Formats a list of result items into a readable summary string.
Each result can be a dict with 'score' and 'text' keys, a tuple/list with score and text,
or any other type, which will be converted to string with a default score of 0.0.
Handles exceptions gracefully and includes error information in the output.
  - Args: results (list): List of result items to format.
  - Returns: str: Formatted summary string with scores and texts.
- `format_raw_results`: Formats a list of raw result items into a readable string.
Each result is processed based on its type (dict, list/tuple, or other),
and formatted with a '[RAW LOG MATCH]' prefix. Handles exceptions by
including error details in the output.
  - Args: results (list): List of raw result items to format.
  - Returns: str: Formatted string representation of all results.
- `display_message`: Displays an informational message box.
  - Args: None
  - Returns: None
- `display_error`: Displays an error message box.
  - Args: None
  - Returns: None
- `format_coverage_data`: Formats the structured coverage data into a readable string grouped by main category.
  - Args: data (list[dict]): List of coverage data entries.
  - Returns: str: A nicely formatted string for displaying coverage stats.

</details>
