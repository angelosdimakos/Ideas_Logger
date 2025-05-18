# `scripts/gui`


## `scripts\gui\__init__`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |


## `scripts\gui\gui`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | gui.py
This module provides the ZephyrusLoggerGUI class, which implements a graphical user interface
for the Zephyrus Ideas Logger application using the tkinter library. It manages the GUI components,
user interactions, and integrates logging functionality. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `ZephyrusLoggerGUI`
A class to represent the Zephyrus Ideas Logger GUI.
This class initializes the GUI components and handles user interactions.
Attributes:
controller (GUIController): The controller for managing the application's logic.
logger (logging.Logger): Logger for tracking GUI events and actions.
config (dict): Configuration settings loaded from the config file.
category_structure (dict): Structure of categories for the GUI.
root (tk.Tk): The main window of the GUI application.

### 🛠️ Functions
#### `__init__`
Initialize the ZephyrusLoggerGUI.
**Parameters:**
controller (GUIController): The controller for managing the application's logic.

#### `_setup_gui_logging`
Set up the logging for the GUI.
This method configures the logging handler to display logs in the GUI.

#### `_build_widgets`
Build the GUI widgets and layout.
This method creates and arranges the GUI components, such as frames and buttons.

#### `_update_coverage_display`
Update the coverage display.
This method retrieves the coverage data from the controller and updates the coverage display.

#### `_populate_category_dropdown`
Populate the category dropdown menu.
This method retrieves the categories from the controller and populates the dropdown menu.

#### `_update_main_category`
Update the main category.
This method updates the main category and subcategory dropdown menus.
**Parameters:**
new_main (str): The new main category.

#### `_log_entry`
Log a new entry.
This method logs a new entry based on the user's input.

#### `_manual_summarize`
Manually summarize the logs.
This method generates a summary of the logs based on the user's input.

#### `_search_summary`
Search for summaries.
This method searches for summaries based on the user's input.

#### `_search_raw`
Search for raw logs.
This method searches for raw logs based on the user's input.

#### `_rebuild_tracker`
Rebuild the tracker.
This method rebuilds the tracker based on the user's input.

#### `_show_coverage`
Show the coverage.
This method displays the coverage data.

#### `run`
Run the GUI application.
This method starts the GUI event loop.


## `scripts\gui\gui_controller`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | gui_controller.py
This module provides the GUIController class for managing the interaction between the GUI
and the logging core of the Zephyrus Logger application. It handles the initialization of
the logger core and facilitates logging entries through the GUI.
Dependencies:
- os
- logging
- scripts.core.core.ZephyrusLoggerCore |
| Args | — |
| Returns | — |

### 📦 Classes
#### `GUIController`
GUIController manages the interaction between the GUI and the logging core.
Attributes:
core (ZephyrusLoggerCore): The instance of the ZephyrusLoggerCore used for logging.

### 🛠️ Functions
#### `__init__`
Initializes the GUIController with the given logger core or initializes a new one.
**Parameters:**
logger_core (Optional[ZephyrusLoggerCore]): The logger core instance. If None, a new instance will be created.
script_dir (Optional[str]): The directory of the script. Defaults to the current working directory.

#### `log_entry`
Logs an entry with the specified main category, subcategory, and text.
**Parameters:**
main (str): The main category of the log entry.
sub (str): The subcategory of the log entry.
text (str): The text content of the log entry.
**Returns:**
Any: The result of the logging operation.

#### `force_summarize_all`
Forces the summarization of all logs.
**Returns:**
Any: The result of the summarization operation.

#### `search_summaries`
Searches for summaries matching the given query.
**Parameters:**
query (str): The search query.
**Returns:**
Any: The result of the search operation.

#### `search_raw_logs`
Searches for raw logs matching the given query.
**Parameters:**
query (str): The search query.
**Returns:**
Any: The result of the search operation.

#### `rebuild_tracker`
Rebuilds the summary tracker and returns True if successful, False otherwise.

#### `get_tracker_status`
Returns a user-friendly status string of the summary tracker.

#### `get_coverage_data`
Retrieves coverage data from the tracker for the UI heatmap.

#### `get_logs`
Retrieves the contents of the plain text log file as a string.


## `scripts\gui\gui_helpers`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | gui_helpers.py
This module provides utility functions for building and customizing the
Zephyrus Logger application's graphical user interface (GUI).
Core features include:
- Validating user input for logging and searching.
- Creating and customizing Tkinter widgets (e.g. scrolled text, buttons).
- Displaying alerts and messages using Tkinter's messagebox module.
- Utility functions for reading and writing JSON files.
Intended to provide a set of reusable functions for the GUI components of
the Zephyrus Logger application. |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `validate_log_input`
Returns False if the input is empty, None, or just whitespace.
Logs a warning if invalid.

#### `get_current_date`
Returns the current date as a string in 'YYYY-MM-DD' format.
:return: Current date as a string.
:rtype: str

#### `get_current_timestamp`
Returns the current date and time as a formatted string (YYYY-MM-DD HH:MM:SS).

#### `clear_text_input`
Clears all text from the given Tkinter text entry widget.
**Parameters:**
entry_widget: The Tkinter text widget to be cleared.

#### `update_status_label`
Update the text and foreground color of a Tkinter label widget.
**Parameters:**
label (tk.Label): The label widget to update.
message (str): The text to display on the label.
color (str, optional): The text color. Defaults to "blue".

#### `get_selected_option`
Returns the currently selected option from a Tkinter menu variable, or a default value if none is selected.
**Parameters:**
menu_var: A Tkinter variable associated with a menu widget.
default (str, optional): The value to return if no option is selected. Defaults to "General".
**Returns:**
str: The selected option or the default value.

#### `append_log_entry`
Appends a log entry with a timestamp and content to the specified log file, organizing entries by date, category, and subcategory.
**Parameters:**
log_file (str): Path to the JSON log file.
date (str): Date key for the log entry (YYYY-MM-DD).
category (str): Category under which to store the entry.
subcategory (str): Subcategory under the category.
entry_text (str): The content of the log entry.

#### `get_category_options`
Retrieves a list of category names from a JSON file at the given path.
**Parameters:**
categories_json_path (str): Path to the JSON file containing categories.
**Returns:**
list: List of category names, or an empty list if reading fails.

#### `create_status_label`
Create and pack a status label widget in the given root window.
**Parameters:**
root: The parent Tkinter widget.
status_var: A Tkinter StringVar to display as the label's text.
**Returns:**
The created Label widget.

#### `create_log_frame`
Creates and returns a disabled scrolled text widget within a frame for logging purposes in a Tkinter GUI.
**Parameters:**
root: The parent Tkinter widget.
**Returns:**
tuple: (log_text, log_frame) where log_text is the ScrolledText widget and log_frame is the containing Frame.

#### `log_message`
Appends a timestamped message to the provided Tkinter text widget for logging purposes.
**Parameters:**
log_text_widget (tkinter.Text): The text widget where the log message will be displayed.
message (str): The message to log.

#### `create_dropdown_menu`
Creates a labeled dropdown menu (OptionMenu) in the given Tkinter frame.
**Parameters:**
frame: The parent Tkinter frame to place the dropdown menu in.
label_text: The text to display as the label next to the dropdown.
variable: A Tkinter variable to store the selected option.
options: A list of options to display in the dropdown menu.
**Returns:**
The created Tkinter OptionMenu widget.

#### `create_button`
Creates and returns a Tkinter Button widget with customizable text, command, size, and colors.
**Parameters:**
frame: The parent widget where the button will be placed.
text (str): The label displayed on the button.
command (callable): The function to be called when the button is clicked.
width (int, optional): The width of the button. Defaults to 15.
height (int, optional): The height of the button. Defaults to 2.
bg (str, optional): The background color of the button. Defaults to "#4CAF50".
fg (str, optional): The text color of the button. Defaults to "white".
**Returns:**
tk.Button: The configured Button widget.

#### `show_messagebox`
Displays a message box with the specified icon, title, and message using tkinter.
**Parameters:**
icon (str): Type of message box to display ('info', 'warning', or 'error').
title (str): The title of the message box window.
message (str): The message to display in the message box.

#### `create_text_entry`
Creates a text entry widget for user input.
**Parameters:**
root (tk.Tk or tk.Frame): The parent widget.
height (int): Number of lines tall.
width (int): Number of characters wide.
**Returns:**
tk.Text: A configured Text widget.

#### `format_summary_results`
Formats a list of result items into a readable summary string.
Each result can be a dict with 'score' and 'text' keys, a tuple/list with score and text,
or any other type, which will be converted to string with a default score of 0.0.
Handles exceptions gracefully and includes error information in the output.
**Parameters:**
results (list): List of result items to format.
**Returns:**
str: Formatted summary string with scores and texts.

#### `format_raw_results`
Formats a list of raw result items into a readable string.
Each result is processed based on its type (dict, list/tuple, or other),
and formatted with a '[RAW LOG MATCH]' prefix. Handles exceptions by
including error details in the output.
**Parameters:**
results (list): List of raw result items to format.
**Returns:**
str: Formatted string representation of all results.

#### `display_message`
Displays an informational message box.

#### `display_error`
Displays an error message box.

#### `format_coverage_data`
Formats the structured coverage data into a readable string grouped by main category.
**Parameters:**
data (list[dict]): List of coverage data entries.
**Returns:**
str: A nicely formatted string for displaying coverage stats.


## `scripts\gui\gui_logging`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | gui_logging.py
This module provides a logging handler that appends log messages to a Tkinter Text widget. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `GUILogHandler`
A logging handler that appends log messages to a Tkinter Text widget.

### 🛠️ Functions
#### `__init__`
:param text_widget: The Text widget where log messages should be appended.

#### `emit`
Emits a log message to the associated Text widget.
:param record: logging.LogRecord

#### `append_message`
Appends a log message to the associated Text widget.
This method is designed to be called from the main thread,
and will block until the message is appended.


## `scripts\gui\style_manager`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | style_manager.py
This module defines the StyleManager class for managing application-wide styles for tkinter and ttk.
Core features include:
- Managing application-wide styles for tkinter and ttk.
- Defining default colors and fonts.
- Configuring ttk styles.
- Updating specific styles with new options. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `StyleManager`
Manages application-wide styles for tkinter and ttk.
This class can be extended to handle dynamic theme changes.
Attributes:
root (Tk): The root Tkinter window.
style (ttk.Style): The ttk style manager instance.

### 🛠️ Functions
#### `__init__`
Initializes the StyleManager with the specified root window.
**Parameters:**
root (Tk): The root Tkinter window.

#### `initialize_styles`
Defines default colors and fonts and configures ttk styles.
**Returns:**
None

#### `update_style`
Update a specific style with new options.
**Parameters:**
style_name (str): The name of the style to update (e.g., 'TButton').
options (Dict[str, Any]): A dictionary of style options (e.g., {'background': 'red'}).
**Returns:**
None


## `scripts\gui\widget_factory`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | widget_factory.py
This module defines the WidgetFactory class for creating common widgets with standardized styling.
Core features include:
- Creating styled buttons, labels, entries, frames, and notebooks for Tkinter applications.
- Providing a consistent look and feel across the application. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `WidgetFactory`
Factory for creating common widgets with standardized styling.
This class provides static methods to create buttons, labels, entries, frames, and notebooks with consistent styles.

### 🛠️ Functions
#### `create_button`
Create and return a styled ttk Button.
**Parameters:**
parent (tk.Widget): The parent widget.
text (str): The text to display on the button.
command (callable): The function to call when the button is clicked.
style (str): The style to apply to the button. Defaults to 'TButton'.
**options: Additional options to configure the button.
**Returns:**
ttk.Button: The created button widget.

#### `create_label`
Create and return a styled ttk Label.
**Parameters:**
parent (tk.Widget): The parent widget.
text (str): The text to display on the label.
style (str): The style to apply to the label. Defaults to 'TLabel'.
**options: Additional options to configure the label.
**Returns:**
ttk.Label: The created label widget.

#### `create_entry`
Create and return a ttk Entry widget.
**Parameters:**
parent (tk.Widget): The parent widget.
textvariable (Any): The variable to associate with the entry. Defaults to None.
**options: Additional options to configure the entry.
**Returns:**
ttk.Entry: The created entry widget.

#### `create_frame`
Create and return a ttk Frame widget.
**Parameters:**
parent (tk.Widget): The parent widget.
style (str): The style to apply to the frame. Defaults to 'TFrame'.
**options: Additional options to configure the frame.
**Returns:**
ttk.Frame: The created frame widget.

#### `create_notebook`
Create and return a ttk Notebook widget.
**Parameters:**
parent (tk.Widget): The parent widget.
**options: Additional options to configure the notebook.
**Returns:**
ttk.Notebook: The created notebook widget.
