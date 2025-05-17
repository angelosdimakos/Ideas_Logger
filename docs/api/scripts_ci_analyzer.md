# Docstring Report for `scripts/ci_analyzer/`


## `scripts\ci_analyzer\__init__`


## `scripts\ci_analyzer\drilldown`


This module provides functionality to generate detailed Markdown reports for top offenders in code quality analysis.
It includes functions to create drilldowns that summarize linting errors, complexity, coverage, and function descriptions for the top offenders.


### Functions

#### generate_top_offender_drilldowns

Generates a Markdown report with expandable drilldowns for the top N files with the most severe code quality issues.
For each top offender file, includes sections for MyPy errors, Pydocstyle issues, functions with high complexity or low coverage, and function docstring summaries if available.

**Arguments:**
severity_df: DataFrame listing files with associated severity metrics.
report_data: Dictionary containing detailed report data keyed by file paths.
top_n: Number of top offenders to include in the report (default is 3).

**Returns:**
A Markdown-formatted string containing detailed, collapsible analysis sections for each top offender file.

## `scripts\ci_analyzer\metrics_summary`


This module provides functionality to generate summary metrics from code quality reports.
It includes functions to analyze report data and summarize key metrics related to methods, tests, complexity, docstrings, and linter issues.


### Functions

#### generate_metrics_summary

Generates a Markdown summary of key code quality metrics from report data.
Aggregates counts of total methods audited, methods missing tests, high-complexity methods (complexity ≥ 10), methods missing docstrings, and linter issues from a nested report data dictionary. Returns a Markdown-formatted string summarizing these metrics.

## `scripts\ci_analyzer\severity_audit`


This module provides functionality to generate a CI code quality audit report.
It includes functions to format priority levels and generate summary header blocks based on severity metrics.


### Functions

#### format_priority

Returns a formatted priority label based on the given severity score.
A high priority ("🔥 High") is assigned for scores above 30, medium ("⚠️ Medium") for scores above 15, and low ("✅ Low") otherwise.

#### generate_header_block

Generates a Markdown header block summarizing key metrics from the CI code quality audit.
Calculates totals and percentages for files analyzed, files with issues, top risk file, methods audited, missing tests, missing docstrings, and linter issues. Includes visual indicators for documentation, testing, and linting coverage.

**Arguments:**
severity_df: DataFrame with severity metrics for each file.
report_data: Dictionary containing detailed audit data per file.

**Returns:**
A Markdown-formatted string representing the report's header block.

#### generate_severity_table

Generates a Markdown table ranking the top 10 files by severity for the CI audit report.
If the severity DataFrame is empty, returns a placeholder row indicating no files found. Each row displays file name, Mypy errors, lint issues, average complexity with risk emoji, average coverage with a visual bar, severity score, and formatted priority level.

#### main

Generates a CI code quality audit report in Markdown format.
Parses command-line arguments for input and output paths, loads audit data, computes severity metrics, and writes a formatted Markdown report summarizing code quality findings.

## `scripts\ci_analyzer\severity_index`


This module provides functionality to compute severity scores for code quality analysis.
It includes functions to compute individual severity scores for files and to create a severity index DataFrame from report data.


### Functions

#### compute_severity

Calculates a severity score for a file using its coverage and linting report data.
The severity score is a weighted sum of MyPy errors, Pydocstyle lint issues, average function complexity, and coverage deficit. Returns a dictionary summarizing these metrics and the computed severity score.

#### compute_severity_index

Aggregates severity scores for multiple files into a sorted DataFrame.
Processes report data for each file, computes severity metrics, and returns a DataFrame sorted by severity score in descending order. If no data is provided, returns an empty DataFrame with predefined columns.

**Arguments:**
report_data: Mapping of file paths to their coverage and linting report data.

**Returns:**
A pandas DataFrame containing severity metrics for each file, sorted by severity score.

## `scripts\ci_analyzer\visuals`


This module provides functionality to render visual representations of risk and scores for code quality analysis.
It includes functions to generate risk emojis and bar representations based on severity scores.


### Functions

#### risk_emoji

Returns an emoji indicating risk level based on the given severity score.
A green emoji ("🟢") represents low risk for scores 90 and above, yellow ("🟡") indicates moderate risk for scores between 70 and 89, and red ("🔴") signifies high risk for scores below 70.

#### render_bar

Generates a horizontal bar visualizing a score as filled and unfilled segments.

**Arguments:**
score: The value to represent, expected in the range 0 to 100.
width: Total number of segments in the bar (default is 20).

**Returns:**
A string with filled ("▓") and unfilled ("░") segments proportional to the score.