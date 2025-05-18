   # CI Router Configuration
This JSON file configures the CI router's behavior, mapping file patterns to CI tasks.

```json
{
  "file_patterns": {
    "python": ["*.py"],
    "tests": ["tests/", "*/test_*.py"],
    "documentation": ["docs/", "*.md", "README.md"],
    "ci": [".github/", "*.yml"],
    "refactor": ["scripts/refactor/"]
  },
  
  "tasks": {
    "lint": {
      "name": "lint",
      "command": "python scripts/refactor/lint_report_pkg/lint_report_cli.py --audit artifacts/router/linting_report.json",
      "description": "Run linter checks on changed files",
      "affected_by": ["python"],
      "always_run": false,
      "requires": [],
      "output_files": ["artifacts/router/linting_report.json"]
    },
    
    "test": {
      "name": "test",
      "command": "pytest -c pytest.ini --cov=scripts --cov-config=.coveragerc --cov-report=json:artifacts/router/coverage.json",
      "description": "Run tests affected by changed files",
      "affected_by": ["python", "tests"],
      "always_run": false,
      "requires": [],
      "output_files": ["artifacts/router/coverage.json"]
    },
    
    "docstring": {
      "name": "docstring",
      "command": "python scripts/refactor/parsers/docstring_parser.py --json --path scripts",
      "description": "Generate docstring summary for changed files",
      "affected_by": ["python"],
      "always_run": false,
      "requires": [],
      "output_files": ["docstring_summary.json"]
    },
    
    "refactor_guard": {
      "name": "refactor_guard",
      "command": "python scripts/refactor/refactor_guard_cli.py --refactored scripts --all --json --output artifacts/router/refactor_audit.json --coverage-path artifacts/router/coverage.json",
      "description": "Run RefactorGuard on changed files",
      "affected_by": ["python"],
      "always_run": false,
      "requires": ["test"],
      "output_files": ["artifacts/router/refactor_audit.json"]
    },
    
    "strictness_analysis": {
      "name": "strictness_analysis",
      "command": "python scripts/refactor/test_discovery.py --tests tests --output artifacts/router/test_report.json && python scripts/refactor/strictness_analyzer.py --test-report artifacts/router/test_report.json --audit artifacts/router/refactor_audit.json --output artifacts/router/final_strictness_report.json",
      "description": "Run strictness analysis on affected tests",
      "affected_by": ["python", "tests"],
      "always_run": false,
      "requires": ["test", "refactor_guard"],
      "output_files": ["artifacts/router/test_report.json", "artifacts/router/final_strictness_report.json"]
    },
    
    "merge_reports": {
      "name": "merge_reports",
      "command": "python scripts/refactor/merge_audit_reports.py --docstrings docstring_summary.json --coverage artifacts/router/refactor_audit.json --linting artifacts/router/linting_report.json -o artifacts/router/merged_report.json",
      "description": "Merge all reports into a comprehensive summary",
      "affected_by": [],
      "always_run": true,
      "requires": ["lint", "docstring", "refactor_guard"],
      "output_files": ["artifacts/router/merged_report.json"]
    },
    
    "severity_audit": {
      "name": "severity_audit",
      "command": "python scripts/ci_analyzer/severity_audit.py --audit artifacts/router/merged_report.json --output artifacts/router/ci_severity_report.md",
      "description": "Generate severity audit report",
      "affected_by": [],
      "always_run": true,
      "requires": ["merge_reports"],
      "output_files": ["artifacts/router/ci_severity_report.md"]
    }
  }
}
```

## Adding Custom Tasks

To add a new CI task:

1. Create a new entry in the `tasks` section
2. Specify which file patterns should trigger the task via the `affected_by` array
3. Set any task dependencies using the `requires` array
4. Add the task to your CI workflow file

Example: Adding a new linting task for YAML files

```json
"yaml_lint": {
  "name": "yaml_lint",
  "command": "yamllint -c .yamllint.yml ./",
  "description": "Run YAML linter on changed YAML files",
  "affected_by": ["yaml"],
  "always_run": false,
  "requires": [],
  "output_files": ["artifacts/router/yamllint_report.txt"]
}
```

Then add a new pattern to `file_patterns`:

```json
"yaml": ["*.yml", "*.yaml"]
```