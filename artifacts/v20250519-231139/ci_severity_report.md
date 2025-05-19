# 📊 CI Code Quality Audit Report

## Executive Summary

| Metric                     | Value    | Visual |
|----------------------------|----------|--------|
| Files analyzed             | `183`    |     |
| Files with issues          | `80`     |     |
| **Top risk file**          | `refactor/parsers/docstring_parser.py` |     |
| Methods audited            | `435`    |     |
| Missing tests              | `409`    | ▓░░░░░░░░░░░░░░░░░░░ 🔴 |
| Missing docstrings         | `106`    | ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░ 🟡 |
| Linter issues              | `324`    | ▓▓▓▓▓░░░░░░░░░░░░░░░ 🔴 |



## 🧨 Severity Rankings (Top 10)

| File | 🔣 Mypy | 🧼 Lint | 📉 Cx | 📊 Cov | 📈 Score | 🎯 Priority |
|------|--------|--------|------|--------|----------|-------------|
| `refactor/parsers/docstring_parser.py` | 9 | 7 | 5.42 🟢 | 0.0% ░░░░░░░░░░░░░░░░░░░░ | 35.92 | 🔥 High |
| `experimental/ci/ci_router.py` | 13 | 1 | 6.08 🟢 | 0.3% ░░░░░░░░░░░░░░░░░░░░ | 35.58 | 🔥 High |
| `doc_generation/quality_doc_generation.py` | 10 | 1 | 11.5 🟡 | 0.0% ░░░░░░░░░░░░░░░░░░░░ | 35.0 | 🔥 High |
| `kg/modules/visualization.py` | 13 | 1 | 4.62 🟢 | 0.0% ░░░░░░░░░░░░░░░░░░░░ | 34.12 | 🔥 High |
| `ai/llm_optimization.py` | 10 | 2 | 7.33 🟢 | 0.0% ░░░░░░░░░░░░░░░░░░░░ | 32.33 | 🔥 High |
| `gui/gui_helpers.py` | 9 | 4 | 2.25 🟢 | 0.0% ░░░░░░░░░░░░░░░░░░░░ | 28.25 | ⚠️ Medium |
| `unified_code_assistant/prompt_builder.py` | 5 | 2 | 9.5 🟢 | 0.0% ░░░░░░░░░░░░░░░░░░░░ | 24.5 | ⚠️ Medium |
| `utils/file_utils.py` | 5 | 5 | 3.89 🟢 | 0.0% ░░░░░░░░░░░░░░░░░░░░ | 23.39 | ⚠️ Medium |
| `ai/module_idea_generator.py` | 6 | 1 | 7.6 🟢 | 0.0% ░░░░░░░░░░░░░░░░░░░░ | 23.1 | ⚠️ Medium |
| `experimental/ci/adapters/merge_reports_router.py` | 7 | 1 | 5.56 🟢 | 0.3% ░░░░░░░░░░░░░░░░░░░░ | 23.05 | ⚠️ Medium |


## 📊 Summary Metrics

- Total methods audited: **435**
- 🚫 Methods missing tests: **409**
- 🔺 High-complexity methods (≥10): **44**
- 📚 Methods missing docstrings: **106**
- 🧼 Linter issues detected: **324**




## 🔎 Top Offenders: Detailed Analysis

<details>
<summary>🔍 `refactor/parsers/docstring_parser.py`</summary>


**❗ MyPy Errors:**
- scripts/refactor/parsers/docstring_parser.py:75: error: Function is missing a type annotation  [no-untyped-def]
- scripts/refactor/parsers/docstring_parser.py:79: error: Call to untyped function "arg_str" in typed context  [no-untyped-call]
- scripts/refactor/parsers/docstring_parser.py:80: error: Call to untyped function "arg_str" in typed context  [no-untyped-call]
- scripts/refactor/parsers/docstring_parser.py:83: error: Call to untyped function "arg_str" in typed context  [no-untyped-call]
- scripts/refactor/parsers/docstring_parser.py:152: error: Function is missing a type annotation  [no-untyped-def]
- scripts/refactor/parsers/docstring_parser.py:154: error: "Collection[str]" has no attribute "append"  [attr-defined]
- scripts/refactor/parsers/docstring_parser.py:156: error: "Collection[str]" has no attribute "append"  [attr-defined]
- scripts/refactor/parsers/docstring_parser.py:158: error: Call to untyped function "visit" in typed context  [no-untyped-call]
- scripts/refactor/parsers/docstring_parser.py:160: error: Call to untyped function "visit" in typed context  [no-untyped-call]

**🧼 Pydocstyle Issues:**
- `DocstringAnalyzer`: D101 — Missing docstring in public class
- `__init__`: D107 — Missing docstring in __init__
- `__init__`: D200 — One-line docstring should fit on one line with quotes (found 3)
- `should_exclude`: D102 — Missing docstring in public method
- `analyze_directory`: D102 — Missing docstring in public method
- `DocstringAuditCLI`: D101 — Missing docstring in public class
- `run`: D200 — One-line docstring should fit on one line with quotes (found 3)

**📉 Complexity & Coverage Issues:**
- `split_docstring_sections`: Complexity = 9, Coverage = 0.0%
- `DocstringAnalyzer.__init__`: Complexity = 1, Coverage = 0.0%
- `DocstringAnalyzer.should_exclude`: Complexity = 1, Coverage = 0.0%
- `DocstringAnalyzer._format_args`: Complexity = 9, Coverage = 0.0%
- `DocstringAnalyzer._get_return_type`: Complexity = 4, Coverage = 0.0%
- `DocstringAnalyzer._process_function`: Complexity = 1, Coverage = 0.0%
- `DocstringAnalyzer._process_class`: Complexity = 5, Coverage = 0.0%
- `DocstringAnalyzer.extract_docstrings`: Complexity = 8, Coverage = 0.0%
- `DocstringAnalyzer.analyze_directory`: Complexity = 7, Coverage = 0.0%
- `DocstringAuditCLI.__init__`: Complexity = 1, Coverage = 0.0%
- `DocstringAuditCLI.parse_args`: Complexity = 1, Coverage = 0.0%
- `DocstringAuditCLI.run`: Complexity = 18, Coverage = 0.0%

**📚 Function Descriptions:**
- `split_docstring_sections`: Split a docstring into its sections: description, args, and returns.
  - Args: ['docstring: Optional[str]']
  - Returns: Dict[str, Optional[str]]
- `__init__`: None
  - Args: ['self: Any', 'exclude_dirs: List[str]']
  - Returns: None
- `should_exclude`: None
  - Args: ['self: Any', 'path: Path']
  - Returns: bool
- `_format_args`: None
  - Args: ['self: Any', 'args_node: ast.arguments']
  - Returns: List[str]
- `arg_str`: None
  - Args: ['arg: Any']
  - Returns: Any
- `_get_return_type`: None
  - Args: ['self: Any', 'func_node: ast.FunctionDef']
  - Returns: str
- `_process_function`: None
  - Args: ['self: Any', 'node: ast.FunctionDef']
  - Returns: Dict[str, Any]
- `_process_class`: None
  - Args: ['self: Any', 'node: ast.ClassDef']
  - Returns: Dict[str, Any]
- `extract_docstrings`: Extract docstrings, args, and return types from a Python file using AST.
Always returns a consistent structure even on parse failure.
  - Args: ['self: Any', 'file_path: Path']
  - Returns: Dict[str, Any]
- `visit`: None
  - Args: ['node: Any']
  - Returns: Any
- `analyze_directory`: None
  - Args: ['self: Any', 'root: Path']
  - Returns: Dict[str, Dict[str, Any]]
- `__init__`: Initialize the command-line interface for the docstring audit.
  - Args: ['self: Any']
  - Returns: None
- `parse_args`: Parse command-line arguments.
  - Args: ['self: Any']
  - Returns: argparse.Namespace
- `run`: Run the docstring audit.
  - Args: ['self: Any']
  - Returns: None

</details>

<details>
<summary>🔍 `experimental/ci/ci_router.py`</summary>


**❗ MyPy Errors:**
- scripts/experimental/ci/ci_router.py:68: error: Missing type parameters for generic type "Dict"  [type-arg]
- scripts/experimental/ci/ci_router.py:126: error: Incompatible types in assignment (expression has type "str", variable has type "CITask")  [assignment]
- scripts/experimental/ci/ci_router.py:127: error: No overload variant of "get" of "dict" matches argument types "CITask", "list[Never]"  [call-overload]
- scripts/experimental/ci/ci_router.py:207: error: Missing type parameters for generic type "Dict"  [type-arg]
- scripts/experimental/ci/ci_router.py:231: error: Missing type parameters for generic type "Dict"  [type-arg]
- scripts/experimental/ci/ci_router.py:241: error: Need type annotation for "result"  [var-annotated]
- scripts/experimental/ci/ci_router.py:262: error: Incompatible types in assignment (expression has type "int", target has type "list[Any] | str | None")  [assignment]
- scripts/experimental/ci/ci_router.py:268: error: Item "str" of "list[Any] | str | None" has no attribute "append"  [union-attr]
- scripts/experimental/ci/ci_router.py:268: error: Item "None" of "list[Any] | str | None" has no attribute "append"  [union-attr]
- scripts/experimental/ci/ci_router.py:276: error: Missing type parameters for generic type "Dict"  [type-arg]
- scripts/experimental/ci/ci_router.py:301: error: Missing type parameters for generic type "Dict"  [type-arg]
- scripts/experimental/ci/ci_router.py:432: error: Function is missing a return type annotation  [no-untyped-def]
- scripts/experimental/ci/ci_router.py:485: error: Call to untyped function "main" in typed context  [no-untyped-call]

**🧼 Pydocstyle Issues:**
- `CIRouter`: D200 — One-line docstring should fit on one line with quotes (found 3)

**📉 Complexity & Coverage Issues:**
- `CIRouter.__init__`: Complexity = 1, Coverage = 0.0%
- `CIRouter.detect_changed_files`: Complexity = 7, Coverage = 0.0%
- `CIRouter.map_files_to_tasks`: Complexity = 8, Coverage = 3.1%
- `CIRouter._get_tasks_for_file`: Complexity = 8, Coverage = 0.0%
- `CIRouter._match_pattern`: Complexity = 12, Coverage = 0.0%
- `CIRouter._add_dependent_tasks`: Complexity = 5, Coverage = 0.0%
- `CIRouter.run_tasks`: Complexity = 4, Coverage = 0.0%
- `CIRouter._run_task`: Complexity = 5, Coverage = 0.0%
- `CIRouter.generate_report`: Complexity = 6, Coverage = 0.0%
- `CIRouter._generate_markdown_report`: Complexity = 9, Coverage = 0.0%
- `create_default_config`: Complexity = 1, Coverage = 0.0%
- `main`: Complexity = 7, Coverage = 0.0%

**📚 Function Descriptions:**
- `__init__`: Initialize the CI router with the provided configuration.
  - Args: ['self: Any', 'config: RouterConfig']
  - Returns: Any
- `detect_changed_files`: Detect changed files using git diff against the specified base branch.
  - Args: ['self: Any', 'base_branch: Optional[str]']
  - Returns: List[str]
- `map_files_to_tasks`: Map changed files to the CI tasks they affect.
  - Args: ['self: Any']
  - Returns: Dict[str, List[str]]
- `_get_tasks_for_file`: Get the tasks affected by changes to a specific file.
  - Args: ['self: Any', 'file_path: str']
  - Returns: List[str]
- `_match_pattern`: Check if a file path matches a pattern.
  - Args: ['self: Any', 'file_path: str', 'pattern: str']
  - Returns: bool
- `_add_dependent_tasks`: Add required dependent tasks to the tasks_to_run set.
  - Args: ['self: Any']
  - Returns: None
- `run_tasks`: Run all selected CI tasks.
  - Args: ['self: Any']
  - Returns: Dict[str, Dict]
- `_run_task`: Run a single CI task.
  - Args: ['self: Any', 'task: CITask']
  - Returns: Dict
- `generate_report`: Generate a comprehensive report of the CI run.
  - Args: ['self: Any']
  - Returns: Dict
- `_generate_markdown_report`: Generate a markdown report from the CI summary.
  - Args: ['self: Any', 'summary: Dict']
  - Returns: None
- `create_default_config`: Create the default router configuration based on the project structure.
  - Args: []
  - Returns: RouterConfig
- `main`: Main entry point for the CI Router.
  - Args: []
  - Returns: Any

</details>

<details>
<summary>🔍 `doc_generation/quality_doc_generation.py`</summary>


**❗ MyPy Errors:**
- scripts/doc_generation/quality_doc_generation.py:29: error: Function is missing a return type annotation  [no-untyped-def]
- scripts/doc_generation/quality_doc_generation.py:29: error: Missing type parameters for generic type "dict"  [type-arg]
- scripts/doc_generation/quality_doc_generation.py:38: error: Need type annotation for "grouped"  [var-annotated]
- scripts/doc_generation/quality_doc_generation.py:64: error: "Collection[str]" has no attribute "append"  [attr-defined]
- scripts/doc_generation/quality_doc_generation.py:79: error: Unsupported target for indexed assignment ("Collection[str]")  [index]
- scripts/doc_generation/quality_doc_generation.py:88: error: "Collection[str]" has no attribute "append"  [attr-defined]
- scripts/doc_generation/quality_doc_generation.py:94: error: Value of type "Collection[str]" is not indexable  [index]
- scripts/doc_generation/quality_doc_generation.py:94: error: Unsupported target for indexed assignment ("Collection[str]")  [index]
- scripts/doc_generation/quality_doc_generation.py:114: error: Function is missing a return type annotation  [no-untyped-def]
- scripts/doc_generation/quality_doc_generation.py:138: error: Call to untyped function "main" in typed context  [no-untyped-call]

**🧼 Pydocstyle Issues:**
- `main`: D103 — Missing docstring in public function

**📉 Complexity & Coverage Issues:**
- `generate_split_reports`: Complexity = 19, Coverage = 0.0%
- `main`: Complexity = 4, Coverage = 0.0%

**📚 Function Descriptions:**
- `generate_split_reports`: Generate split code quality documentation files.
  - Args: ['report_data: dict', 'output_dir: Path', 'verbose: bool']
  - Returns: Any
- `main`: None
  - Args: []
  - Returns: Any

</details>
