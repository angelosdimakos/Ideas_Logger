# Docstring Report for `scripts/unified_code_assistant/`


## `scripts\unified_code_assistant\__init__`


## `scripts\unified_code_assistant\analysis`


### Functions

#### analyze_report

Analyze the report data to extract top offenders, severity data, and metrics.

## `scripts\unified_code_assistant\assistant_cli`


### Functions

#### chat_mode

#### main

## `scripts\unified_code_assistant\assistant_utils`


### Functions

#### load_report

#### extract_code_snippets

#### _format_snippet

#### get_issue_locations

Extract and categorize issues for a given file path from the report data.
Returns a dict with keys:
- 'mypy_errors': List of mypy issue dicts
- 'lint_issues': List of lint issue dicts
- 'complexity_issues': List of complexity issue dicts

#### _extract_mypy_issues

#### _extract_lint_issues

#### _extract_complexity_issues

## `scripts\unified_code_assistant\module_summarizer`


### Functions

#### summarize_modules

Generate summaries of module functionality based on docstrings.

**Arguments:**
report_data (Dict): Parsed code analysis report.
summarizer (AISummarizer): Summarization engine.
config: Configuration object.
path_filter (Optional[str]): Optional substring to filter files.

**Returns:**
Dict[str, str]: Mapping of file paths to summaries.

## `scripts\unified_code_assistant\prompt_builder`


### Functions

#### build_contextual_prompt

#### build_enhanced_contextual_prompt

## `scripts\unified_code_assistant\strategy`


### Functions

#### generate_strategy

Generate strategic recommendations using severity and metric data.

**Arguments:**
severity_data (List[Dict]): Computed severity info per file.
summary_metrics (Dict): High-level code quality metrics.
limit (int): Max number of files to include.
persona (str): AI assistant persona.
summarizer (AISummarizer): Summarization engine.

**Returns:**
str: Strategic AI recommendations