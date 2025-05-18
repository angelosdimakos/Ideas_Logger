# `scripts/refactor/parsers`


## `scripts\refactor\parsers\__init__`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |


## `scripts\refactor\parsers\docstring_parser`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Docstring Parser
===============================
This module scans a Python project directory for missing or partial docstrings.
It outputs structured JSON and markdown-style reports with description, args, and return sections.
Also supports generating MkDocs-compatible markdown files. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `DocstringAnalyzer`
*No description available.*

#### `DocstringAuditCLI`
*No description available.*

### 🛠️ Functions
#### `split_docstring_sections`
Split a docstring into its sections: description, args, and returns.
**Parameters:**
docstring (Optional[str]): The docstring to split.
**Returns:**
Dict[str, Optional[str]]: A dictionary containing the sections: description, args, and returns.

#### `__init__`
Initialize the DocstringAnalyzer with directories to exclude.
**Parameters:**
exclude_dirs (List[str]): A list of directories to exclude from analysis.

#### `should_exclude`
Determine if a given path should be excluded from analysis.
**Parameters:**
path (Path): The path to check.
**Returns:**
bool: True if the path should be excluded, False otherwise.

#### `extract_docstrings`
Extract docstrings from a Python file, recursively.
**Parameters:**
file_path (Path): The path to the Python file to analyze.
**Returns:**
Dict[str, Any]: A dictionary containing docstring information.

#### `visit_node`
*No description available.*

#### `analyze_directory`
Analyze all Python files in the given directory and its subdirectories.
**Parameters:**
root (Path): The path to the directory to analyze.
**Returns:**
Dict[str, Dict[str, Any]]: A dictionary with normalized file paths as keys and
dictionaries with docstring information as values.

#### `generate_mkdocs_markdown`
Generate MkDocs-compatible markdown files from docstring analysis results.
**Parameters:**
results (Dict[str, Dict[str, Any]]): Docstring analysis results.
output_dir (Path): Directory to write markdown files to.

#### `_generate_module_markdown`
Generate markdown documentation for a single module.
**Parameters:**
file_path (str): Path to the module.
docstrings (Dict[str, Any]): Docstring information for the module.
output_path (Path): Path to write markdown file to.

#### `__init__`
Initialize the command-line interface for the docstring audit.

#### `parse_args`
Parse command-line arguments.
**Returns:**
argparse.Namespace: The parsed command-line arguments.

#### `run`
Run the docstring audit.


## `scripts\refactor\parsers\json_coverage_parser`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `_load_files`
Return the `files` section with all keys normalised to POSIX paths.

#### `_best_suffix_match`
Find the file-entry whose tail components best match *requested*.
Returns the matching coverage dict or **None** if nothing plausible found.

#### `_fully_uncovered`
Return a coverage dict that marks every method as 0 % covered.

#### `_coverage_from_summary`
Extract coverage %, hits and missing lines list from a summary block.

#### `_coverage_from_executed`
*No description available.*

#### `parse_json_coverage`
Return per-method coverage data for *filepath* based on a `coverage.py`
JSON (v5) report previously converted with ``coverage json``.
