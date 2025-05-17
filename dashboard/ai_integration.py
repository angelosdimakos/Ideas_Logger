import os
from typing import Any, Dict, List, Tuple

from scripts.ai.llm_router import get_prompt_template, apply_persona
from scripts.ai.module_docstring_summarizer import summarize_module
from scripts.unified_code_assistant.analysis import analyze_report
from scripts.unified_code_assistant.prompt_builder import build_contextual_prompt, build_enhanced_contextual_prompt
from scripts.unified_code_assistant.assistant_utils import get_issue_locations
from scripts.unified_code_assistant.module_summarizer import summarize_modules
from scripts.ai.llm_refactor_advisor import build_refactor_prompt
from scripts.unified_code_assistant import cli_entrypoint
import tempfile
import json

class AIIntegration:
    def __init__(self, config, summarizer):
        """
        Initializes the AIIntegration instance with configuration and summarizer objects.
        """
        self.config = config
        self.summarizer = summarizer

    def generate_audit_summary(self, metrics_context: str) -> str:
        """
        Generates an audit summary based on provided metrics context.
        
        Combines a persona-applied audit summary prompt with the given metrics context and uses the summarizer to produce a summary.
        	
        Args:
        	metrics_context: A string containing metrics or contextual information to be summarized.
        
        Returns:
        	A summary string generated from the combined prompt and metrics context.
        """
        prompt = get_prompt_template("Audit Summary", self.config)
        final_prompt = apply_persona(prompt, self.config.persona)
        enriched = final_prompt + "\n\n" + metrics_context
        return self.summarizer.summarize_entry(enriched, subcategory="Audit Summary")

    def generate_refactor_advice(self, merged_data, limit: int):
        """
        Generates refactoring advice based on analysis of the provided merged data.
        
        Analyzes the merged data to identify the top offenders for refactoring, constructs a contextual prompt, and uses the summarizer to generate actionable suggestions.
        
        Args:
        	merged_data: The combined data report to analyze for refactoring opportunities.
        	limit: The maximum number of top offenders to consider.
        
        Returns:
        	A tuple containing the refactor suggestion string and a list of the top offenders.
        """
        analysis = analyze_report(merged_data, top_n=limit)
        prompt = build_contextual_prompt(
            "What needs refactoring?",
            analysis["top_offenders"],
            analysis["summary_metrics"],
            self.config.persona
        )
        suggestion = self.summarizer.summarize_entry(prompt, subcategory="Refactor Advisor")
        return suggestion, analysis["top_offenders"]

    def generate_strategic_recommendations(self, merged_data, limit: int = 30):
        """
        Generates strategic recommendations by invoking an external CLI assistant with the provided merged data.
        
        Args:
            merged_data: The data to be analyzed for generating recommendations.
            limit: The maximum number of top recommendations to return (default is 30).
        
        Returns:
            The output string produced by the CLI assistant containing strategic recommendations.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(merged_data, f)
            f.flush()
            args = ["assistant", f.name, "--mode", "strategic", "--top", str(limit), "--persona", self.config.persona]
            return cli_entrypoint.call_cli_for_output(args)

    def chat_general(self, user_query, merged_data):
        """
        Generates a risk-focused AI chat response based on a user query and analyzed code metrics.
        
        Args:
            user_query: The user's question or prompt for the AI assistant.
            merged_data: Aggregated code analysis data to inform the response.
        
        Returns:
            A summary string providing risk-related advice or insights in response to the user query.
        """
        analysis = analyze_report(merged_data)
        prompt = build_contextual_prompt(user_query, analysis["top_offenders"], analysis["summary_metrics"], self.config.persona)
        return self.summarizer.summarize_entry(prompt, subcategory="Risk Advisor Chat")

    def chat_code(self, file_path, complexity_info, lint_info, user_query):
        """
        Generates an AI-driven analysis and recommendation summary for a specific code file.
        
        Builds a detailed context using the file's complexity, linting information, issue locations, placeholder module summary, and user query. Produces a summarized response with code analysis and actionable recommendations.
        """
        offender_tuple = (file_path, None, [], 1, 5, 0.8)
        report_data = {
            file_path: {
                "coverage": {"complexity": complexity_info},
                "linting": {"quality": lint_info}
            }
        }

        file_issues = {
            file_path: get_issue_locations(file_path, report_data)
        }

        module_summaries = {
            file_path: "Module summary not available"
        }

        refactor_prompt = build_refactor_prompt(
            [offender_tuple],
            self.config,
            subcategory="Refactor Advisor",
            verbose=False,
            limit=1
        )
        file_recommendations = {
            file_path: self.summarizer.summarize_entry(refactor_prompt, subcategory="Tooling & Automation")
        }

        contextual_prompt = build_enhanced_contextual_prompt(
            user_query,
            [offender_tuple],
            summary_metrics={"coverage": "unknown"},
            module_summaries=module_summaries,
            file_issues=file_issues,
            file_recommendations=file_recommendations,
            persona=self.config.persona
        )

        return self.summarizer.summarize_entry(contextual_prompt, subcategory="Code Analysis")

    def chat_doc(self, module_path, funcs):
        """
        Generates a summary of a module and its functions using the configured summarizer.
        
        Args:
            module_path: Path to the module to be summarized.
            funcs: List of functions within the module to include in the summary.
        
        Returns:
            A summary string describing the module and its functions.
        """
        return summarize_module(module_path, funcs, self.summarizer, self.config)
