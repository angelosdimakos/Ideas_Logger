# `scripts/core`


## `scripts\core\__init__`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |


## `scripts\core\core`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Core module for Zephyrus Logger
================================
This refactored **core.py** wires together the new, slimmer helper
modules we just introduced (`EnvironmentBootstrapper`, `LogManager`,
`MarkdownLogger`, `SummaryTracker`, `SummaryEngine`). It restores the
public surface that the unit & integration tests expect while keeping
the implementation focused and declarative.
Key public methods / attributes re-exposed
-----------------------------------------
* **save_entry**          – add a new idea to JSON + Markdown & update tracker
* **log_new_entry**       – alias of *save_entry* (used by integration tests)
* **generate_global_summary** – force batch summarisation via `SummaryEngine`
* **generate_summary**    – backward-compat shim (date arg ignored)
* **search_summaries** / **search_raw_logs** – thin wrappers around the FAISS
indexers (gracefully degrade to empty list when indices are disabled in
tests)
* **BATCH_SIZE**          – pulled from config with sane default so tests can
use it directly.
Everything else (bootstrap, validation, etc.) stays untouched aside from
swapping our bespoke `_initialize_environment` with the clearer
`EnvironmentBootstrapper`. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `ZephyrusLoggerCore`
High-level façade that ties together logging, summarizing, and search functionalities.
This class serves as the main interface for managing logs, generating summaries,
and searching through entries within the Zephyrus Logger application. It initializes
various components necessary for logging and summarization, ensuring the environment
is properly set up.
Attributes:
TIMESTAMP_FORMAT (str): Format for timestamps in logs.
DATE_FORMAT (str): Format for dates in logs.
BATCH_KEY (str): Key for batch processing.
ORIGINAL_SUMMARY_KEY (str): Key for original summaries.
CORRECTED_SUMMARY_KEY (str): Key for corrected summaries.
CORRECTION_TIMESTAMP_KEY (str): Key for correction timestamps.
CONTENT_KEY (str): Key for content in logs.
TIMESTAMP_KEY (str): Key for timestamps in logs.
BATCH_SIZE (int): Number of entries to process in a batch.
ai_summarizer (AISummarizer): Instance of the AI summarizer.
log_manager (LogManager): Instance of the log manager.
md_logger (MarkdownLogger): Instance of the markdown logger.
summary_tracker (SummaryTracker): Instance of the summary tracker.
summary_engine (SummaryEngine): Instance of the summary engine.

### 🛠️ Functions
#### `__init__`
Initializes ZephyrusLoggerCore with configuration, environment setup, and core components.
Loads configuration, resolves file system paths, ensures required directories and files exist, and instantiates collaborators for logging, summarization, and summary tracking. Validates the summary tracker on startup, rebuilding it if necessary or configured to do so.
**Parameters:**
script_dir: Path to the script directory used for resolving application paths.
Raises:
RuntimeError: If the summary tracker fails validation after a rebuild.

#### `save_entry`
Saves a new log entry to both the JSON log and Markdown export.
Adds the entry under the specified main category and subcategory, updates the summary tracker, and returns whether the Markdown export succeeded.
**Parameters:**
main_category: The primary category for the log entry.
subcategory: The subcategory for the log entry.
entry: The content of the log entry.
**Returns:**
True if the entry was successfully exported to Markdown; False otherwise.

#### `generate_global_summary`
Generates a batch summary for the specified main category and subcategory.
**Parameters:**
main_category: The primary category to summarize.
subcategory: The subcategory within the main category.
**Returns:**
True if the batch summarization succeeds; otherwise, False.

#### `generate_summary`
Generates a summary for the specified main category and subcategory.
This method ignores the date argument and delegates to generate_global_summary for backward compatibility.
**Parameters:**
_date_str: Ignored legacy date argument.
main_category: The main category to summarize.
subcategory: The subcategory to summarize.
**Returns:**
True if the summary generation succeeds, False otherwise.

#### `_safe_search`
Safely performs a search on a specified FAISS indexer attribute of the summary tracker.
If the indexer or its search method is unavailable, or if an exception occurs during search, returns an empty list.
**Parameters:**
indexer_attr: Name of the summary tracker attribute representing the FAISS indexer.
query: The search query string.
top_k: Maximum number of results to return.
**Returns:**
A list of search results, or an empty list if the search fails.

#### `search_summaries`
Searches summary entries for the most relevant matches to a query using vector similarity.
**Parameters:**
query: The search query string.
top_k: Maximum number of results to return.
**Returns:**
A list of the top-k most relevant summary search results, or an empty list if search fails.

#### `search_raw_logs`
Searches raw log entries for the most relevant matches to a query using vector similarity.
**Parameters:**
query: The search query string.
top_k: Maximum number of results to return.
**Returns:**
A list of the top-k most relevant raw log entries matching the query.

#### `_safe_read_json`
Safely reads a JSON file and returns its contents as a dictionary.
If the file cannot be read or parsed, returns an empty dictionary instead of raising an exception.


## `scripts\core\core_cli`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Command Line Interface for Zephyrus Logger
===============================
This module provides a command-line interface for the Zephyrus Logger application,
allowing users to log entries, summarize categories, and search through logs. |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `log`
Logs a new entry under the specified main and subcategory.
**Parameters:**
main: Main category for the log entry.
sub: Subcategory for the log entry.
entry: Content of the log entry.
The entry is saved in both JSON and Markdown formats.

#### `summarize`
Generates a summary for the specified main category and subcategory.
**Parameters:**
main: The main category to summarize.
sub: The subcategory to summarize.
Prints a confirmation message if the summary is generated, or a warning if there are insufficient entries or the operation fails.

#### `search`
Searches summaries or raw logs and displays the top results.
**Parameters:**
query: The search query string.
top_k: Maximum number of results to display.
kind: Specifies whether to search 'summary' or 'raw' logs. Defaults to 'summary'.


## `scripts\core\environment_bootstrapper`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Environment Bootstrapper Module
===============================
This module provides the EnvironmentBootstrapper class, which is responsible
for setting up the necessary directories and files for the Zephyrus Logger
application. It ensures that all required resources are in place before
the application starts. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `EnvironmentBootstrapper`
A class to bootstrap the environment for the Zephyrus Logger application.
This class handles the creation of necessary directories and files,
ensuring that the application has all required resources available.
Attributes:
paths (ZephyrusPaths): An instance containing paths for logs, exports,
and configuration files.
default_batch_size (int): The default batch size to use if the
configuration file is missing.

### 🛠️ Functions
#### `__init__`
Initializes the EnvironmentBootstrapper with paths and a default batch size.
**Parameters:**
paths: Contains locations for logs, exports, and configuration files.
default_batch_size: Default batch size used if the configuration file is missing.

#### `bootstrap`
Prepares the application environment by ensuring required directories and files exist.
Calls internal methods to create necessary directories and initialize essential files for the Zephyrus Logger application, guaranteeing all resources are ready before startup.

#### `_make_directories`
Creates required directories for logs, exports, and configuration files if they do not exist.

#### `_initialize_files`
Initializes required log and configuration files for the Zephyrus Logger environment.
Creates empty or default-initialized files if they do not exist, including the JSON log, text log, correction summaries, and configuration files. If the correction summaries file exists but is empty, it is reinitialized as an empty JSON file. The configuration file is recreated with a default batch size if missing.


## `scripts\core\log_manager`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | log_manager.py
This module provides the LogManager class for managing log entries and correction summaries.
It includes functionality for reading and writing log data in both JSON and plain text formats,
as well as handling timestamps and content keys for structured logging. The LogManager is essential
for the Zephyrus Logger application to maintain a reliable logging system.
Dependencies:
- pathlib
- datetime
- logging
- scripts.utils.file_utils |
| Args | — |
| Returns | — |

### 📦 Classes
#### `LogManager`
*No description available.*

### 🛠️ Functions
#### `__init__`
Initializes a LogManager instance.
**Parameters:**
json_log_file (Path): Path to the JSON file that stores log entries.
txt_log_file (Path): Path to the text file that stores log entries in plain text.
correction_summaries_file (Path): Path to the JSON file that stores correction summaries.
timestamp_format (str): Timestamp format for log entries.
content_key (str): Key used to store the content of a log entry in the JSON file.
timestamp_key (str): Key used to store the timestamp of a log entry in the JSON file.

#### `_safe_read_or_create_json`
Safely reads a JSON file or creates it if it doesn't exist.
If the file doesn't exist, it will create an empty JSON object.
**Parameters:**
filepath (Path): Path to the JSON file.
**Returns:**
dict: The parsed JSON data or an empty dictionary if the file couldn't be loaded.

#### `read_logs`
Reads the JSON log file and returns its contents. If the file doesn't exist, it will create an empty JSON object.
**Returns:**
dict: The parsed JSON data or an empty dictionary if the file couldn't be loaded.

#### `update_logs`
Updates the JSON log file with the provided update function.
The update function will be provided with the current JSON data as a dictionary.
The function should modify the dictionary in-place as needed.
**Parameters:**
update_func (Callable[[dict], None]): The function to call to update the JSON data.

#### `append_entry`
Appends a new log entry to the JSON log file.
**Parameters:**
date_str (str): The date of the log entry in the format specified by `timestamp_format`.
main_category (str): The main category of the log entry.
subcategory (str): The subcategory of the log entry.
entry (str): The content of the log entry.

#### `updater`
Updates the JSON data to append a new log entry.
**Parameters:**
data (dict): The current JSON data.

#### `get_unsummarized_batch`
Retrieves a batch of unsummarized log entries for the given main category and subcategory.
**Parameters:**
main_category (str): The main category of the log entries.
subcategory (str): The subcategory of the log entries.
summarized_total (int): The total number of log entries that have already been summarized.
batch_size (int): The number of unsummarized log entries to retrieve in the batch.
**Returns:**
list: A list of log entries, each represented as a dictionary with 'timestamp' and 'content' keys.

#### `update_correction_summaries`
Updates the correction summaries JSON file with new data.
**Parameters:**
main_category (str): The main category of the log entries.
subcategory (str): The subcategory of the log entries.
new_data (dict): The new data to append to the correction summaries.
The dictionary should contain the following keys:
- "batch": The batch label.
- "original_summary": The original summary.
- "corrected_summary": The corrected summary.
- "correction_timestamp": The timestamp of the correction.
- "start": The start timestamp of the batch.
- "end": The end timestamp of the batch.


## `scripts\core\markdown_logger`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Markdown Logger Module
===============================
This module provides the MarkdownLogger class, which is responsible
for logging entries to Markdown files. It handles the creation and
updating of Markdown files in the specified export directory. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `MarkdownLogger`
A class to log entries to Markdown files.
This class manages the logging of entries into Markdown format,
creating new files or updating existing ones as necessary.
Attributes:
export_dir (Path): The directory where Markdown files will be saved.

### 🛠️ Functions
#### `__init__`
Initializes a MarkdownLogger to write entries to Markdown files in the specified directory.
**Parameters:**
export_dir: Directory where Markdown files will be stored.

#### `log`
Logs an entry under a specific date and category in a Markdown file.
Creates or updates a Markdown file named after the main category, adding the entry under the specified date header and subcategory. Returns True if the operation succeeds, or False if an error occurs.


## `scripts\core\summary_engine`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Summary Engine Module
===============================
This module provides the SummaryEngine class, which is responsible
for generating summaries from log entries using AI summarization.
It integrates with the log manager and summary tracker to manage
the summarization process. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `SummaryEngine`
A class to manage the summarization of log entries.
This class utilizes an AI summarizer to generate summaries from
batches of log entries, coordinating with the log manager and
summary tracker.
Attributes:
summarizer (AISummarizer): The AI summarizer instance.
log_manager (LogManager): The log manager instance.
tracker (SummaryTracker): The summary tracker instance.
timestamp_format (str): The format for timestamps.
content_key (str): The key for content in log entries.
timestamp_key (str): The key for timestamps in log entries.
batch_size (int): The number of entries to process in a batch.

### 🛠️ Functions
#### `__init__`
Initialize the SummaryEngine.
Parameters:
summarizer (AISummarizer): The AI summarizer instance.
log_manager (LogManager): The log manager instance.
summary_tracker (SummaryTracker): The summary tracker instance.
timestamp_format (str): The format for timestamps.
content_key (str): The key for content in log entries.
timestamp_key (str): The key for timestamps in log entries.
batch_size (int): The number of entries to process in a batch.

#### `_get_summary`
Generate a summary from a batch of log entries.
Parameters:
batch_entries (List[Dict[str, Any]]): The batch of log entries.
subcategory (str): The subcategory for the summary.
**Returns:**
Optional[str]: The generated summary, or None if summarization fails.

#### `summarize`
Summarize log entries for a given main category and subcategory.
Parameters:
main_category (str): The main category for the summary.
subcategory (str): The subcategory for the summary.
**Returns:**
bool: True if summarization is successful, False otherwise.


## `scripts\core\summary_tracker`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | summary_tracker.py
This module provides the SummaryTracker class for managing and tracking summaries of logs.
It includes functionality for loading tracker data, initializing indexers, and maintaining
the state of summaries. This module is essential for the Zephyrus Logger application to
manage summaries effectively.
Dependencies:
- json
- logging
- pathlib
- collections (defaultdict)
- scripts.indexers.summary_indexer
- scripts.indexers.raw_log_indexer
- scripts.utils.file_utils
- scripts.paths.ZephyrusPaths |
| Args | — |
| Returns | — |

### 📦 Classes
#### `SummaryTracker`
SummaryTracker manages the loading, initialization, and tracking of summary data for logs.
Attributes:
paths (ZephyrusPaths): The paths configuration for the summary tracker.
tracker_path (Path): The path to the summary tracker file.
tracker (Dict[str, Dict[str, Any]]): The loaded tracker data.
summary_indexer (Optional[SummaryIndexer]): The indexer for summaries.
raw_indexer (Optional[RawLogIndexer]): The indexer for raw logs.

### 🛠️ Functions
#### `__init__`
Initializes the SummaryTracker with the given paths.
**Parameters:**
paths (ZephyrusPaths): The paths configuration for the summary tracker.

#### `_safe_load_tracker`
Safely loads the tracker data from the tracker file.
**Returns:**
Dict[str, Dict[str, Any]]: The loaded tracker data, or an empty dictionary if loading fails.

#### `_safe_init_summary_indexer`
Safely initializes the SummaryIndexer.
**Returns:**
Optional[SummaryIndexer]: The initialized SummaryIndexer, or None if initialization fails.

#### `_safe_init_raw_indexer`
Safely initializes the RawLogIndexer.
**Returns:**
Optional[RawLogIndexer]: The initialized RawLogIndexer, or None if initialization fails.

#### `get_summarized_count`
Retrieves the summarized count for the given main category and subcategory.
**Parameters:**
main_category (str): The main category.
subcategory (str): The subcategory.
**Returns:**
int: The summarized count.

#### `update`
Updates the tracker with the given summarized and new entries counts.
**Parameters:**
main_category (str): The main category.
subcategory (str): The subcategory.
summarized (int, optional): The summarized count. Defaults to 0.
new_entries (int, optional): The new entries count. Defaults to 0.

#### `_save`
Saves the tracker data to the tracker file.

#### `rebuild`
Rebuilds the tracker by clearing the current data and re-counting the logged and summarized entries.

#### `validate`
Validates the tracker by comparing the summarized counts with the actual counts in the correction summaries.
**Parameters:**
verbose (bool, optional): If True, logs every subcategory status. Otherwise, only logs mismatches. Defaults to False.
**Returns:**
bool: True if the tracker is valid (no mismatches), False otherwise.

#### `get_coverage_data`
Returns a structured list of coverage data for all tracked (main, sub) categories.
Each entry includes:
- main_category
- subcategory
- logged_total
- estimated_summarized_entries
- coverage_percent (0–100)
