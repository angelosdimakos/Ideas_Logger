import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from dashboard.data_loader import load_artifact
from dashboard.metrics import (
    compute_executive_summary,
    get_low_coverage_modules,
    coverage_by_module,
    compute_severity,
    compute_severity_df,
    build_prod_to_tests_df,
    severity_distribution,
)
from dashboard.ai_integration import AIIntegration
from scripts.ai.ai_summarizer import AISummarizer
from scripts.config.config_manager import ConfigManager

file_limit = 30

def init_artifacts_dir(default_dir: str = "artifacts") -> str:
    return default_dir if os.path.isdir(default_dir) else "."

artifacts_dir = init_artifacts_dir()
merged_data = load_artifact(os.path.join(artifacts_dir, "merged_report.json"))
strictness_data = load_artifact(os.path.join(artifacts_dir, "final_strictness_report.json"))

st.set_page_config(page_title="CI Audit Dashboard", layout="wide")
st.title("\U0001F4CA CI Audit Dashboard")

config = ConfigManager.load_config()
summarizer = AISummarizer()
ai = AIIntegration(config, summarizer)

summary = compute_executive_summary(merged_data, strictness_data)
for i, (label, val) in enumerate(summary.items()):
    if i % 3 == 0:
        cols = st.columns(3)
    cols[i % 3].metric(label.replace("_", " ").title(), val if isinstance(val, str) else str(val))

st.markdown("---")

with st.expander("\U0001F4DA AI Report Summary", expanded=True):
    if "audit_summary" not in st.session_state:
        st.session_state["audit_summary"] = ""
    if st.button("Generate AI Summary"):
        low_cov = get_low_coverage_modules(strictness_data)
        metrics_ctx = (
            f"Total Tests: {summary['total_tests']}; "
            f"Avg Strictness: {summary['avg_strictness']}; "
            f"Avg Severity: {summary['avg_severity']}; "
            f"Overall Coverage: {summary['overall_coverage']}%"
        ) + "; ".join(f"{m}: {cov*100:.1f}%" for m, cov in low_cov)
        st.session_state["audit_summary"] = ai.generate_audit_summary(metrics_ctx)
    if st.session_state["audit_summary"]:
        st.success("AI summary generated!")
        st.write(st.session_state["audit_summary"])

st.markdown("---")

with st.expander("\U0001F4C8 Coverage by Module", expanded=True):
    cov_list = coverage_by_module(merged_data)
    if cov_list:
        modules, values = zip(*cov_list)
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(modules, values)
        ax.set_xlabel("Coverage (%)")
        ax.set_xlim(0, 100)
        ax.bar_label(bars, fmt="%.1f%%", padding=5)
        ax.invert_yaxis()
        st.pyplot(fig)
    else:
        st.info("No coverage data available.")

st.markdown("---")

with st.expander("\U0001F916 Refactor Advisor", expanded=True):
    if "refactor_suggestions" not in st.session_state:
        st.session_state["refactor_suggestions"] = None
        st.session_state["offender_df"] = None
    refactor_limit = st.slider("Number of files to analyze:", 5, 50, 30, step=5, key="refactor_limit")
    if st.button("Generate Refactor Suggestions"):
        suggestions, offenders = ai.generate_refactor_advice(merged_data, limit=refactor_limit)
        st.session_state["refactor_suggestions"] = suggestions
        df = pd.DataFrame([
            {
                "File": os.path.basename(fp),
                "Severity Score": score,
                "Mypy Errors": len(errors),
                "Lint Issues": lint_issues,
                "Complexity": cx,
                "Coverage": cov,
            }
            for fp, score, errors, lint_issues, cx, cov in offenders
        ])
        st.session_state["offender_df"] = df
    if st.session_state["refactor_suggestions"]:
        st.success("Refactor suggestions generated!")
        st.markdown(st.session_state["refactor_suggestions"])
    if st.session_state.get("offender_df") is not None:
        st.dataframe(st.session_state["offender_df"].style.background_gradient(subset=["Severity Score"]))

st.markdown("---")

with st.expander("Get AI-Powered Recommendations", expanded=True):
    if "strategic_recommendations" not in st.session_state:
        st.session_state["strategic_recommendations"] = ""
    if st.button("Generate Strategic Recommendations"):
        st.session_state["strategic_recommendations"] = ai.generate_strategic_recommendations(merged_data, limit=file_limit)
    if st.session_state["strategic_recommendations"]:
        st.markdown(st.session_state["strategic_recommendations"])

st.markdown("---")
