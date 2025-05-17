# Docstring Report for `scripts/utils/`


## `scripts\utils\__init__`


## `scripts\utils\file_io`


### Functions

#### load_json_any

Load .json or compressed .json.{gz,bz2,xz} transparently.
Returns {} on missing file for caller-side resilience.

## `scripts\utils\file_utils`


### Functions

#### sanitize_filename

Return *name* stripped of illegal chars and truncated to 100 chars.

#### get_timestamp

Current time as ``YYYY‑MM‑DD_HH‑MM‑SS``.

#### _to_path

Internal: coerce *p* to ``Path`` exactly once.

#### safe_path

Ensure ``path.parent`` exists; return ``Path``.

#### write_json

#### read_json

#### safe_read_json

#### make_backup

#### zip_python_files

Zip all ``.py`` files under *root_dir* (recursively), excluding any directory whose
name appears in *exclude_dirs* (case‑sensitive match against each path part).
If *exclude_dirs* is ``None`` we default to::{.python}
{".venv", "__pycache__", ".git", "node_modules"}

**Arguments:**
output_path: Destination ``.zip`` path (created/overwritten).
root_dir:    Directory to start searching; ``'.'`` by default.
exclude_dirs: Folder names to skip entirely.

## `scripts\utils\git_utils`


git_utils.py
This module provides utility functions for working with Git, including:
- Getting changed Python files compared to a specified branch.
- Running an interactive commit flow to create and push a new branch.
Intended for use in CI workflows and scripts to automate code quality and coverage reporting.


### Functions

#### get_changed_files

Returns a list of changed Python files compared to the specified Git base branch.
Runs 'git diff --name-only' to identify changed files and filters for those ending with '.py'.
Handles compatibility with different Python versions and returns an empty list if the Git command fails.

**Arguments:**
base (str): The Git base branch or commit to compare against. Defaults to 'origin/main'.

**Returns:**
List[str]: A list of changed Python file paths.

#### interactive_commit_flow

Guides the user through an interactive Git commit and push process.
Prompts the user to either push changes to the default branch or create and push to a new branch, handling all Git commands interactively.

**Arguments:**
default_branch (str): The branch to push to by default. Defaults to "main".

**Returns:**
None

#### get_current_branch

Returns the name of the current Git branch as a string.
Executes a Git command to determine the active branch in the local repository.

## `scripts\utils\link_summaries_to_raw_logs`


Module for processing raw logs and injecting entries into correction summaries.
This module provides functionality to flatten raw log entries based on categories and inject those entries into correction summaries.
Functions:
- flatten_raw_entries: Flattens raw log entries for a specified category and subcategory.
- inject_entries_into_summaries: Injects raw log entries into correction summaries based on batch labels.


### Functions

#### flatten_raw_entries

Flatten raw log entries for a given main category and subcategory across all dates,
sorted chronologically.

**Arguments:**
raw_logs (dict): Raw logs as loaded from zephyrus_log.json.
main_cat (str): The main category.
subcat (str): The subcategory.

**Returns:**
list: A list of entries (each is a dict) for the given category/subcategory in chronological order.

#### inject_entries_into_summaries

Injects corresponding raw log entries into each batch of correction summaries based on batch labels.
Loads configuration to determine file paths, reads raw logs and correction summaries, and for each batch in the summaries,
injects the relevant raw entries by extracting their content fields. Updates the summaries file in place.

**Returns:**
None

## `scripts\utils\zip_util`


zip_util.py
This module provides the main entry point for the zip_util utility,
which zips all .py files in a project, excluding specified directories.


### Functions

#### main

Parses command-line arguments to zip all .py files in a project, excluding specified directories.
Calls the internal utility to create the zip archive and logs the output path.