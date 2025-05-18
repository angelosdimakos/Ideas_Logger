# `scripts/refactor`


## `scripts\refactor\__init__`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | The `refactor` module provides tools for analyzing, comparing, and validating Python code refactoring.
Core functionality includes:
- Comparing original and refactored Python modules or directories to detect changes in class and method definitions.
- Analyzing cyclomatic complexity of functions and methods to ensure maintainability.
- Identifying missing or insufficient test coverage for public methods.
- Integrating with code coverage data to enrich analysis results.
- Supporting configuration for complexity thresholds and file/directory ignore patterns.
This module is intended to help developers and teams maintain code quality and test coverage during refactoring processes. |
| Args | — |
| Returns | — |


## `scripts\refactor\ast_extractor`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | ast_extractor.py
This module provides utilities for analyzing Python source files using the AST (Abstract Syntax Tree) to extract class and method information.
Core features include:
- Extracting all classes and their methods from a Python file, including method start and end line numbers.
- Supporting nested class and method extraction.
- Comparing two sets of class methods to identify missing or newly added methods after refactoring.
- Providing a ClassMethodInfo class to encapsulate class and method metadata for further analysis.
Intended for use in code analysis, refactoring tools, and automated quality checks. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `ClassMethodInfo`
Holds information about methods in a single class.
Attributes:
class_name (str): Name of the class.
methods (Dict[str, Tuple[int, int]]): Mapping from method name to a tuple of (start_lineno, end_lineno).

#### `ClassMethodExtractor`
*No description available.*

### 🛠️ Functions
#### `__init__`
Initializes ClassMethodInfo with the class name and an empty methods dictionary.
**Parameters:**
class_name (str): The name of the class.

#### `add_method`
Record a method with its start and end line numbers.
**Parameters:**
name (str): The name of the method.
linenos (Tuple[int, int]): A tuple containing the start and end line numbers of the method.

#### `__repr__`
Returns a string representation of the ClassMethodInfo instance.
**Returns:**
str: A string representation of the class and its methods.

#### `extract_class_methods`
Extracts all classes and their methods from a Python file, including method start and end line numbers.
**Parameters:**
file_path (str): Path to the Python source file.
**Returns:**
List[ClassMethodInfo]: A list of ClassMethodInfo instances containing class and method data.

#### `__init__`
*No description available.*

#### `visit_ClassDef`
*No description available.*

#### `generic_visit`
Visit all child nodes, to catch nested class definitions.

#### `compare_class_methods`
Compare two ClassMethodInfo objects and return which methods are missing in the refactored version and which are newly added.
**Parameters:**
original (ClassMethodInfo): The original class method info.
refactored (ClassMethodInfo): The refactored class method info.
**Returns:**
Dict[str, List[str]]: A dictionary with keys 'missing' and 'added', each mapping to a sorted list of method names.


## `scripts\refactor\merge_audit_reports`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | merge_audit_reports.py – bespoke normalizer
Merges docstring, coverage/complexity, and linting JSON reports into a unified output.
Uses **custom normalization logic per input source** to ensure accurate matching.
Author: Your Name
Version: 1.0 |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `normalize_path`
Normalize any report path by stripping everything up to and including the project 'scripts' directory
and converting to a forward‑slash relative path.
**Parameters:**
path (str): The original file path.
**Returns:**
str: The normalized relative path.

#### `load_and_normalize`
Load JSON and normalize its keys using a common path normalizer.
**Parameters:**
path (Path): The path to the JSON file.
**Returns:**
Dict[str, Any]: A dictionary with normalized keys and their corresponding values.

#### `merge_reports`
Merge docstring, coverage, and linting reports into a single JSON output.
**Parameters:**
doc_path (Path): Path to the docstring JSON file.
cov_path (Path): Path to the coverage JSON file.
lint_path (Path): Path to the linting JSON file.
output_path (Path): Path where the merged output will be saved.

#### `main`
Main entry point for the script.


## `scripts\refactor\method_line_ranges`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | method_line_ranges.py
This module provides utilities for extracting the start and end line numbers of all functions and methods in a Python source file using the AST (Abstract Syntax Tree).
Core features include:
- The MethodRangeVisitor class, which traverses the AST to collect line ranges for top-level functions, class methods, and methods in nested classes.
- The extract_method_line_ranges function, which parses a Python file and returns a dictionary mapping each function or method (as "function" or "Class.method") to its (start_lineno, end_lineno) tuple.
- Handles both synchronous and asynchronous functions, and supports Python versions with or without the end_lineno attribute.
- Designed for use in code analysis, refactoring tools, and coverage mapping.
Intended to facilitate precise mapping of code structure for downstream analysis and tooling. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `MethodRangeVisitor`
Collects start and end line numbers for each function or async method,
keyed by 'ClassName.method' for methods or just 'function' for top-level functions.
Nested classes are also visited.
Attributes:
ranges (Dict[str, Tuple[int, int]]): A dictionary mapping functions or methods to their line ranges.
current_class (Optional[str]): The name of the current class being visited.

### 🛠️ Functions
#### `__init__`
Initializes the MethodRangeVisitor with an empty dictionary for ranges
and a placeholder for the current class name.

#### `visit_ClassDef`
Visits a class definition node and collects line ranges for its methods.
**Parameters:**
node (ast.ClassDef): The class definition node to visit.

#### `visit_FunctionDef`
Visits a function definition node and records its line range.
**Parameters:**
node (ast.FunctionDef): The function definition node to visit.

#### `visit_AsyncFunctionDef`
Visits an asynchronous function definition node and records its line range.
**Parameters:**
node (ast.AsyncFunctionDef): The asynchronous function definition node to visit.

#### `_record_range`
Records the line range for a function or asynchronous function node.
**Parameters:**
node (Union[ast.FunctionDef, ast.AsyncFunctionDef]): The function or asynchronous function node to record.

#### `extract_method_line_ranges`
Parses a Python file and returns a dict mapping each function or method
to its (start_lineno, end_lineno).
**Parameters:**
file_path (str): Path to the Python source file.
**Returns:**
Dict[str, Tuple[int, int]]: A dict mapping functions or methods to their line ranges.
Raises:
FileNotFoundError: If the file cannot be found.
IOError: If the file cannot be read.
SyntaxError: If the file cannot be parsed.


## `scripts\refactor\refactor_guard`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | RefactorGuard: analyse refactors and (optionally) enrich the results with line‑coverage
information coming from a ``.coverage`` SQLite DB or a JSON export produced by Coverage.py.
Adds support for both `.coverage` and `coverage.json` formats. Automatically switches
parsers based on the extension. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `AnalysisError`
Raised when an error occurs during analysis.

#### `RefactorGuard`
Analyse / validate Python refactors.

### 🛠️ Functions
#### `__init__`
*No description available.*

#### `attach_coverage_hits`
*No description available.*

#### `analyze_tests`
*No description available.*

#### `analyze_module`
*No description available.*

#### `_simple_name`
*No description available.*

#### `analyze_directory_recursive`
*No description available.*

#### `print_human_readable`
Print a human-readable summary of the analysis results.


## `scripts\refactor\refactor_guard_cli`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `_ensure_utf8_stdout`
*No description available.*

#### `_parse_args`
*No description available.*

#### `_merge_coverage`
*No description available.*

#### `handle_full_scan`
*No description available.*

#### `handle_single_file`
*No description available.*

#### `main`
*No description available.*


## `scripts\refactor\strictness_analyzer`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Test Coverage Mapper (Strictness Report Version)
Author: Angelos Dimakos
Version: 3.2.0
Loads precomputed strictness analysis and merges it with audit coverage data
into a module-centric report with consistent schema handling.
Usage:
python test_coverage_mapper.py --test-report test_report.json --audit refactor_audit.json --output final_report.json |
| Args | — |
| Returns | — |

### 📦 Classes
#### `ComplexityMetrics`
Model for storing code complexity and test coverage metrics for a single method.

#### `FileAudit`
Model for storing audit data for a specific file.

#### `AuditReport`
Top-level model for the audit report.

#### `StrictnessEntry`
Model for storing test strictness evaluation data.

#### `StrictnessReport`
Top-level model for the strictness report.

#### `MethodOutput`
Standardized output model for method data in the final report.

#### `TestOutput`
Standardized output model for test data in the final report.

#### `ModuleOutput`
Standardized output model for module data in the final report.

#### `FinalReport`
Top-level model for the final merged report.

### 🛠️ Functions
#### `weighted_coverage`
Return overall coverage weighted by each function's lines-of-code.
**Parameters:**
func_dict: Dictionary of function names to ComplexityMetrics
**Returns:**
float: Weighted coverage value between 0.0 and 1.0

#### `get_test_severity`
Compute severity with implicit weighting from coverage.
**Parameters:**
test_entry: StrictnessEntry object with test data.
coverage: Optional coverage value (0.0 to 1.0). If None, no weighting applied.
alpha: Weighting factor for severity vs. coverage.
Higher alpha means severity dominates.
**Returns:**
float: Adjusted severity score.

#### `load_audit_report`
Load the audit report JSON into the Pydantic model.
**Parameters:**
audit_path: Path to the audit report JSON file
**Returns:**
AuditReport: Pydantic model with audit data
Raises:
SystemExit: If file not found or invalid JSON

#### `load_test_report`
Load the precomputed strictness analysis JSON.
**Parameters:**
test_report_path: Path to the test strictness report JSON file
**Returns:**
List[StrictnessEntry]: List of test strictness entries
Raises:
SystemExit: If file not found or invalid JSON

#### `generate_module_report`
*No description available.*

#### `fuzzy_match`
Fuzzy matching with partial ratio preference for looser matching.

#### `validate_report_schema`
*No description available.*

#### `should_assign_test_to_module`
Decide if a test should be assigned to a production module using strict matching.
Prioritizes conventions and imports. Fuzzy matching is a last resort with a high bar.

#### `main`
*No description available.*
