# Docstring Report for `scripts/refactor/lint_report_pkg/plugins/`


## `scripts\refactor\lint_report_pkg\plugins\__init__`


Auto-discover all ToolPlugin subclasses so the orchestrator can `import PLUGINS`.


## `scripts\refactor\lint_report_pkg\plugins\black`


Black Plugin for Lint Report Package
===============================
This module provides a plugin for the Black code formatter, implementing the ToolPlugin interface.
It includes functionality to run Black on code and parse its output for formatting issues.


### Classes

#### BlackPlugin

Plugin for the Black code formatter.
Attributes:
name (str): The name of the plugin.
default_report (Path): The default report file path.

### Functions

#### run

Run Black in check mode on the scripts directory.

**Returns:**
int: The exit code from the Black command.

#### parse

Parse the output report from Black and update the destination dictionary.

**Arguments:**
dst (Dict[str, Dict[str, Any]]): Destination dictionary to update with formatting needs.

## `scripts\refactor\lint_report_pkg\plugins\flake8`


### Classes

#### Flake8Plugin

### Functions

#### run

#### parse

## `scripts\refactor\lint_report_pkg\plugins\mypy`


Mypy Plugin for Lint Report Package
===============================
This module provides a plugin for the MyPy type checker, implementing the ToolPlugin interface.
It includes functionality to run MyPy on code and parse its output for type checking errors.


### Classes

#### MypyPlugin

Plugin for the MyPy type checker.
Attributes:
name (str): The name of the plugin.
default_report (Path): The default report file path.

### Functions

#### run

Run MyPy in strict mode on the scripts directory.

**Returns:**
int: The exit code from the MyPy command.

#### parse

Parse the output report from MyPy and update the destination dictionary.

**Arguments:**
dst (Dict[str, Dict[str, Any]]): Destination dictionary to update with type checking errors.

## `scripts\refactor\lint_report_pkg\plugins\pydocstyle`


Pydocstyle Plugin for Lint Report Package
===============================
This module provides a plugin for the pydocstyle tool, implementing the ToolPlugin interface.
It includes functionality to run pydocstyle on code and parse its output for docstring issues.


### Classes

#### PydocstylePlugin

Plugin for the pydocstyle tool.
Attributes:
name (str): The name of the plugin.
default_report (Path): The default report file path.

### Functions

#### run

Execute the pydocstyle tool on the scripts directory.

**Returns:**
int: The exit code from the pydocstyle command.

#### parse

Parse pydocstyle output and inject docstring issues grouped by symbol with full detail.

**Arguments:**
dst (Dict[str, Dict[str, Any]]): Destination dictionary to update with docstring issues.