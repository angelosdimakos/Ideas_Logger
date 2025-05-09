# 📊 CI Code Quality Audit Report

## Executive Summary

| Metric                     | Value    | Visual |
|----------------------------|----------|--------|
| Files analyzed             | `122`    |     |
| Files with issues          | `60`     |     |
| **Top risk file**          | `kg/modules/visualization.py` |     |
| Methods audited            | `322`    |     |
| Missing tests              | `108`    | ▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░ 🔴 |
| Missing docstrings         | `248`    | ▓▓▓▓░░░░░░░░░░░░░░░░ 🔴 |
| Linter issues              | `222`    | ▓▓▓▓▓▓░░░░░░░░░░░░░░ 🔴 |



## 🧨 Severity Rankings (Top 10)

| File | 🔣 Mypy | 🧼 Lint | 📉 Cx | 📊 Cov | 📈 Score | 🎯 Priority |
|------|--------|--------|------|--------|----------|-------------|
| `kg/modules/visualization.py` | 13 | 1 | 4.62 🟢 | 26.3% ▓▓▓▓▓░░░░░░░░░░░░░░░ | 33.6 | 🔥 High |
| `gui/gui_helpers.py` | 9 | 4 | 2.25 🟢 | 0.0% ░░░░░░░░░░░░░░░░░░░░ | 28.25 | ⚠️ Medium |
| `refactor/strictness_analyzer.py` | 7 | 0 | 8.0 🟢 | 0.0% ░░░░░░░░░░░░░░░░░░░░ | 24.0 | ⚠️ Medium |
| `refactor/parsers/docstring_parser.py` | 5 | 5 | 4.5 🟢 | 27.0% ▓▓▓▓▓░░░░░░░░░░░░░░░ | 23.46 | ⚠️ Medium |
| `utils/file_utils.py` | 5 | 5 | 3.89 🟢 | 73.7% ▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░ | 21.92 | ⚠️ Medium |
| `refactor/refactor_guard.py` | 0 | 5 | 12.0 🟡 | 54.5% ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░ | 20.41 | ⚠️ Medium |
| `refactor/parsers/json_coverage_parser.py` | 0 | 0 | 17.0 🟡 | 1.4% ░░░░░░░░░░░░░░░░░░░░ | 18.97 | ⚠️ Medium |
| `refactor/parsers/coverage_parser.py` | 4 | 1 | 7.67 🟢 | 13.4% ▓▓░░░░░░░░░░░░░░░░░░ | 18.9 | ⚠️ Medium |
| `core/log_manager.py` | 6 | 2 | 2.14 🟢 | 24.6% ▓▓▓▓░░░░░░░░░░░░░░░░ | 18.65 | ⚠️ Medium |
| `ai/ai_summarizer.py` | 3 | 5 | 3.25 🟢 | 34.2% ▓▓▓▓▓▓░░░░░░░░░░░░░░ | 18.07 | ⚠️ Medium |


## 📊 Summary Metrics

- Total methods audited: **322**
- 🚫 Methods missing tests: **108**
- 🔺 High-complexity methods (≥10): **27**
- 📚 Methods missing docstrings: **248**
- 🧼 Linter issues detected: **222**




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
- `GraphVisualizer.visualize_graph`: Complexity = 10, Coverage = 1.4%
- `GraphVisualizer._position_nodes_in_layers`: Complexity = 3, Coverage = 41.7%
- `GraphVisualizer._handle_remaining_nodes`: Complexity = 6, Coverage = 21.1%
- `GraphVisualizer._draw_module_rectangles`: Complexity = 8, Coverage = 1.6%
- `GraphVisualizer._get_node_colors`: Complexity = 3, Coverage = 3.3%
- `GraphVisualizer._get_complexity_color`: Complexity = 3, Coverage = 37.5%
- `GraphVisualizer._shorten_label`: Complexity = 3, Coverage = 37.5%

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
- `validate_log_input`: Complexity = 3, Coverage = 0.0%
- `get_current_date`: Complexity = 1, Coverage = 0.0%
- `get_current_timestamp`: Complexity = 1, Coverage = 0.0%
- `clear_text_input`: Complexity = 1, Coverage = 0.0%
- `update_status_label`: Complexity = 1, Coverage = 0.0%
- `get_selected_option`: Complexity = 2, Coverage = 0.0%
- `append_log_entry`: Complexity = 4, Coverage = 0.0%
- `get_category_options`: Complexity = 3, Coverage = 0.0%
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

<details>
<summary>🔍 `refactor/strictness_analyzer.py`</summary>


**❗ MyPy Errors:**
- scripts/refactor/strictness_analyzer.py:202: error: Incompatible return value type (got "None", expected "Path")  [return-value]
- scripts/refactor/strictness_analyzer.py:205: error: Incompatible return value type (got "None", expected "Path")  [return-value]
- scripts/refactor/strictness_analyzer.py:237: error: Incompatible types in assignment (expression has type "Path", variable has type "dict[str, Any]")  [assignment]
- scripts/refactor/strictness_analyzer.py:240: error: "dict[str, Any]" has no attribute "resolve"  [attr-defined]
- scripts/refactor/strictness_analyzer.py:245: error: Argument 1 to "map_test_to_prod_path" has incompatible type "dict[str, Any]"; expected "Path"  [arg-type]
- scripts/refactor/strictness_analyzer.py:278: error: Generator has incompatible item type "object"; expected "bool"  [misc]
- scripts/refactor/strictness_analyzer.py:345: error: Missing type parameters for generic type "Dict"  [type-arg]

**📉 Complexity & Coverage Issues:**
- `extract_test_functions`: Complexity = 5, Coverage = 0.0%
- `analyze_strictness`: Complexity = 7, Coverage = 0.0%
- `compute_strictness_score`: Complexity = 1, Coverage = 0.0%
- `attach_coverage_hits`: Complexity = 6, Coverage = 0.0%
- `map_test_to_prod_path`: Complexity = 11, Coverage = 0.0%
- `map_tests_to_prod_code`: Complexity = 17, Coverage = 0.0%
- `scan_test_directory`: Complexity = 4, Coverage = 0.0%
- `main`: Complexity = 13, Coverage = 0.0%

**📚 Function Descriptions:**
- `extract_test_functions`: Extract test function names and line ranges from a Python test file.
  - Args: filepath (Path): The path to the Python test file.
  - Returns: List[Dict[str, Any]]: A list of dictionaries containing test function names and their line ranges.
- `analyze_strictness`: Analyze basic strictness heuristics on a test function.
  - Args: lines (List[str]): The lines of the test function.
func (Dict[str, Any]): A dictionary containing the test function's metadata.
  - Returns: Dict[str, Any]: A dictionary containing the analysis results.
- `compute_strictness_score`: Compute a weighted strictness score using heuristics and coverage hit ratio.
  - Args: asserts (int): The number of assert statements.
raises (int): The number of expected exceptions.
mocks (int): The number of mock objects used.
branches (int): The number of branches in the code.
length (int): The length of the test function.
hit_ratio (float): The coverage hit ratio.
  - Returns: float: The computed strictness score.
- `attach_coverage_hits`: Attach line hit counts and recompute score.
  - Args: results (List[Dict[str, Any]]): The results of the test analysis.
coverage_data (Dict[str, Dict[str, Any]]): The coverage data mapping.
  - Returns: None
- `map_test_to_prod_path`: Map a test file path to its corresponding production code path.
  - Args: test_path (Path): The path to the test file.
test_root (Path): The root directory of the test files.
source_root (Path): The root directory of the production code.
  - Returns: Path: The corresponding production code path.
- `map_tests_to_prod_code`: Map test functions to production code they cover.
  - Args: test_results (List[Dict[str, Any]]): The results of the test analysis.
test_root (Path): The root directory of the test files.
source_root (Path): The root directory of the production code.
coverage_data (Dict[str, Dict[str, Any]]): The coverage data mapping.
  - Returns: None
- `scan_test_directory`: Scan test directory and extract test function information.
  - Args: tests_path (Path): The path to the test directory.
  - Returns: List[Dict[str, Any]]: A list of dictionaries containing test function information.
- `main`: Main entry point for the script.
  - Args: tests_dir (str): The directory containing test files.
source_dir (str): The directory containing production code.
coverage_path (str): The path to the coverage data file.
output_path (Optional[str]): The path to the output file (if any).
  - Returns: None

</details>
