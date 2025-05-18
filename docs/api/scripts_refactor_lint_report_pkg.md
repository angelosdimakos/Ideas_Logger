# `scripts/refactor/lint_report_pkg`


## `scripts\refactor\lint_report_pkg\__init__`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Plugin-based quality-checker package.
`core.merge_into_refactor_guard()` is the only public entry-point most
code ever needs. |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `register`
Decorator used by each plugin module to register it in the plugin registry.
**Parameters:**
name (str): The name to register the plugin under.
**Returns:**
Callable[[Type], Type]: A decorator that registers the class in the plugin registry.

#### `_inner`
*No description available.*

#### `_discover_plugins`
Discovers and imports all plugin modules in the 'plugins' directory.
This function automatically imports all Python files in the 'plugins' directory,
excluding those that start with an underscore.


## `scripts\refactor\lint_report_pkg\core`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Core Module for Lint Report Package
=====================================
This module provides the base class for tool plugins and functions for plugin discovery.
It includes the abstract base class ToolPlugin that all plugins must implement,
and a utility to access all discovered plugins. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `ToolPlugin`
Abstract base class for tool plugins.
All subclasses must define:
- name: str (unique plugin name)
- default_report: Path (where output is written)
- run(): run the tool
- parse(dst): enrich the lint result dictionary

### 🛠️ Functions
#### `name`
Unique plugin identifier (e.g., 'flake8').

#### `default_report`
Path where the tool writes its report (txt/json/xml).

#### `run`
Execute the tool, writing to `default_report`; return exit code.

#### `parse`
Read `default_report` and update `dst` with findings.

#### `all_plugins`
Return all ToolPlugin instances registered by plugin modules.


## `scripts\refactor\lint_report_pkg\helpers`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Helpers for Lint Report Package
===============================
This module provides utility functions shared by the quality-checker core and plugins.
It includes functions for running commands, printing safely, and reading report files. |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `safe_print`
Print `msg` even on exotic console encodings (swallows UnicodeEncodeError).
**Parameters:**
msg (str): The message to print.

#### `run_cmd`
Run *cmd*, write **combined stdout + stderr** to *output_file* (UTF-8),
and return the subprocess' exit-code.
**Parameters:**
cmd (Sequence[str]): The command to run.
output_file (Union[str, os.PathLike]): The file to write the output to.
**Returns:**
int: The exit code of the command.

#### `read_report`
Return the textual contents of *path* (empty string if the file is missing),
decoding as UTF-8 and falling back to “replace” for any bad bytes.
**Parameters:**
path (Path): The path to the report file.
**Returns:**
str: The contents of the report file.


## `scripts\refactor\lint_report_pkg\lint_report_cli`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Lint Report CLI
===============================
This script enriches a RefactorGuard audit file with linting, coverage, and docstring analysis data.
Key points:
- Zero-setup: If the audit JSON is missing, an empty one is created for plugins to populate.
- No --reports argument: Each plugin runs its own tool and saves its report next to the audit file.
- Optional docstring merge: If a docstring summary JSON is present, it is injected under a top-level "docstrings" key in the audit file.
Typical usage:
$ python lint_report_cli.py --audit refactor_audit.json
$ python lint_report_cli.py --audit refactor_audit.json --docstrings docstring_summary.json |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `enrich_refactor_audit`
Enrich *audit_path* with lint, coverage, and optional docstring data.
Parameters:
----------
audit_path: str
Path to the RefactorGuard audit JSON file.


## `scripts\refactor\lint_report_pkg\path_utils`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Path Utilities for Quality Audit Modules
===============================
This module provides common path helper functions used across quality and audit modules.
It includes functions for normalizing paths relative to the repository root. |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `norm`
Return a *repository-relative* normalized path.
If the file lives outside the repo, fall back to “last-two components”
to avoid collisions yet stay platform-agnostic.
**Parameters:**
p (str | os.PathLike): The path to normalize.
**Returns:**
str: The normalized repository-relative path.


## `scripts\refactor\lint_report_pkg\quality_checker`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Quality Checker for Lint Report Package
=======================================
This module serves as the public API for the lint report package.
It imports all plugins, drives tool execution and parsing, and merges results into the RefactorGuard audit. |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `merge_into_refactor_guard`
Enrich *audit_path* with quality data produced by every plugin.
Parameters
----------
audit_path : str
Path to the RefactorGuard audit JSON file.

#### `merge_reports`
Return merged dict where *b* overrides *a* on duplicate keys.
Parameters
----------
file_a : str
Path to the first JSON file.
file_b : str
Path to the second JSON file.


## `scripts\refactor\lint_report_pkg\quality_registry`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Quality Registry for Lint Report Package
===============================
This module provides functionality to register and run quality plugins.
It includes decorators for registering plugins and a method to invoke all registered plugins. |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `register`
Decorator to register a quality plug-in.
**Parameters:**
func (Plugin): The plugin function to register.
**Returns:**
Plugin: The registered plugin function.

#### `run_all`
Invoke every registered plug-in in order.
**Parameters:**
quality (Dict[str, Dict[str, Any]]): The quality data to pass to plugins.
report_paths (Dict[str, Path]): The paths to the reports.
