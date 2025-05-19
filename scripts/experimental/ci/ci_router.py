#!/usr/bin/env python3
"""
CI Router
=========
Intelligent CI execution router that analyzes git diffs to determine which CI tasks to run.

Key features:
- Detects changed files using git diff
- Maps file paths to specific CI tasks
- Generates granular reports based on affected code areas
- Optimizes CI workflow by only running necessary tools

Usage:
    python ci_router.py --base-branch main --report-dir artifacts/router
    python ci_router.py --changed-files-only --report-dir artifacts/router
"""

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Ensure the repo root is on sys.path so we can import project modules
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

# Import relevant project utilities
import scripts.utils.git_utils as git_utils


@dataclass
class CITask:
    """Represents a CI task that can be conditionally executed."""
    name: str
    command: str
    description: str
    affected_by: List[str] = field(default_factory=list)  # File patterns that trigger this task
    always_run: bool = False
    requires: List[str] = field(default_factory=list)  # Tasks that must run before this one
    output_files: List[str] = field(default_factory=list)  # Expected output file paths


@dataclass
class RouterConfig:
    """Configuration for the CI Router."""
    tasks: Dict[str, CITask] = field(default_factory=dict)
    file_patterns: Dict[str, List[str]] = field(default_factory=dict)
    report_dir: str = "artifacts/router"
    base_branch: str = "main"
    verbose: bool = False


class CIRouter:
    """
    Main CI router that determines which CI tasks to run based on changed files.
    """

    def __init__(self, config: RouterConfig):
        """Initialize the CI router with the provided configuration."""
        self.config = config
        self.changed_files: List[str] = []
        self.tasks_to_run: Set[str] = set()
        self.task_results: Dict[str, Dict] = {}

        # Create report directory if it doesn't exist
        os.makedirs(self.config.report_dir, exist_ok=True)

    def detect_changed_files(self, base_branch: Optional[str] = None) -> List[str]:
        """
        Detect changed files using git diff against the specified base branch.

        Args:
            base_branch: The base branch to compare against (e.g., 'main')

        Returns:
            List of changed file paths
        """
        branch = base_branch or self.config.base_branch
        try:
            self.changed_files = git_utils.get_changed_files(f"origin/{branch}")
            if self.config.verbose:
                print(f"Detected {len(self.changed_files)} changed files")
                for file in self.changed_files[:10]:  # Limit output for brevity
                    print(f"  - {file}")
                if len(self.changed_files) > 10:
                    print(f"  ... and {len(self.changed_files) - 10} more")

            return self.changed_files
        except Exception as e:
            print(f"Error detecting changed files: {e}")
            return []

    def map_files_to_tasks(self) -> Dict[str, List[str]]:
        """
        Map changed files to the CI tasks they affect.

        Returns:
            Dictionary mapping task names to lists of affected files
        """
        task_file_map = defaultdict(list)

        for file_path in self.changed_files:
            matched_tasks = self._get_tasks_for_file(file_path)
            for task_name in matched_tasks:
                task_file_map[task_name].append(file_path)

        # Add always-run tasks
        for task_name, task in self.config.tasks.items():
            if task.always_run:
                self.tasks_to_run.add(task_name)

        # Add tasks based on file changes
        for task_name in task_file_map:
            self.tasks_to_run.add(task_name)

        # Add required dependent tasks
        self._add_dependent_tasks()

        if self.config.verbose:
            print(f"Selected {len(self.tasks_to_run)} tasks to run:")
            for task in self.tasks_to_run:
                print(f"  - {task}: {len(task_file_map.get(task, []))} affected files")

        return dict(task_file_map)

    def _get_tasks_for_file(self, file_path: str) -> List[str]:
        """
        Get the tasks affected by changes to a specific file.

        Args:
            file_path: Path to the changed file

        Returns:
            List of task names affected by this file
        """
        affected_tasks = []

        for task_name, task in self.config.tasks.items():
            for pattern in task.affected_by:
                # If the pattern is in the file_patterns dictionary, check against those patterns
                if pattern in self.config.file_patterns:
                    pattern_list = self.config.file_patterns[pattern]
                    if any(self._match_pattern(file_path, p) for p in pattern_list):
                        affected_tasks.append(task_name)
                        break
                # Otherwise, check against the pattern directly
                elif self._match_pattern(file_path, pattern):
                    affected_tasks.append(task_name)
                    break

        return affected_tasks

    def _match_pattern(self, file_path: str, pattern: str) -> bool:
        """
        Check if a file path matches a pattern.

        Args:
            file_path: Path to the file
            pattern: Pattern to match against

        Returns:
            True if the file matches the pattern, False otherwise
        """
        # Direct prefix match
        if pattern.endswith('/') and file_path.startswith(pattern):
            return True
        # Exact file match
        if pattern == file_path:
            return True
        # Extension match
        if pattern.startswith('*.') and file_path.endswith(pattern[1:]):
            return True
        # Path component match
        if pattern.startswith('/') and pattern[1:] in file_path.split('/'):
            return True
        # Directory contains match
        if '/' in pattern and pattern in file_path:
            return True
        # Glob pattern match
        if '*' in pattern or '?' in pattern:
            import fnmatch
            return fnmatch.fnmatch(file_path, pattern)

        return False

    def _add_dependent_tasks(self) -> None:
        """Add required dependent tasks to the tasks_to_run set."""
        queue = list(self.tasks_to_run)
        visited = set(queue)

        while queue:
            task_name = queue.pop(0)
            if task_name not in self.config.tasks:
                continue

            for req in self.config.tasks[task_name].requires:
                if req not in visited:
                    self.tasks_to_run.add(req)
                    queue.append(req)
                    visited.add(req)

    def run_tasks(self) -> Dict[str, Dict]:
        """
        Run all selected CI tasks.

        Returns:
            Dictionary mapping task names to their results
        """
        for task_name in sorted(self.tasks_to_run):
            task = self.config.tasks.get(task_name)
            if not task:
                print(f"Warning: Task '{task_name}' not found in configuration")
                continue

            print(f"Running task: {task_name} - {task.description}")
            result = self._run_task(task)
            self.task_results[task_name] = result

            # Save individual task result
            results_file = Path(self.config.report_dir) / f"{task_name}_result.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)

        return self.task_results

    def _run_task(self, task: CITask) -> Dict:
        """
        Run a single CI task.

        Args:
            task: The CITask to run

        Returns:
            Dictionary containing the task result
        """
        result = {
            "name": task.name,
            "description": task.description,
            "command": task.command,
            "status": "running",
            "output": "",
            "exit_code": None,
            "artifacts": []
        }

        try:
            # Run the command and capture output
            process = subprocess.run(
                task.command,
                shell=True,
                capture_output=True,
                text=True,
                check=False
            )

            result["output"] = process.stdout + process.stderr
            result["exit_code"] = process.returncode
            result["status"] = "success" if process.returncode == 0 else "failure"

            # Check for expected output files
            for output_file in task.output_files:
                if os.path.exists(output_file):
                    result["artifacts"].append(output_file)

            return result
        except Exception as e:
            result["status"] = "error"
            result["output"] = str(e)
            return result

    def generate_report(self) -> Dict:
        """
        Generate a comprehensive report of the CI run.

        Returns:
            Dictionary containing the complete CI report
        """
        summary = {
            "changed_files": self.changed_files,
            "tasks_run": len(self.task_results),
            "successful_tasks": sum(1 for r in self.task_results.values() if r["status"] == "success"),
            "failed_tasks": sum(1 for r in self.task_results.values() if r["status"] in ["failure", "error"]),
            "task_results": self.task_results
        }

        # Save the summary report
        summary_file = Path(self.config.report_dir) / "router_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        # Generate markdown report
        self._generate_markdown_report(summary)

        return summary

    def _generate_markdown_report(self, summary: Dict) -> None:
        """
        Generate a markdown report from the CI summary.

        Args:
            summary: The CI summary dictionary
        """
        markdown_file = Path(self.config.report_dir) / "router_report.md"

        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write("# CI Router Report\n\n")

            # Summary section
            f.write("## Summary\n\n")
            f.write(f"- **Changed Files:** {len(summary['changed_files'])}\n")
            f.write(f"- **Tasks Run:** {summary['tasks_run']}\n")
            f.write(f"- **Successful Tasks:** {summary['successful_tasks']}\n")
            f.write(f"- **Failed Tasks:** {summary['failed_tasks']}\n\n")

            # Changed files section
            f.write("## Changed Files\n\n")
            if summary['changed_files']:
                for file in summary['changed_files']:
                    f.write(f"- `{file}`\n")
            else:
                f.write("No files changed.\n")
            f.write("\n")

            # Task results section
            f.write("## Task Results\n\n")
            for task_name, result in summary['task_results'].items():
                status_emoji = "✅" if result["status"] == "success" else "❌"
                f.write(f"### {status_emoji} {task_name}\n\n")
                f.write(f"**Description:** {result['description']}\n\n")
                f.write(f"**Status:** {result['status']}\n\n")

                if result["artifacts"]:
                    f.write("**Artifacts:**\n\n")
                    for artifact in result["artifacts"]:
                        f.write(f"- [{os.path.basename(artifact)}]({artifact})\n")
                    f.write("\n")

                if result["output"]:
                    f.write("**Output:**\n\n")
                    f.write("```\n")
                    # Limit output to avoid huge files
                    output_lines = result["output"].splitlines()
                    if len(output_lines) > 20:
                        output_excerpt = "\n".join(output_lines[:10] + ["..."] + output_lines[-10:])
                        f.write(f"{output_excerpt}\n")
                    else:
                        f.write(f"{result['output']}\n")
                    f.write("```\n\n")


def create_default_config() -> RouterConfig:
    """
    Create the default router configuration based on the project structure.

    Returns:
        RouterConfig with default settings for the project
    """
    # Define file pattern categories
    file_patterns = {
        "python": ["*.py"],
        "tests": ["tests/", "*/test_*.py"],
        "documentation": ["docs/", "*.md", "README.md"],
        "ci": [".github/", "*.yml"],
        "refactor": ["scripts/refactor/"]
    }

    # Define CI tasks
    tasks = {
        "lint": CITask(
            name="lint",
            command="python scripts/refactor/lint_report_pkg/lint_report_cli.py --audit artifacts/router/linting_report.json",
            description="Run linter checks on changed files",
            affected_by=["python"],
            output_files=["artifacts/router/linting_report.json"]
        ),
        "test": CITask(
            name="test",
            command="pytest -c pytest.ini --cov=scripts --cov-config=.coveragerc --cov-report=json:artifacts/router/coverage.json",
            description="Run tests affected by changed files",
            affected_by=["python", "tests"],
            output_files=["artifacts/router/coverage.json"]
        ),
        "docstring": CITask(
            name="docstring",
            command="python scripts/refactor/parsers/docstring_parser.py --json --path scripts",
            description="Generate docstring summary for changed files",
            affected_by=["python"],
            output_files=["docstring_summary.json"]
        ),
        "refactor_guard": CITask(
            name="refactor_guard",
            command="python scripts/refactor/refactor_guard_cli.py --refactored scripts --all --json --output artifacts/router/refactor_audit.json --coverage-path artifacts/router/coverage.json",
            description="Run RefactorGuard on changed files",
            affected_by=["python"],
            requires=["test"],
            output_files=["artifacts/router/refactor_audit.json"]
        ),
        "strictness_analysis": CITask(
            name="strictness_analysis",
            command="python scripts/refactor/test_discovery.py --tests tests --output artifacts/router/test_report.json && python scripts/refactor/strictness_analyzer.py --test-report artifacts/router/test_report.json --audit artifacts/router/refactor_audit.json --output artifacts/router/final_strictness_report.json",
            description="Run strictness analysis on affected tests",
            affected_by=["python", "tests"],
            requires=["test", "refactor_guard"],
            output_files=["artifacts/router/test_report.json", "artifacts/router/final_strictness_report.json"]
        ),
        "merge_reports": CITask(
            name="merge_reports",
            command="python scripts/refactor/merge_audit_reports.py --docstrings docstring_summary.json --coverage artifacts/router/refactor_audit.json --linting artifacts/router/linting_report.json -o artifacts/router/merged_report.json",
            description="Merge all reports into a comprehensive summary",
            requires=["lint", "docstring", "refactor_guard"],
            always_run=True,
            output_files=["artifacts/router/merged_report.json"]
        ),
        "severity_audit": CITask(
            name="severity_audit",
            command="python scripts/ci_analyzer/severity_audit.py --audit artifacts/router/merged_report.json --output artifacts/router/ci_severity_report.md",
            description="Generate severity audit report",
            requires=["merge_reports"],
            always_run=True,
            output_files=["artifacts/router/ci_severity_report.md"]
        )
    }

    return RouterConfig(tasks=tasks, file_patterns=file_patterns)


def main():
    """Main entry point for the CI Router."""
    parser = argparse.ArgumentParser(description="Run CI tasks based on changed files")
    parser.add_argument("--base-branch", default="main", help="Base branch to compare against")
    parser.add_argument("--report-dir", default="artifacts/router", help="Directory for reports")
    parser.add_argument("--changed-files-only", action="store_true", help="Only detect changed files and exit")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--config", help="Path to custom configuration JSON file")
    args = parser.parse_args()

    # Create configuration
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            # Convert the loaded JSON to RouterConfig format
            # (This is a simplified version - a real implementation would need more robust conversion)
            config = RouterConfig(
                file_patterns=config_data.get('file_patterns', {}),
                report_dir=args.report_dir,
                base_branch=args.base_branch,
                verbose=args.verbose
            )
            for task_name, task_data in config_data.get('tasks', {}).items():
                config.tasks[task_name] = CITask(**task_data)
    else:
        config = create_default_config()
        config.report_dir = args.report_dir
        config.base_branch = args.base_branch
        config.verbose = args.verbose

    # Initialize router
    router = CIRouter(config)

    # Detect changed files
    changed_files = router.detect_changed_files()

    # If only reporting changed files, exit now
    if args.changed_files_only:
        print(f"Detected {len(changed_files)} changed files:")
        for file in changed_files:
            print(f"  {file}")
        return 0

    # Map files to tasks and run selected tasks
    router.map_files_to_tasks()
    router.run_tasks()
    router.generate_report()

    print(f"CI Router completed. Reports saved to {args.report_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())