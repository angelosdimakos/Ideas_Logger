# `scripts/gui/panels`


## `scripts\gui\panels\__init__`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |


## `scripts\gui\panels\action_panel`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | action_panel.py
This module defines the ActionPanel class, which hosts buttons for actions such as summarizing or rebuilding.
Core features include:
- Creating buttons for summarizing and rebuilding functionality.
- Integrating with the application controller to trigger actions. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `ActionPanel`
ActionPanel hosts buttons for actions such as summarizing or rebuilding.
Attributes:
frame (Optional[ttk.Frame]): The frame containing the action buttons.
summarize_button (Optional[ttk.Button]): The button for summarizing logs.
rebuild_button (Optional[ttk.Button]): The button for rebuilding the tracker.

### 🛠️ Functions
#### `__init__`
Initializes the ActionPanel with the specified parent and controller.
**Parameters:**
parent (tk.Widget): The parent widget for this panel.
controller (Optional[object]): The controller for handling actions. Defaults to None.

#### `initialize_ui`
Creates and packs the action buttons into the panel.
**Returns:**
None

#### `on_summarize`
Trigger the controller's summarize function if available.
**Returns:**
None

#### `on_rebuild`
Trigger the controller's rebuild_tracker function if available.
**Returns:**
None

#### `refresh`
Action panel may not need refreshing, but this hook is here if needed.
**Returns:**
None


## `scripts\gui\panels\coverage_panel`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | coverage_panel.py
This module defines the CoveragePanel class, which displays coverage metrics in a tree view.
Core features include:
- Displaying coverage metrics for various categories.
- Integrating with the application controller to fetch coverage data. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `CoveragePanel`
CoveragePanel displays coverage metrics in a tree view.
Attributes:
frame (Optional[ttk.LabelFrame]): The frame containing the coverage metrics.
tree (Optional[ttk.Treeview]): The tree view for displaying coverage data.

### 🛠️ Functions
#### `__init__`
Initializes the CoveragePanel with the specified parent and controller.
**Parameters:**
parent (tk.Widget): The parent widget for this panel.
controller (Optional[object]): The controller for handling coverage data. Defaults to None.

#### `initialize_ui`
Creates and packs the user interface components for the coverage panel.
**Returns:**
None

#### `refresh`
Refreshes the coverage data displayed in the tree view.
**Returns:**
None


## `scripts\gui\panels\entry_panel`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | entry_panel.py
This module defines the EntryPanel class, which provides the interface for creating new log entries.
Core features include:
- Allowing users to enter and submit new log entries.
- Integrating with the application controller to handle log submission. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `EntryPanel`
EntryPanel provides the interface for creating new log entries.
Attributes:
frame (Optional[ttk.LabelFrame]): The frame containing the entry interface.
entry_text (Optional[tk.Text]): The text widget for entering log content.
submit_button (Optional[ttk.Button]): The button for submitting the log entry.

### 🛠️ Functions
#### `__init__`
Initializes the EntryPanel with the specified parent and controller.
**Parameters:**
parent (tk.Widget): The parent widget for this panel.
controller (Optional[object]): The controller for handling log submissions. Defaults to None.

#### `initialize_ui`
Creates and packs the user interface components for the entry panel.
**Returns:**
None

#### `on_submit`
Handles the submission of a new log entry.
Retrieves text from the text widget and submits it to the controller if available.
**Returns:**
None

#### `refresh`
Clears the text area when refreshing, if needed.
**Returns:**
None


## `scripts\gui\panels\log_panel`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | log_panel.py
This module defines the LogPanel class, which manages the display area for logs.
Core features include:
- Displaying log entries in a scrollable text area.
- Integrating with the application controller to fetch log data. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `LogPanel`
LogPanel manages the display area for logs.
Attributes:
frame (ttk.LabelFrame): The frame containing the log display.
log_display (scrolledtext.ScrolledText): The text area for displaying log entries.

### 🛠️ Functions
#### `__init__`
Initializes the LogPanel with the specified parent and controller.
**Parameters:**
parent (tk.Widget): The parent widget for this panel.
controller (Optional[object]): The controller for handling log data. Defaults to None.

#### `initialize_ui`
Creates and packs the user interface components for the log panel.
**Returns:**
None

#### `refresh`
Refreshes the log display area by fetching logs from the controller.
**Returns:**
None
