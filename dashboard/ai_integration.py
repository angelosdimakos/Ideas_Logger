# File: scripts/dashboard/ai_integration.py

"""
Module: scripts/dashboard/ai_integration.py
Encapsulates all AI-related prompts, summaries, and LLM integrations
for the CI Audit Dashboard.
"""

import os
from typing import Any, Dict, List, Tuple

from scripts.ai.ai_summarizer import AISummarizer
from scripts.ai.llm_router import get_prompt_template, apply_persona
from scripts.ai.llm_refactor_advisor import extract_top_offenders, build_refactor_prompt
from scripts.ai.chat_refactor import build_contextual_prompt
from scripts.ai.module_docstring_summarizer import summarize_module
from scripts.ai.llm_optimization import build_strategic_recommendations_prompt


class AIIntegration:
    def __init__(self, config: Any, summarizer: AISummarizer):
        self.config = config
        self.summarizer = summarizer

    def generate_audit_summary(self, metrics_context: str) -> str:
        """
        Generate a high-level audit summary using the AI summarizer.
        `metrics_context` should be a formatted string of key metrics.
        """
        prompt = get_prompt_template("Audit Summary", self.config)
        final_prompt = apply_persona(prompt, self.config.persona)
        enriched = final_prompt + "\n\n" + metrics_context
        return self.summarizer.summarize_entry(
            enriched,
            subcategory="Audit Summary"
        )

    def generate_refactor_advice(
        self,
        merged_data: Dict[str, Any],
        limit: int
    ) -> Tuple[str, List[Tuple[str, float, List[str], int, int, float]]]:
        """
        Extract top offenders and build refactor suggestions.
        Returns a tuple of (suggestions_text, offenders_list).
        `offenders_list` items are tuples:
          (file_path, score, errors, lint_issues, complexity, coverage)
        """
        offenders = extract_top_offenders(merged_data, top_n=limit)
        prompt = build_refactor_prompt(offenders, self.config, verbose=False, limit=limit)
        suggestions = self.summarizer.summarize_entry(
            prompt,
            subcategory="Refactor Advisor"
        )
        return suggestions, offenders

    def generate_strategic_recommendations(
        self,
        severity_data: List[Dict[str, Any]],
        summary_metrics: Dict[str, Any],
        low_cov_context: str
    ) -> str:
        """
        Build and run the strategic recommendations prompt.
        `low_cov_context` should list top low-coverage modules.
        """
        base_prompt = build_strategic_recommendations_prompt(
            severity_data,
            summary_metrics,
            limit=summary_metrics.get("limit", 30)
        )
        enriched = base_prompt + "\n\n" + low_cov_context
        return self.summarizer.summarize_entry(
            enriched,
            subcategory="Strategic Recommendations"
        )

    def chat_general(self, user_query: str, merged_data: Dict[str, Any]) -> str:
        """
        Chat interface for general questions about code risk/quality.
        """
        prompt = build_contextual_prompt(user_query, merged_data, self.config)
        return self.summarizer.summarize_entry(
            prompt,
            subcategory="Risk Advisor Chat"
        )

    def chat_code(
        self,
        file_path: str,
        complexity_info: Dict[str, Any],
        lint_info: Dict[str, Any],
        user_query: str
    ) -> str:
        """
        Chat interface for file-specific code questions.
        """
        details = (
            f"Analyze the file '{os.path.basename(file_path)}' with the following:\n"
            f"- MyPy Errors: {len(lint_info.get('mypy', {}).get('errors', []))}\n"
            f"- Pydocstyle Issues: {sum(len(v) for v in lint_info.get('pydocstyle', {}).get('functions', {}).values())}\n"
            f"- Function Count: {len(complexity_info)}\n\n"
            f"User Question: {user_query}"
        )
        return self.summarizer.summarize_entry(details, subcategory="Code Analysis")

    def chat_doc(
        self,
        module_path: str,
        funcs: List[Dict[str, Any]]
    ) -> str:
        """
        Chat interface for module docstring summarization.
        """
        return summarize_module(module_path, funcs, self.summarizer, self.config)
