# Docstring Report for `scripts/refactor/parsers/`


## `scripts\refactor\parsers\__init__`


## `scripts\refactor\parsers\docstring_parser`


Docstring Parser
===============================
This module scans a Python project directory for missing or partial docstrings.
It outputs structured JSON and markdown-style reports with description, args, and return sections.
Also supports generating MkDocs-compatible markdown files.


### Classes

#### DocstringAnalyzer

#### DocstringAuditCLI

### Functions

#### split_docstring_sections

Split a docstring into its sections: description, args, and returns.

**Arguments:**
docstring (Optional[str]): The docstring to split.

**Returns:**
Dict[str, Optional[str]]: A dictionary containing the sections: description, args, and returns.

#### __init__

Initialize the DocstringAnalyzer with directories to exclude.

**Arguments:**
exclude_dirs (List[str]): A list of directories to exclude from analysis.

#### should_exclude

Determine if a given path should be excluded from analysis.

**Arguments:**
path (Path): The path to check.

**Returns:**
bool: True if the path should be excluded, False otherwise.

#### extract_docstrings

Extract docstrings from a Python file, recursively.

**Arguments:**
file_path (Path): The path to the Python file to analyze.

**Returns:**
Dict[str, Any]: A dictionary containing docstring information.

#### visit_node

#### analyze_directory

Analyze all Python files in the given directory and its subdirectories.

**Arguments:**
root (Path): The path to the directory to analyze.

**Returns:**
Dict[str, Dict[str, Any]]: A dictionary with normalized file paths as keys and
dictionaries with docstring information as values.

#### generate_mkdocs_markdown

Generate MkDocs-compatible markdown files from docstring analysis results.

**Arguments:**
results (Dict[str, Dict[str, Any]]): Docstring analysis results.
output_dir (Path): Directory to write markdown files to.

#### generate_mkdocs_markdown

Generate MkDocs-compatible markdown files from docstring analysis results.
Now mirrors the structure of quality and coverage reports.

#### __init__

Initialize the command-line interface for the docstring audit.

#### parse_args

Parse command-line arguments.

**Returns:**
argparse.Namespace: The parsed command-line arguments.

#### run

Run the docstring audit.

## `scripts\refactor\parsers\json_coverage_parser`


### Functions

#### _load_files

Return the `files` section with all keys normalised to POSIX paths.

#### _best_suffix_match

Find the file-entry whose tail components best match *requested*.
Returns the matching coverage dict or **None** if nothing plausible found.

#### _fully_uncovered

Return a coverage dict that marks every method as 0 % covered.

#### _coverage_from_summary

Extract coverage %, hits and missing lines list from a summary block.

#### _coverage_from_executed

#### parse_json_coverage

Return per-method coverage data for *filepath* based on a `coverage.py`
JSON (v5) report previously converted with ``coverage json``.