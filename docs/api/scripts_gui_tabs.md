# `scripts/gui/tabs`


## `scripts\gui\tabs\__init__`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |


## `scripts\gui\tabs\main_tab`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | main_tab.py
This module defines the MainTab class, which is the primary tab for logging functionality in the application.
Core features include:
- Organizing child panels for logging, coverage, entry, and actions.
- Refreshing child panels when the tab becomes active. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `MainTab`
MainTab is the primary tab for logging functionality.
It organizes child panels: LogPanel, CoveragePanel, EntryPanel, and ActionPanel.
Attributes:
log_panel (LogPanel): The panel for displaying logs.
coverage_panel (CoveragePanel): The panel for displaying coverage information.
entry_panel (EntryPanel): The panel for entering new log entries.
action_panel (ActionPanel): The panel for action buttons.

### 🛠️ Functions
#### `setup_tab`
Create a container frame to hold the child panels and pack them into the tab.
**Returns:**
None

#### `on_show`
Called when the MainTab becomes active. This refreshes all child panels.
**Returns:**
None
