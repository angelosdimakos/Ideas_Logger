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
        self.config = config
        self.summarizer = summarizer

    def generate_audit_summary(self, metrics_context: str) -> str:
        prompt = get_prompt_template("Audit Summary", self.config)
        final_prompt = apply_persona(prompt, self.config.persona)
        enriched = final_prompt + "\n\n" + metrics_context
        return self.summarizer.summarize_entry(enriched, subcategory="Audit Summary")

    def generate_refactor_advice(self, merged_data, limit: int):
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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(merged_data, f)
            f.flush()
            args = ["assistant", f.name, "--mode", "strategic", "--top", str(limit), "--persona", self.config.persona]
            return cli_entrypoint.call_cli_for_output(args)

    def chat_general(self, user_query, merged_data):
        analysis = analyze_report(merged_data)
        prompt = build_contextual_prompt(user_query, analysis["top_offenders"], analysis["summary_metrics"], self.config.persona)
        return self.summarizer.summarize_entry(prompt, subcategory="Risk Advisor Chat")

    def chat_code(self, file_path, complexity_info, lint_info, user_query):
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
        return summarize_module(module_path, funcs, self.summarizer, self.config)
