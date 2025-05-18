# `scripts/utils`


## `scripts\utils\__init__`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |


## `scripts\utils\file_io`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `load_json_any`
Load .json or compressed .json.{gz,bz2,xz} transparently.
Returns {} on missing file for caller-side resilience.


## `scripts\utils\file_utils`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `sanitize_filename`
Return *name* stripped of illegal chars and truncated to 100 chars.

#### `get_timestamp`
Current time as ``YYYY‑MM‑DD_HH‑MM‑SS``.

#### `_to_path`
Internal: coerce *p* to ``Path`` exactly once.

#### `safe_path`
Ensure ``path.parent`` exists; return ``Path``.

#### `write_json`
*No description available.*

#### `read_json`
*No description available.*

#### `safe_read_json`
*No description available.*

#### `make_backup`
*No description available.*

#### `zip_python_files`
Zip all ``.py`` files under *root_dir* (recursively), excluding any directory whose
name appears in *exclude_dirs* (case‑sensitive match against each path part).
If *exclude_dirs* is ``None`` we default to::{.python}
{".venv", "__pycache__", ".git", "node_modules"}
**Parameters:**
output_path: Destination ``.zip`` path (created/overwritten).
root_dir:    Directory to start searching; ``'.'`` by default.
exclude_dirs: Folder names to skip entirely.


## `scripts\utils\git_utils`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | git_utils.py
This module provides utility functions for working with Git, including:
- Getting changed Python files compared to a specified branch.
- Running an interactive commit flow to create and push a new branch.
Intended for use in CI workflows and scripts to automate code quality and coverage reporting. |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `get_changed_files`
Returns a list of changed Python files compared to the specified Git base branch.
Runs 'git diff --name-only' to identify changed files and filters for those ending with '.py'.
Handles compatibility with different Python versions and returns an empty list if the Git command fails.
**Parameters:**
base (str): The Git base branch or commit to compare against. Defaults to 'origin/main'.
**Returns:**
List[str]: A list of changed Python file paths.

#### `interactive_commit_flow`
Guides the user through an interactive Git commit and push process.
Prompts the user to either push changes to the default branch or create and push to a new branch, handling all Git commands interactively.
**Parameters:**
default_branch (str): The branch to push to by default. Defaults to "main".
**Returns:**
None

#### `get_current_branch`
Returns the name of the current Git branch as a string.
Executes a Git command to determine the active branch in the local repository.


## `scripts\utils\link_summaries_to_raw_logs`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Module for processing raw logs and injecting entries into correction summaries.
This module provides functionality to flatten raw log entries based on categories and inject those entries into correction summaries.
Functions:
- flatten_raw_entries: Flattens raw log entries for a specified category and subcategory.
- inject_entries_into_summaries: Injects raw log entries into correction summaries based on batch labels. |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `flatten_raw_entries`
Flatten raw log entries for a given main category and subcategory across all dates,
sorted chronologically.
**Parameters:**
raw_logs (dict): Raw logs as loaded from zephyrus_log.json.
main_cat (str): The main category.
subcat (str): The subcategory.
**Returns:**
list: A list of entries (each is a dict) for the given category/subcategory in chronological order.

#### `inject_entries_into_summaries`
Injects corresponding raw log entries into each batch of correction summaries based on batch labels.
Loads configuration to determine file paths, reads raw logs and correction summaries, and for each batch in the summaries,
injects the relevant raw entries by extracting their content fields. Updates the summaries file in place.
**Returns:**
None


## `scripts\utils\zip_util`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | zip_util.py
This module provides the main entry point for the zip_util utility,
which zips all .py files in a project, excluding specified directories. |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `main`
Parses command-line arguments to zip all .py files in a project, excluding specified directories.
Calls the internal utility to create the zip archive and logs the output path.
