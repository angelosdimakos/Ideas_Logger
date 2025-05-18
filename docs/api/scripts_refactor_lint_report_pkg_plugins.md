# `scripts/refactor/lint_report_pkg/plugins`


## `scripts\refactor\lint_report_pkg\plugins\__init__`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Auto-discover all ToolPlugin subclasses so the orchestrator can `import PLUGINS`. |
| Args | — |
| Returns | — |


## `scripts\refactor\lint_report_pkg\plugins\black`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Black Plugin for Lint Report Package
===============================
This module provides a plugin for the Black code formatter, implementing the ToolPlugin interface.
It includes functionality to run Black on code and parse its output for formatting issues. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `BlackPlugin`
Plugin for the Black code formatter.
Attributes:
name (str): The name of the plugin.
default_report (Path): The default report file path.

### 🛠️ Functions
#### `run`
Run Black in check mode on the scripts directory.
**Returns:**
int: The exit code from the Black command.

#### `parse`
Parse the output report from Black and update the destination dictionary.
**Parameters:**
dst (Dict[str, Dict[str, Any]]): Destination dictionary to update with formatting needs.


## `scripts\refactor\lint_report_pkg\plugins\flake8`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |

### 📦 Classes
#### `Flake8Plugin`
*No description available.*

### 🛠️ Functions
#### `run`
*No description available.*

#### `parse`
*No description available.*


## `scripts\refactor\lint_report_pkg\plugins\mypy`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Mypy Plugin for Lint Report Package
===============================
This module provides a plugin for the MyPy type checker, implementing the ToolPlugin interface.
It includes functionality to run MyPy on code and parse its output for type checking errors. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `MypyPlugin`
Plugin for the MyPy type checker.
Attributes:
name (str): The name of the plugin.
default_report (Path): The default report file path.

### 🛠️ Functions
#### `run`
Run MyPy in strict mode on the scripts directory.
**Returns:**
int: The exit code from the MyPy command.

#### `parse`
Parse the output report from MyPy and update the destination dictionary.
**Parameters:**
dst (Dict[str, Dict[str, Any]]): Destination dictionary to update with type checking errors.


## `scripts\refactor\lint_report_pkg\plugins\pydocstyle`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Pydocstyle Plugin for Lint Report Package
===============================
This module provides a plugin for the pydocstyle tool, implementing the ToolPlugin interface.
It includes functionality to run pydocstyle on code and parse its output for docstring issues. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `PydocstylePlugin`
Plugin for the pydocstyle tool.
Attributes:
name (str): The name of the plugin.
default_report (Path): The default report file path.

### 🛠️ Functions
#### `run`
Execute the pydocstyle tool on the scripts directory.
**Returns:**
int: The exit code from the pydocstyle command.

#### `parse`
Parse pydocstyle output and inject docstring issues grouped by symbol with full detail.
**Parameters:**
dst (Dict[str, Dict[str, Any]]): Destination dictionary to update with docstring issues.
