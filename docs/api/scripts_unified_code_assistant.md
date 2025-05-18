# `scripts/unified_code_assistant`


## `scripts\unified_code_assistant\__init__`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |


## `scripts\unified_code_assistant\analysis`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `analyze_report`
Analyze the report data to extract top offenders, severity data, and metrics.


## `scripts\unified_code_assistant\assistant_cli`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `chat_mode`
*No description available.*

#### `main`
*No description available.*


## `scripts\unified_code_assistant\assistant_utils`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `load_report`
*No description available.*

#### `extract_code_snippets`
*No description available.*

#### `_format_snippet`
*No description available.*

#### `get_issue_locations`
Extract and categorize issues for a given file path from the report data.
Returns a dict with keys:
- 'mypy_errors': List of mypy issue dicts
- 'lint_issues': List of lint issue dicts
- 'complexity_issues': List of complexity issue dicts

#### `_extract_mypy_issues`
*No description available.*

#### `_extract_lint_issues`
*No description available.*

#### `_extract_complexity_issues`
*No description available.*


## `scripts\unified_code_assistant\module_summarizer`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `summarize_modules`
Generate summaries of module functionality based on docstrings.
**Parameters:**
report_data (Dict): Parsed code analysis report.
summarizer (AISummarizer): Summarization engine.
config: Configuration object.
path_filter (Optional[str]): Optional substring to filter files.
**Returns:**
Dict[str, str]: Mapping of file paths to summaries.


## `scripts\unified_code_assistant\prompt_builder`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `build_contextual_prompt`
*No description available.*

#### `build_enhanced_contextual_prompt`
*No description available.*


## `scripts\unified_code_assistant\strategy`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `generate_strategy`
Generate strategic recommendations using severity and metric data.
**Parameters:**
severity_data (List[Dict]): Computed severity info per file.
summary_metrics (Dict): High-level code quality metrics.
limit (int): Max number of files to include.
persona (str): AI assistant persona.
summarizer (AISummarizer): Summarization engine.
**Returns:**
str: Strategic AI recommendations
