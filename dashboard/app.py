import os
import json
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from dashboard.data_loader import load_artifact, is_excluded
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

# ---------------------- Setup & Data Loading ----------------------

def init_artifacts_dir(default_dir: str = "artifacts") -> str:
    """Return the artifacts directory or fallback to current directory."""
    return default_dir if os.path.isdir(default_dir) else "."

artifacts_dir = init_artifacts_dir()
merged_data = load_artifact(os.path.join(artifacts_dir, "merged_report.json"))
strictness_data = load_artifact(os.path.join(artifacts_dir, "final_strictness_report.json"))

# ---------------------- Streamlit Configuration ----------------------

st.set_page_config(page_title="CI Audit Dashboard", layout="wide")
st.title("📊 CI Audit Dashboard")

# ---------------------- Initialize AI Integration ----------------------

config = ConfigManager.load_config()
summarizer = AISummarizer()
ai = AIIntegration(config, summarizer)

# ---------------------- Executive Summary ----------------------

summary = compute_executive_summary(merged_data, strictness_data)
col1, col2, col3 = st.columns(3)
col1.metric("Total Unique Tests", summary["total_tests"])
col2.metric("Avg Strictness", summary["avg_strictness"])
col3.metric("Avg Severity", summary["avg_severity"])
col4, col5, col6 = st.columns(3)
col4.metric("Production Modules", summary["prod_files"])
col5.metric("Overall Coverage", f"{summary['overall_coverage']}%")
col6.metric("Missing Docstrings", f"{summary['missing_doc_percent']}%")
st.markdown("---")

# ---------------------- AI-Powered Report Summary ----------------------

with st.expander("📚 AI Report Summary", expanded=True):
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

# ---------------------- Coverage by Module ----------------------

with st.expander("📈 Coverage by Module", expanded=True):
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

# ---------------------- 🤖 Refactor Advisor ----------------------

with st.expander("🤖 Refactor Advisor", expanded=True):
    if "refactor_suggestions" not in st.session_state:
        st.session_state["refactor_suggestions"] = None
        st.session_state["offender_df"] = None
    refactor_limit = st.slider(
        "Number of files to analyze:", 5, 50, 30, step=5, key="refactor_limit"
    )
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
        st.dataframe(
            st.session_state["offender_df"].style.background_gradient(
                subset=["Severity Score"]
            )
        )

st.markdown("---")

# ---------------------- 🔥 Top Risk Files ----------------------

with st.expander("🔥 Top Risk Files", expanded=True):
    risk_df = compute_severity_df(merged_data, compute_severity)
    if not risk_df.empty:
        st.dataframe(risk_df.head(10))
    else:
        st.info("No risk files.")

st.markdown("---")

# ---------------------- 🧩 Production Coverage View ----------------------

with st.expander("🧩 Production Coverage View", expanded=True):
    prod_df = build_prod_to_tests_df(strictness_data)
    if not prod_df.empty:
        st.dataframe(prod_df)
    else:
        st.info("No production coverage data.")

st.markdown("---")

# ---------------------- 📊 Severity Distribution ----------------------

with st.expander("📊 Severity Distribution", expanded=True):
    buckets = severity_distribution(strictness_data)
    labels, counts = zip(*buckets.items())
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, counts)
    for i, v in enumerate(counts):
        ax.text(i, v + 0.5, str(v), ha='center')
    st.pyplot(fig)
    st.markdown(f"Low: {buckets['Low']}, Medium: {buckets['Medium']}, High: {buckets['High']}")

st.markdown("---")

# ---------------------- 💬 Ask the AI Assistant ----------------------

with st.expander("💬 Ask the AI Assistant", expanded=True):
    tab1, tab2, tab3 = st.tabs(["General Questions", "Code Analysis", "Documentation"])

    with tab1:
        user_query = st.text_input("Ask about code risk/quality:", key="general_query")
        if st.button("Get AI Response", key="general_btn") and user_query:
            st.session_state["general_response"] = ai.chat_general(user_query, merged_data)
        if "general_response" in st.session_state:
            st.write(st.session_state["general_response"])

    with tab2:
        files = ["Select a file..."] + [os.path.basename(f) for f in merged_data.keys()]
        selected = st.selectbox("Select file:", files, key="code_file")
        code_query = st.text_input("Your question:", key="code_query")
        if st.button("Analyze Code", key="code_btn") and code_query and selected != "Select a file...":
            full_path = next((f for f in merged_data if os.path.basename(f)==selected), None)
            if full_path:
                file_data = merged_data[full_path]
                ci = file_data.get("coverage",{}).get("complexity",{})
                li = file_data.get("linting",{}).get("quality",{})
                st.session_state["code_response"] = ai.chat_code(full_path, ci, li, code_query)
        if "code_response" in st.session_state:
            st.write(st.session_state["code_response"])

    with tab3:
        mods = ["Select a module..."] + [os.path.basename(f) for f in merged_data.keys()]
        sel_mod = st.selectbox("Module:", mods, key="mod_doc")
        folder_opts = ["Select a folder..."] + sorted({os.path.dirname(f) for f in merged_data})
        sel_folder = st.selectbox("Folder:", folder_opts, key="folder_doc")
        if st.button("Summarize Module", key="doc_btn"):
            if sel_mod != "Select a module...":
                path = next((f for f in merged_data if os.path.basename(f)==sel_mod), None)
                funcs = merged_data[path].get("docstrings",{}).get("functions",[]) if path else []
                st.session_state["doc_response"] = ai.chat_doc(path, funcs)
            elif sel_folder != "Select a folder...":
                files = [f for f in merged_data if os.path.dirname(f)==sel_folder]
                funcs = []
                for f in files:
                    funcs += merged_data[f].get("docstrings",{}).get("functions",[])
                st.session_state["doc_response"] = ai.chat_doc(sel_folder, funcs)
        if "doc_response" in st.session_state:
            st.write(st.session_state["doc_response"])

st.markdown("---")

# ---------------------- 🧠 AI-Powered Recommendations ---------------------- #
with st.expander("Get AI-Powered Recommendations", expanded=True):
    if "strategic_recommendations" not in st.session_state:
        st.session_state["strategic_recommendations"] = ""
    if st.button("Generate Strategic Recommendations"):
        # 1. Gather raw data
        severity_data = [
            compute_severity(fp, content)
            for fp, content in merged_data.items()
        ]
        # 2. Build summary metrics
        summary_metrics = {
            "total_tests": summary["total_tests"],
            "avg_strictness": summary["avg_strictness"],
            "avg_severity": summary["avg_severity"],
            "coverage": summary["overall_coverage"],
            "missing_docs": summary["missing_doc_percent"],
            "high_severity_tests": severity_distribution(strictness_data)["High"],
            "medium_severity_tests": severity_distribution(strictness_data)["Medium"],
            "low_severity_tests": severity_distribution(strictness_data)["Low"],
            "limit": file_limit,
        }
        # 3. Build low-coverage context
        low_cov = get_low_coverage_modules(strictness_data, top_n=5)
        low_cov_context = "\n".join(f"{m}: {cov*100:.1f}%" for m, cov in low_cov)
        # 4. Call the AIIntegration helper
        st.session_state["strategic_recommendations"] = ai.generate_strategic_recommendations(
            severity_data, summary_metrics, low_cov_context
        )

    if st.session_state["strategic_recommendations"]:
        st.markdown(st.session_state["strategic_recommendations"])


# ---------------------- 📂 Reports & Downloads ----------------------

c1, c2 = st.columns(2)

