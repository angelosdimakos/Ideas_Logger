# CI Router Documentation

This document explains how to use the CI Router system to optimize your CI workflows by only running relevant tasks based on changed files.

## Overview

The CI Router analyzes git diffs to determine which files have changed and then selectively runs only the CI tasks that are relevant to those changes. This approach significantly reduces CI execution time while maintaining comprehensive code quality checks.

## Components

The CI Router system consists of:

1. **CI Router Script** (`scripts/ci/ci_router.py`): The core router that analyzes file changes and determines which tasks to run.

2. **Adapter Scripts**: Scripts that run specific CI tasks on only the files that have changed:
   - `scripts/ci/adapters/lint_router.py`: Runs linting only on changed Python files
   - `scripts/ci/adapters/test_router.py`: Runs tests that are affected by changed files
   - `scripts/ci/adapters/docstring_router.py`: Analyzes docstrings only in changed files
   - `scripts/ci/adapters/refactor_guard_router.py`: Runs RefactorGuard on changed files

3. **Configuration File** (`scripts/ci/router_config.json`): Defines file patterns and CI tasks.

4. **GitHub Actions Workflow** (`.github/workflows/ci_router.yml`): Integrates the router with GitHub Actions.

## Usage

### Running the CI Router

To run the CI Router manually:

```bash
# Run the router against a specific base branch
python scripts/ci/ci_router.py --base-branch main --report-dir artifacts/router

# Only detect changed files without running tasks
python scripts/ci/ci_router.py --changed-files-only

# Use verbose output for debugging
python scripts/ci/ci_router.py --verbose
```

### Running Individual Adapters

Each adapter can be run individually, using the router report as input:

```bash
# Run linting on changed files
python scripts/ci/adapters/lint_router.py --router-report artifacts/router/router_summary.json --output lint_report.json

# Run tests affected by changes
python scripts/ci/adapters/test_router.py --router-report artifacts/router/router_summary.json --coverage --output test_results.json

# Analyze docstrings in changed files
python scripts/ci/adapters/docstring_router.py --router-report artifacts/router/router_summary.json --output docstring_summary.json

# Run RefactorGuard on changed files
python scripts/ci/adapters/refactor_guard_router.py --router-report artifacts/router/router_summary.json --output refactor_audit.json
```

### Integration Testing

To test the CI Router integration with all adapters:

```bash
# Run integration test with a specific test file
python scripts/ci/test_ci_router_integration.py --test-file scripts/refactor/parsers/docstring_parser.py

# Clean up temporary files after testing
python scripts/ci/test_ci_router_integration.py --clean
```

## Configuration

The CI Router is configured through the `scripts/ci/router_config.json` file. This file defines:

1. **File Patterns**: Patterns used to match files for different tasks
2. **Tasks**: CI tasks that can be run, with their dependencies and affected patterns

### Adding a New Task

To add a new CI task:

1. Add a new entry to the `tasks` section in `router_config.json`:

```json
"new_task": {
  "name": "new_task",
  "command": "python scripts/your_script.py --args",
  "description": "Description of the task",
  "affected_by": ["pattern1", "pattern2"],
  "always_run": false,
  "requires": ["other_task"],
  "output_files": ["output.json"]
}
```

2. Add any new file patterns to the `file_patterns` section:

```json
"pattern1": ["*.ext", "path/to/files/"]
```

3. Update the GitHub Actions workflow to include the new task.

## GitHub Actions Integration

The CI Router integrates with GitHub Actions through the `.github/workflows/ci_router.yml` file. This workflow:

1. Runs the router to determine which tasks to execute
2. Sets output variables for each task
3. Conditionally runs subsequent jobs based on those outputs

### Advantages

- **Faster CI Execution**: Only runs relevant jobs
- **Reduced Resource Usage**: Saves CI minutes and computational resources
- **Detailed Reports**: Provides comprehensive information about what changed and what was tested
- **Flexible Configuration**: Easily adaptable to different project structures

## Troubleshooting

If you encounter issues with the CI Router:

1. Run with `--verbose` flag for detailed output
2. Check the router report (`router_summary.json`) for information about detected changes
3. Run the integration test to verify all components are working correctly
4. Ensure that git is properly configured in your CI environment

## Best Practices

1. **Keep Configuration Updated**: Ensure new file types or directories are added to pattern definitions
2. **Use Meaningful Task Names**: Task names should clearly indicate their purpose
3. **Define Dependencies Correctly**: Ensure task dependencies are properly specified
4. **Regular Integration Testing**: Run integration tests when updating router components