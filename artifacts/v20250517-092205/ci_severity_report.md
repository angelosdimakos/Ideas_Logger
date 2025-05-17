# 📊 CI Code Quality Audit Report

## Executive Summary

| Metric                     | Value    | Visual |
|----------------------------|----------|--------|
| Files analyzed             | `154`    |     |
| Files with issues          | `64`     |     |
| **Top risk file**          | `kg/modules/visualization.py` |     |
| Methods audited            | `350`    |     |
| Missing tests              | `98`    | ▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░ 🟡 |
| Missing docstrings         | `295`    | ▓▓▓░░░░░░░░░░░░░░░░░ 🔴 |
| Linter issues              | `252`    | ▓▓▓▓▓░░░░░░░░░░░░░░░ 🔴 |



## 🧨 Severity Rankings (Top 10)

| File | 🔣 Mypy | 🧼 Lint | 📉 Cx | 📊 Cov | 📈 Score | 🎯 Priority |
|------|--------|--------|------|--------|----------|-------------|
| `kg/modules/visualization.py` | 13 | 1 | 4.62 🟢 | 50.8% ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░ | 33.11 | 🔥 High |
| `ai/llm_optimization.py` | 10 | 2 | 7.33 🟢 | 99.2% ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░ | 30.35 | 🔥 High |
| `ai/refactor_advisor_cli.py` | 11 | 0 | 4.56 🟢 | 0.0% ░░░░░░░░░░░░░░░░░░░░ | 28.56 | ⚠️ Medium |
| `gui/gui_helpers.py` | 9 | 4 | 2.25 🟢 | 27.0% ▓▓▓▓▓░░░░░░░░░░░░░░░ | 27.71 | ⚠️ Medium |
| `ai/module_idea_generator.py` | 6 | 3 | 7.6 🟢 | 63.8% ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░ | 24.82 | ⚠️ Medium |
| `refactor/parsers/docstring_parser.py` | 5 | 5 | 5.0 🟢 | 93.6% ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░ | 22.63 | ⚠️ Medium |
| `utils/file_utils.py` | 5 | 5 | 3.89 🟢 | 93.0% ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░ | 21.53 | ⚠️ Medium |
| `refactor/refactor_guard.py` | 0 | 5 | 11.83 🟡 | 60.3% ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░ | 20.13 | ⚠️ Medium |
| `ai/llm_refactor_advisor.py` | 7 | 0 | 5.0 🟢 | 91.7% ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░ | 19.17 | ⚠️ Medium |
| `gui/app.py` | 6 | 2 | 1.0 🟢 | 0.0% ░░░░░░░░░░░░░░░░░░░░ | 18.0 | ⚠️ Medium |


## 📊 Summary Metrics

- Total methods audited: **350**
- 🚫 Methods missing tests: **98**
- 🔺 High-complexity methods (≥10): **28**
- 📚 Methods missing docstrings: **295**
- 🧼 Linter issues detected: **252**




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
- scripts/ai/llm_optimization.py:52: error: Missing type parameters for generic type "Dict"  [type-arg]
- scripts/ai/llm_optimization.py:76: error: Missing type parameters for generic type "dict"  [type-arg]
- scripts/ai/llm_optimization.py:79: error: Missing type parameters for generic type "dict"  [type-arg]
- scripts/ai/llm_optimization.py:80: error: Missing type parameters for generic type "dict"  [type-arg]
- scripts/ai/llm_optimization.py:81: error: Missing type parameters for generic type "dict"  [type-arg]
- scripts/ai/llm_optimization.py:106: error: Missing type parameters for generic type "dict"  [type-arg]
- scripts/ai/llm_optimization.py:132: error: Missing type parameters for generic type "list"  [type-arg]
- scripts/ai/llm_optimization.py:194: error: Need type annotation for "file_prefixes" (hint: "file_prefixes: dict[<type>, <type>] = ...")  [var-annotated]
- scripts/ai/llm_optimization.py:303: error: Missing type parameters for generic type "list"  [type-arg]
- scripts/ai/llm_optimization.py:321: error: Missing type parameters for generic type "list"  [type-arg]

**🧼 Pydocstyle Issues:**
- `_categorise_issues`: D205 — 1 blank line required between summary line and description (found 0)
- `extract_top_issues`: D103 — Missing docstring in public function

**📉 Complexity & Coverage Issues:**
- `_categorise_issues`: Complexity = 9, Coverage = 100.0%
- `summarize_file_data_for_llm`: Complexity = 7, Coverage = 100.0%
- `extract_top_issues`: Complexity = 11, Coverage = 100.0%
- `build_strategic_recommendations_prompt`: Complexity = 15, Coverage = 92.5%
- `compute_severity`: Complexity = 9, Coverage = 100.0%
- `_summarise_offenders`: Complexity = 7, Coverage = 100.0%
- `_format_offender_block`: Complexity = 6, Coverage = 100.0%

**📚 Function Descriptions:**
- `_mean`: None
  - Args: None
  - Returns: None
- `_categorise_issues`: Return a three-line summary that counts how many files trigger each
broad issue category.
Categories
----------
• type errors   (Mypy Errors > 5)
• high complexity (Avg Complexity > 7)
• low coverage  (Avg Coverage % < 60)
  - Args: None
  - Returns: None
- `summarize_file_data_for_llm`: Create the *exact* summary dict expected by legacy callers/tests.
  - Args: None
  - Returns: None
- `extract_top_issues`: None
  - Args: None
  - Returns: None
- `build_refactor_prompt`: Return an LLM prompt focused on refactoring advice for up to *limit* files.
  - Args: None
  - Returns: None
- `build_strategic_recommendations_prompt`: Return a high‑level, strategy‑oriented prompt covering the *limit* worst files.
  - Args: None
  - Returns: None
- `compute_severity`: Compute a weighted severity score for one module.
  - Args: None
  - Returns: None
- `_summarise_offenders`: Aggregate offender list into a human‑readable summary block.
  - Args: None
  - Returns: None
- `_fmt`: None
  - Args: None
  - Returns: None
- `_format_offender_block`: None
  - Args: None
  - Returns: None

</details>

<details>
<summary>🔍 `ai/refactor_advisor_cli.py`</summary>


**❗ MyPy Errors:**
- scripts/ai/refactor_advisor_cli.py:50: error: Function is missing a type annotation for one or more arguments  [no-untyped-def]
- scripts/ai/refactor_advisor_cli.py:90: error: Returning Any from function declared to return "dict[str, Any]"  [no-any-return]
- scripts/ai/refactor_advisor_cli.py:109: error: Incompatible types in assignment (expression has type "list[Any]", variable has type "None")  [assignment]
- scripts/ai/refactor_advisor_cli.py:112: error: Incompatible types in assignment (expression has type "list[dict[str, Any]]", variable has type "None")  [assignment]
- scripts/ai/refactor_advisor_cli.py:114: error: "None" has no attribute "__iter__" (not iterable)  [attr-defined]
- scripts/ai/refactor_advisor_cli.py:141: error: "None" has no attribute "__iter__" (not iterable)  [attr-defined]
- scripts/ai/refactor_advisor_cli.py:150: error: "None" has no attribute "__iter__" (not iterable)  [attr-defined]
- scripts/ai/refactor_advisor_cli.py:162: error: Argument "severity_data" to "build_strategic_recommendations_prompt" has incompatible type "None"; expected "list[dict[str, Any]]"  [arg-type]
- scripts/ai/refactor_advisor_cli.py:198: error: Argument 4 to "summarize_module" has incompatible type "Any | AppConfig"; expected "ConfigManager"  [arg-type]
- scripts/ai/refactor_advisor_cli.py:243: error: Value of type "None" is not indexable  [index]
- scripts/ai/refactor_advisor_cli.py:352: error: "main" does not return a value (it only ever returns None)  [func-returns-value]

**📉 Complexity & Coverage Issues:**
- `UnifiedCodeAssistant.__init__`: Complexity = 3, Coverage = 0.0%
- `UnifiedCodeAssistant._load_report`: Complexity = 4, Coverage = 0.0%
- `UnifiedCodeAssistant.analyze_codebase`: Complexity = 4, Coverage = 0.0%
- `UnifiedCodeAssistant.generate_strategic_recommendations`: Complexity = 7, Coverage = 0.0%
- `UnifiedCodeAssistant.generate_module_summaries`: Complexity = 5, Coverage = 0.0%
- `UnifiedCodeAssistant.answer_query`: Complexity = 2, Coverage = 0.0%
- `UnifiedCodeAssistant._build_contextual_prompt`: Complexity = 3, Coverage = 0.0%
- `chat_mode`: Complexity = 3, Coverage = 0.0%
- `main`: Complexity = 10, Coverage = 0.0%

**📚 Function Descriptions:**
- `__init__`: Initialize the Unified Code Assistant.
  - Args: report_path (str): Path to the code analysis report JSON file
config: Optional configuration object
  - Returns: None
- `_load_report`: Load a JSON report from the specified file path.
  - Args: None
  - Returns: None
- `analyze_codebase`: Perform a comprehensive analysis of the codebase.
  - Args: top_n (int): Number of top files to analyze
path_filter (Optional[str]): Optional filter to focus on specific file paths
  - Returns: Dict[str, Any]: Analysis results including top offenders and severity data
- `generate_strategic_recommendations`: Generate strategic recommendations for improving code quality.
  - Args: limit (int): Maximum number of files to consider
  - Returns: str: Strategic recommendations from the AI assistant
- `generate_module_summaries`: Generate summaries of module functionality based on docstrings.
  - Args: path_filter (Optional[str]): Optional filter to focus on specific file paths
  - Returns: Dict[str, str]: Dictionary mapping file paths to their summaries
- `answer_query`: Answer a user query about the codebase using chain-of-thought processing.
  - Args: query (str): The user's question
  - Returns: str: The assistant's response
- `_build_contextual_prompt`: Build a contextual prompt for answering the user's query.
  - Args: query (str): The user's question
  - Returns: str: A prompt tailored to the query and available analysis data
- `chat_mode`: Run the assistant in interactive chat mode.
  - Args: assistant (UnifiedCodeAssistant): The initialized assistant
  - Returns: None
- `main`: Main entry point for the Unified Code Assistant CLI.
  - Args: None
  - Returns: None

</details>
