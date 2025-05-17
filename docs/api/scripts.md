# Docstring Report for `scripts/`


## `scripts\__init__`


## `scripts\dev_commit`


### Functions

#### get_current_branch

Returns the name of the current Git branch.

**Returns:**
str: The current branch name.

#### get_modified_files

Returns a list of files modified (but not yet committed) in the current Git working directory.

**Returns:**
list[str]: List of modified file paths.

#### is_valid_branch_name

Checks if the provided branch name is valid according to Git naming conventions.

**Arguments:**
name (str): The branch name to validate.

**Returns:**
bool: True if the branch name is valid, False otherwise.

#### generate_suggested_branch_name

Generates a suggested branch name based on modified files and the current date.

**Returns:**
str: A suggested branch name in the format 'fix/<keywords>-<date>'.

#### switch_to_new_branch

Prompts the user to create and switch to a new Git branch.
Suggests a branch name based on modified files and validates user input.
Exits the script if the branch name is invalid or if Git fails to create or push the branch.

## `scripts\main`


main.py
This module provides the entrypoint for the Zephyrus Logger application.
It initializes the logging system, loads the application configuration, and
sets up the GUI or CLI depending on the mode specified in the configuration.
Key features include:
- Logging setup
- Config loading
- GUI or CLI setup
- Controller and GUI instance initialization
This is the main entrypoint for the Zephyrus Logger application.


### Functions

#### bootstrap

Bootstraps the Zephyrus Logger application.

**Arguments:**
start_gui (bool, optional): Whether to launch the GUI. Defaults to True.

**Returns:**
Tuple[GUIController, ZephyrusLoggerGUI | None]: The controller and GUI instance (None if headless).
Raises:
Exception: Propagates any fatal errors encountered during initialization.

## `scripts\paths`


### Classes

#### ZephyrusPaths

Dataclass for managing and resolving all Zephyrus project file and directory paths.
Provides methods to construct absolute paths for logs, exports, configuration, and vector store files,
with support for test mode path overrides based on the loaded configuration.

### Functions

#### _resolve_path

Resolve an absolute Path for a given config key, falling back to the provided default if the key is missing.

**Arguments:**
config (dict): The configuration dictionary.
key (str): The configuration key to look up.
default (Any): The default value to use if the key is not present.

**Returns:**
Path: The resolved absolute path.

#### from_config

Constructs a ZephyrusPaths instance by resolving all required file and directory paths from the loaded configuration.
Automatically applies test mode path overrides if enabled.

**Arguments:**
script_dir (Path): The directory containing the current script.

**Returns:**
ZephyrusPaths: An instance with all paths resolved according to the configuration.