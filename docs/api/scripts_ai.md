# `scripts/ai`


## `scripts\ai\__init__`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | The `ai` module provides AI-powered summarization utilities for text entries using large language models (LLMs).
Core features include:
- Generating concise summaries for individual or multiple text entries.
- Supporting subcategory-specific prompts for context-aware summarization.
- Configurable model selection and prompt templates, loaded at initialization.
- Fallback to the Ollama chat API for summarization if the primary LLM fails.
- Designed for seamless integration into workflows requiring automated, high-quality text summarization.
This module enables flexible and robust summarization capabilities for downstream applications such as log analysis, reporting, and intelligent querying. |
| Args | — |
| Returns | — |


## `scripts\ai\ai_summarizer`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | This module provides the AISummarizer class for generating summaries of text entries
using a configurable large language model (LLM).
It supports both single-entry and bulk summarization, with the ability to use
subcategory-specific prompts loaded from configuration. If the primary summarization
method fails, the module falls back to the Ollama chat API to attempt summarization.
Logging is integrated throughout for monitoring and debugging,
and configuration is loaded at initialization for flexible model and prompt management.
Typical use cases include automated summarization of logs, notes, or other textual data
in workflows requiring concise, context-aware summaries. |
| Args | — |
| Returns | — |

### 📦 Classes
#### `AISummarizer`
AISummarizer provides methods to generate summaries for single or multiple text entries
using a configurable LLM model and subcategory-specific prompts. It supports fallback
to the Ollama chat API if primary summarization fails and loads configuration settings
at initialization.

### 🛠️ Functions
#### `__init__`
Initializes the AISummarizer with configuration settings, LLM model selection, and subcategory-specific prompts.

#### `_fallback_summary`
Attempts to generate a summary using the Ollama chat API as a fallback.
Sends the provided prompt to the chat model and returns the generated summary, or an error message if the fallback fails.

#### `summarize_entry`
Generates a summary for a single text entry using the configured LLM model and an optional subcategory-specific prompt.
**Parameters:**
entry_text: The text to be summarized.
subcategory: Optional subcategory to select a specialized prompt.
**Returns:**
The generated summary, or a fallback message if summarization fails.

#### `summarize_entries_bulk`
Generates a summary for multiple text entries using the configured LLM model and subcategory-specific prompts.
If the input list is empty, returns a warning message. Falls back to an alternative summarization method if the primary LLM call fails or returns an invalid response.
**Parameters:**
entries: List of text entries to summarize.
subcategory: Optional subcategory to select a specific summarization prompt.
**Returns:**
The generated summary as a string, or a fallback message if summarization is unsuccessful.


## `scripts\ai\llm_optimization`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | Utility helpers for summarising code‑quality artefacts and building LLM prompts.
🔧 **Patch v2** – restores backwards‑compat fields and fixes helper signature
regressions that broke the existing unit‑test suite.
*   `summarize_file_data_for_llm` again returns the exact keys
``{"complexity", "coverage"}`` expected by old tests.
*   Added thin wrapper ``_categorise_issues`` that accepts the legacy
`(entries, condition, message, cap)` signature and is used by
``build_strategic_recommendations_prompt``.
*   Internal refactor helpers renamed with leading underscores but public
function signatures stay **unchanged**.
*   Added type‑hints + docstrings for the new helper. |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `_mean`
Calculates the mean of a list of floats.
Returns 0.0 if the list is empty.

#### `_categorise_issues`
Returns a summary of how many files fall into each major code quality issue category.
The summary includes counts of files with more than 5 type errors, average complexity greater than 7, and average coverage below 60%.

#### `summarize_file_data_for_llm`
Generates a summary dictionary of code quality metrics for a single file.
Extracts and computes average complexity, coverage percentage, MyPy error count, and docstring completeness from nested file data. Returns a dictionary with legacy-compatible keys, including the file name, full path, rounded metrics, docstring ratio, and a list of up to three top issues.

#### `extract_top_issues`
Extracts up to a specified number of top code quality issues from file data.
The function prioritizes the first MyPy error, the first function with high complexity (complexity > 10), and the first function with low coverage (coverage < 50%), returning formatted issue descriptions.
**Parameters:**
file_data: Dictionary containing code quality metrics for a file.
max_issues: Maximum number of issues to extract.
**Returns:**
A list of formatted strings describing the top issues found in the file.

#### `build_refactor_prompt`
Builds an LLM prompt requesting strategic refactoring suggestions for a list of offender files.
The prompt summarizes up to `limit` files with significant code quality issues, applies a persona and template from the configuration, and includes both a summary and detailed offender information. The resulting prompt instructs the LLM to focus on identifying refactoring patterns rather than file-specific advice.
**Parameters:**
offenders: List of tuples containing file details and metrics for files needing refactoring.
config: Configuration object providing persona and prompt template.
verbose: If True, includes detailed information for each file; otherwise, provides a concise summary.
limit: Maximum number of offender files to include in the prompt.
**Returns:**
A formatted prompt string for use with an LLM.

#### `build_strategic_recommendations_prompt`
Constructs a detailed prompt for an LLM to generate strategic, actionable recommendations for improving code quality and test coverage based on severity data and summary metrics.
The prompt summarizes the distribution of key issues (high complexity, low coverage, type errors), highlights problematic modules with multiple severe files, and lists the top offenders. It instructs the LLM to provide specific, non-generic recommendations tied directly to the identified files and modules, prioritizing complexity, coverage, type errors, and documentation.
**Parameters:**
severity_data: List of dictionaries containing per-file severity metrics and scores.
summary_metrics: Overall codebase metrics, either as a formatted string or a dictionary.
limit: Maximum number of top offender files to include in the summary (default: 30).
**Returns:**
A formatted prompt string for use with an LLM, emphasizing targeted, codebase-specific recommendations.

#### `compute_severity`
Calculates a weighted severity score and summary metrics for a single module.
The severity score combines counts of MyPy errors, pydocstyle lint issues, average function complexity, and lack of test coverage using fixed weights. Returns a dictionary with the file name, full path, error and issue counts, average complexity, average coverage percentage, and the computed severity score.

#### `_summarise_offenders`
Aggregates a list of offender files into a summary of key code quality issues.
Counts and lists up to five example files for each of the following categories: high complexity (complexity > 8), low coverage (coverage < 50%), and many type errors (more than 5 type errors). Returns a formatted multiline string summarizing the counts and sample file names per category.

#### `_fmt`
Formats a list of strings as a comma-separated string, truncating with '...' if more than five items.
**Parameters:**
lst: List of strings to format.
**Returns:**
A string of up to five comma-separated items from the list, followed by '...' if the list contains more than five items.

#### `_format_offender_block`
Formats offender file details into a summary block for inclusion in LLM prompts.
If verbose is True, returns a detailed multiline summary for each file including severity score, error counts, complexity, coverage, and sample errors. Otherwise, returns a concise single-line summary per file.


## `scripts\ai\llm_refactor_advisor`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | This module provides functionality to load audit reports and build refactor prompts for an AI assistant.
It includes functions to load JSON audit data, extract top offenders based on various metrics, and generate prompts for AI assistance. |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `load_audit`
Loads and returns audit data from a JSON file at the given path.
**Parameters:**
path: Path to the JSON audit report file.
**Returns:**
Parsed audit data as a dictionary.

#### `extract_top_offenders`
Identifies and ranks the top offending files in an audit report based on code quality metrics.
Processes the report data to compute a composite score for each file using MyPy errors, linting issues, average code complexity, and average test coverage. Applies special weighting for "app/views.py" to prioritize its score. Returns a list of the top N files sorted by descending score, with each entry containing the file path, score, error and lint counts, average complexity, and average coverage.
**Parameters:**
report_data: Audit report data mapping file paths to their metrics.
top_n: Number of top offenders to return.
**Returns:**
A list of tuples for the top offenders, each containing file path, score, error count, lint issue count, average complexity, and average coverage.

#### `build_refactor_prompt`
Constructs a prompt for an AI assistant summarizing top risky files for refactoring.
Generates a ranked list of offender files with their associated metrics and formats it into a prompt using a template and persona from the configuration. Optionally limits the number of offenders included and adds detailed file paths if verbose is True.
**Parameters:**
offenders: List of tuples containing file path, score, MyPy errors, lint issues, code complexity, and coverage.
subcategory: Prompt template subcategory to use.
verbose: If True, includes full file paths in the prompt.
limit: Maximum number of offenders to include; includes all if None.
**Returns:**
The formatted prompt string for the AI assistant.


## `scripts\ai\llm_router`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | This module provides functionality to retrieve prompt templates and apply personas to prompts for an AI assistant.
It includes functions to get prompt templates based on subcategories and modify prompts according to specified personas. |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `get_prompt_template`
Retrieves the prompt template for a specified subcategory from the configuration.
If the subcategory is not found, returns the default prompt template.

#### `apply_persona`
Appends persona-specific instructions to a prompt to tailor the AI's response style.
If the persona is "reviewer", "mentor", or "planner", a corresponding instruction is added to the prompt. If the persona is "default" or unrecognized, the prompt is returned unchanged.
**Parameters:**
prompt: The original prompt string.
persona: The persona to apply ("default", "reviewer", "mentor", or "planner").
**Returns:**
The prompt string with persona-specific instructions appended if applicable.


## `scripts\ai\module_docstring_summarizer`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | This module provides functionality to load audit reports and build refactor prompts for an AI assistant.
It includes functions to load JSON audit data, extract top offenders based on various metrics, and generate prompts for AI assistance. |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `summarize_module`
Generates a concise summary of a Python module's functionality based on its docstrings.
Formats the provided docstring entries into a structured prompt, applies persona adjustments, and uses the given AI summarizer to produce a human-readable summary. Returns a fixed message if no docstrings are available.
**Parameters:**
file_path: Path to the module file.
doc_entries: List of docstring entries, each representing a function or class.
**Returns:**
A summary string describing the module's functionality, or a message if no docstrings are found.

#### `run`
Executes the module docstring summarization workflow for a given JSON audit report.
Processes each file in the report, optionally filtering by file path substring, and generates a summary of its documented functions using an AI summarizer. Outputs the results either to a Markdown file or to standard output.


## `scripts\ai\module_idea_generator`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `suggest_new_modules`
Generates new module or package suggestions and corresponding Python prototype code based on an architecture report.
Reads a JSON report of documented functions, filters them by an optional path substring, and summarizes their docstrings. Uses an AI summarizer to propose new modules/packages with justifications and then generates Python code stubs for the suggested modules, adhering to strict naming conventions.
**Parameters:**
artifact_path: Path to the JSON architecture report.
subcategory: Optional subcategory for prompt context.
path_filter: Optional substring to filter file paths.
**Returns:**
A tuple containing the textual module suggestions and the generated Python prototype code.

#### `generate_test_stubs`
Generates pytest unit test stubs for the provided module prototype code.
**Parameters:**
prototype_code: The Python module prototype code for which to generate tests.
**Returns:**
A string containing pytest test stubs formatted with appropriate filenames and code blocks.

#### `extract_filenames_from_code`
Extracts Python filenames from code by searching for '# Filename: <filename.py>' comments.
**Parameters:**
code: The code string to search for filename comments.
**Returns:**
A list of extracted Python filenames.

#### `export_prototypes_to_files`
Writes generated code or test stubs to files based on embedded '# Filename' comments.
Scans code blocks for filename annotations, adjusts names for test files if needed, adds required imports, and writes each code block to the appropriate file within the specified output directory.

#### `validate_test_coverage`
Checks that all public functions and methods in the given module directory have corresponding pytest tests in the specified test directory.
**Parameters:**
module_dir: Path to the directory containing module source files.
test_dir: Path to the directory containing pytest test files.
**Returns:**
A list of fully qualified names for public functions and methods that lack corresponding tests.
