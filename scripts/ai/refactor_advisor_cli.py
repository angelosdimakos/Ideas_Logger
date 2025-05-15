"""
Unified Code Assistant - A chatbot that integrates various code analysis modules
to provide comprehensive insights and recommendations.

This module serves as the main entry point for interacting with the code analysis system.
It coordinates between different specialized modules to:
1. Analyze code quality metrics
2. Identify risky files
3. Provide refactoring recommendations
4. Generate docstring summaries
5. Offer strategic improvement plans

The assistant follows a chain-of-thought approach, transparently showing the steps
it takes to arrive at recommendations.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

# Import the specialized modules
from scripts.ai.ai_summarizer import AISummarizer
from scripts.ai.llm_router import apply_persona
from scripts.ai import llm_refactor_advisor as advisor
from scripts.ai import llm_optimization as optim
from scripts.ai import module_docstring_summarizer as docsum
from scripts.ci_analyzer.metrics_summary import generate_metrics_summary
from scripts.config.config_manager import ConfigManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class UnifiedCodeAssistant:
    """
    A unified interface for interacting with code analysis modules and generating insights.

    This class coordinates the flow of information between modules to create a coherent
    chain-of-thought analysis process.
    """

    def __init__(self, report_path: str, config=None):
        """
        Initialize the Unified Code Assistant.

        Args:
            report_path (str): Path to the code analysis report JSON file
            config: Optional configuration object
        """
        self.report_path = report_path
        self.config = config or ConfigManager.load_config()
        self.summarizer = AISummarizer()
        self.report_data = self._load_report(report_path)

        # Ensure summary_metrics is a dictionary with expected keys
        metrics = generate_metrics_summary(self.report_data)
        if isinstance(metrics, str):
            # Parse string metrics into a dictionary if needed
            self.summary_metrics = {
                "total_tests": "N/A",
                "avg_strictness": "N/A",
                "avg_severity": "N/A",
                "coverage": "N/A",
                "missing_docs": "N/A",
                "high_severity_tests": "N/A",
                "medium_severity_tests": "N/A",
                "low_severity_tests": "N/A"
            }
        else:
            self.summary_metrics = metrics

        self.top_offenders = None
        self.severity_data = None

        logger.info(f"Initialized Unified Code Assistant with report: {report_path}")

    def _load_report(self, path: str) -> Dict[str, Any]:
        """Load a JSON report from the specified file path."""
        logger.info(f"Loading report from {path}")
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load report: {e}")
            raise

    def analyze_codebase(self, top_n: int = 20, path_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform a comprehensive analysis of the codebase.

        Args:
            top_n (int): Number of top files to analyze
            path_filter (Optional[str]): Optional filter to focus on specific file paths

        Returns:
            Dict[str, Any]: Analysis results including top offenders and severity data
        """
        logger.info(f"Analyzing codebase, focusing on top {top_n} files")

        # Extract top offenders
        self.top_offenders = advisor.extract_top_offenders(self.report_data, top_n=top_n)

        # Compute severity for each file
        self.severity_data = [
            optim.compute_severity(fp, self.report_data[fp])
            for fp, *_ in self.top_offenders
            if (not path_filter) or (path_filter in fp)
        ]

        return {
            "top_offenders": self.top_offenders,
            "severity_data": self.severity_data,
            "summary_metrics": self.summary_metrics
        }

    def generate_strategic_recommendations(self, limit: int = 20) -> str:
        """
        Generate strategic recommendations for improving code quality.

        Args:
            limit (int): Maximum number of files to consider

        Returns:
            str: Strategic recommendations from the AI assistant
        """
        if not self.severity_data:
            self.analyze_codebase(top_n=limit)

        logger.info("Generating strategic recommendations")

        # Extract more detailed information about the codebase structure
        file_types = {}
        for fp, *_ in self.top_offenders:
            # Get file extension
            ext = Path(fp).suffix
            if ext not in file_types:
                file_types[ext] = 0
            file_types[ext] += 1

        # Determine common patterns in the codebase
        module_patterns = {}
        for fp, *_ in self.top_offenders:
            basename = Path(fp).stem
            # Look for common prefixes or naming patterns
            parts = basename.split('_')
            if parts:
                prefix = parts[0]
                if prefix not in module_patterns:
                    module_patterns[prefix] = 0
                module_patterns[prefix] += 1

        # Build the strategic recommendations prompt
        strategic_prompt = optim.build_strategic_recommendations_prompt(
            severity_data=self.severity_data,
            summary_metrics=self.summary_metrics,
            limit=limit
        )

        # Apply persona to the prompt
        persona_prompt = apply_persona(strategic_prompt, self.config.persona)

        # Generate the recommendations using the AI summarizer
        return self.summarizer.summarize_entry(
            persona_prompt,
            subcategory="Tooling & Automation"
        )

    def generate_module_summaries(self, path_filter: Optional[str] = None) -> Dict[str, str]:
        """
        Generate summaries of module functionality based on docstrings.

        Args:
            path_filter (Optional[str]): Optional filter to focus on specific file paths

        Returns:
            Dict[str, str]: Dictionary mapping file paths to their summaries
        """
        logger.info("Generating module summaries")

        summaries = {}
        for file_path, data in self.report_data.items():
            if path_filter and path_filter not in file_path:
                continue

            funcs = data.get("docstrings", {}).get("functions", [])
            if not funcs:
                continue

            summary = docsum.summarize_module(
                file_path, funcs, self.summarizer, self.config
            )
            summaries[file_path] = summary

        return summaries

    def answer_query(self, query: str) -> str:
        """
        Answer a user query about the codebase using chain-of-thought processing.

        Args:
            query (str): The user's question

        Returns:
            str: The assistant's response
        """
        logger.info(f"Processing query: {query}")

        # If analysis hasn't been run yet, do it now
        if not self.top_offenders:
            self.analyze_codebase()

        # Build a contextual prompt based on the query and analysis results
        prompt = self._build_contextual_prompt(query)

        # Generate the response using the AI summarizer
        return self.summarizer.summarize_entry(
            prompt,
            subcategory="Tooling & Automation"
        )

    def _build_contextual_prompt(self, query: str) -> str:
        """
        Build a contextual prompt for answering the user's query.

        Args:
            query (str): The user's question

        Returns:
            str: A prompt tailored to the query and available analysis data
        """
        # Create a summary of top offenders
        offender_summary = "\n".join([
            f"- `{fp}`: MyPy={len(errors)}, Lint={lint}, "
            f"Cx={cx}, Coverage={cov * 100:.1f}%"
            for fp, _, errors, lint, cx, cov in self.top_offenders[:5]
        ])

        # Base prompt
        prompt = f"""
You are an AI assistant helping engineers improve their Python codebase.

Here is a summary of the most risky files:
{offender_summary}

Overall metrics:
{self.summary_metrics}

Now answer the developer's question below using this context, showing your reasoning step by step:

Q: {query}
        """

        return apply_persona(prompt.strip(), self.config.persona)


def chat_mode(assistant: UnifiedCodeAssistant) -> None:
    """
    Run the assistant in interactive chat mode.

    Args:
        assistant (UnifiedCodeAssistant): The initialized assistant
    """
    print("\n=== Code Assistant Chat Mode ===")
    print("💬 Ask anything about your codebase, e.g:")
    print("   - What's the worst file?")
    print("   - What refactoring should we prioritize?")
    print("   - Which functions need tests?")
    print("   - Suggest a plan to improve our code quality")
    print("\nType 'exit' or 'quit' to end the conversation.\n")

    # First run the analysis to prepare data
    assistant.analyze_codebase()

    while True:
        query = input("\n❓> ")
        if query.strip().lower() in {"exit", "quit"}:
            break

        print("\n🧠 Processing your question...\n")
        response = assistant.answer_query(query)
        print(f"\n🤖 {response}\n")


def main() -> None:
    """Main entry point for the Unified Code Assistant CLI."""
    parser = argparse.ArgumentParser(
        description="Unified Code Assistant - Analyze code quality and get AI recommendations"
    )
    parser.add_argument("report_json", help="Path to merged_report.json")
    parser.add_argument(
        "--mode",
        choices=["chat", "analyze", "strategic", "summaries"],
        default="chat",
        help="Operation mode (default: chat)"
    )
    parser.add_argument("--top", type=int, default=20, help="Number of worst files to analyze")
    parser.add_argument("--persona", default="mentor", help="Assistant persona (mentor, reviewer, planner)")
    parser.add_argument("--path-filter", help="Filter to specific file paths")
    parser.add_argument("--output", "-o", help="Output file path for results")
    args = parser.parse_args()

    # Configure persona
    config = ConfigManager.load_config()
    config.persona = args.persona

    # Initialize the assistant
    assistant = UnifiedCodeAssistant(args.report_json, config)

    # Execute the requested mode
    if args.mode == "chat":
        chat_mode(assistant)

    elif args.mode == "analyze":
        results = assistant.analyze_codebase(top_n=args.top, path_filter=args.path_filter)
        output = json.dumps(results, indent=2)

        if args.output:
            Path(args.output).write_text(output)
            print(f"Analysis results written to {args.output}")
        else:
            print(output)

    elif args.mode == "strategic":
        recommendations = assistant.generate_strategic_recommendations(limit=args.top)

        if args.output:
            Path(args.output).write_text(recommendations)
            print(f"Strategic recommendations written to {args.output}")
        else:
            print(recommendations)

    elif args.mode == "summaries":
        summaries = assistant.generate_module_summaries(path_filter=args.path_filter)
        output = "\n\n".join([f"## {path}\n\n{summary}" for path, summary in summaries.items()])

        if args.output:
            Path(args.output).write_text(output)
            print(f"Module summaries written to {args.output}")
        else:
            print(output)


if __name__ == "__main__":
    sys.exit(main())