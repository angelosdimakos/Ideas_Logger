# `scripts/refactor/complexity`


## `scripts\refactor\complexity\__init__`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |


## `scripts\refactor\complexity\complexity_analyzer`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | complexity_analyzer.py
This module provides utilities for analyzing the cyclomatic complexity of Python functions, methods, and modules using the AST (Abstract Syntax Tree).
Core features include:
- Computing cyclomatic complexity for each function and method in a Python file, including support for nested classes.
- Summing per-function complexities to produce a module-level complexity score.
- Supporting Python 3.10+ match/case syntax in complexity calculations.
- Providing a ComplexityVisitor class for AST traversal and complexity computation.
- Handling syntax and I/O errors gracefully with warnings.
- Deprecated alias for backward compatibility.
Intended for use in code quality analysis, refactoring tools, and CI pipelines to help maintain manageable code complexity. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `ComplexityVisitor`
Visits each top-level function or method definition and computes
its cyclomatic complexity based on decision point nodes.
Nested functions are entirely skipped; nested classes are recursed into.

### 🛠️ Functions
#### `__init__`
Initializes the ComplexityVisitor with an empty dictionary for function scores
and sets the current class name to an empty string.
**Returns:**
None

#### `visit_ClassDef`
Visits a class definition node and computes the complexity of its methods.
**Parameters:**
node (ast.ClassDef): The class definition node to visit.
**Returns:**
None

#### `visit_FunctionDef`
Visits a function definition node and calculates its complexity.
**Parameters:**
node (ast.FunctionDef): The function definition node to visit.
**Returns:**
None

#### `visit_AsyncFunctionDef`
Visits an asynchronous function definition node and calculates its complexity.
**Parameters:**
node (ast.AsyncFunctionDef): The asynchronous function definition node to visit.
**Returns:**
None

#### `_compute_and_record`
Calculate complexity for a function/method node and record it.
**Parameters:**
node (ast.AST): The function or method node to analyze.
**Returns:**
None

#### `count_nodes`
Recursively counts the number of decision nodes in the given AST node.
**Parameters:**
n (ast.AST): The AST node to count decision nodes in.
**Returns:**
int: The number of decision nodes in the given AST node.

#### `get_scores`
Return the computed complexity scores.
**Returns:**
Dict[str, int]: A dictionary mapping function/method names to their complexity scores.

#### `calculate_function_complexity_map`
Parses the given Python file and returns a mapping from function/method
full names to their cyclomatic complexity scores.
**Parameters:**
file_path (str): Path to the Python source file.
**Returns:**
Dict[str, int]: A mapping of function/method names to their complexity scores.
On parse errors, prints a warning and returns an empty dict.

#### `calculate_module_complexity`
Sum all function/method complexities in the module and add 1 overhead.
**Parameters:**
module_path (str): Path to the Python module.
**Returns:**
int: The total complexity score for the module, or -1 on error.

#### `calculate_cyclomatic_complexity_for_module`
Deprecated alias for calculate_module_complexity.
Issues a DeprecationWarning and delegates to calculate_module_complexity.
**Parameters:**
module_path (str): Path to the Python module.
**Returns:**
int: The total complexity score for the module, or -1 on error.


## `scripts\refactor\complexity\complexity_summary`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | complexity_summary.py
This module provides functionality for analyzing code complexity from a JSON audit file.
It reads the audit data, checks for complexity thresholds, and prints a summary report
indicating any methods that exceed the specified complexity limits.
Dependencies:
- json
- sys
- os |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `analyze_complexity`
Analyzes code complexity from a JSON audit file and prints a summary.
Parameters:
file_path (str): Path to the audit JSON file. Defaults to "refactor_audit.json".
max_complexity (int): Maximum allowed complexity before issuing warnings. Defaults to 10.
Exits the process with an error message if the file is missing, empty, or contains invalid JSON.

#### `run_analysis`
Analyzes method complexity across files and prints a summary report.
**Parameters:**
data (Dict[str, Any]): Mapping of file names to complexity information.
max_complexity (Union[int, float]): Threshold for complexity warnings.
use_emoji (bool, optional): If True, prints summary with emojis; otherwise, uses plain text.
Prints:
A summary of methods and files analyzed, and lists methods exceeding the complexity threshold.
Exits the process with an error code if warnings are found and use_emoji is False.
