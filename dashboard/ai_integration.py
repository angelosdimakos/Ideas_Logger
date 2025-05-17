# File: scripts/dashboard/ai_integration.py

"""
Module: scripts/dashboard/ai_integration.py
Encapsulates all AI-related prompts, summaries, and LLM integrations
for the CI Audit Dashboard.
"""

import os
from typing import Any, Dict, List, Tuple

from scripts.ai.llm_router import get_prompt_template, apply_persona
from scripts.ai.chat_refactor import build_contextual_prompt
from scripts.ai.module_docstring_summarizer import summarize_module
from scripts.unified_code_assistant.analysis import analyze_report
from scripts.unified_code_assistant.strategy import generate_strategy
from scripts.unified_code_assistant.prompt_builder import build_contextual_prompt

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

    def generate_strategic_recommendations(self, severity_data, summary_metrics, low_cov_context):
        prompt = generate_strategy(
            severity_data=severity_data,
            summary_metrics=summary_metrics,
            limit=summary_metrics.get("limit", 30),
            persona=self.config.persona,
            summarizer=self.summarizer
        )
        return prompt  # already string output

    def chat_general(self, user_query, merged_data):
        analysis = analyze_report(merged_data)
        prompt = build_contextual_prompt(user_query, analysis["top_offenders"], analysis["summary_metrics"], self.config.persona)
        return self.summarizer.summarize_entry(prompt, subcategory="Risk Advisor Chat")

    def chat_code(self, file_path, complexity_info, lint_info, user_query):
        details = (
            f"Analyze the file '{os.path.basename(file_path)}' with the following:\n"
            f"- MyPy Errors: {len(lint_info.get('mypy', {}).get('errors', []))}\n"
            f"- Pydocstyle Issues: {sum(len(v) for v in lint_info.get('pydocstyle', {}).get('functions', {}).values())}\n"
            f"- Function Count: {len(complexity_info)}\n\n"
            f"User Question: {user_query}"
        )
        return self.summarizer.summarize_entry(details, subcategory="Code Analysis")

    def chat_doc(self, module_path, funcs):
        return summarize_module(module_path, funcs, self.summarizer, self.config)

