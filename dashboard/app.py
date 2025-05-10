import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Tuple

# AI Integration Imports
from scripts.ai.ai_summarizer import AISummarizer
from scripts.ai.llm_router import get_prompt_template, apply_persona
from scripts.ai.llm_refactor_advisor import extract_top_offenders, build_refactor_prompt
from scripts.ai.chat_refactor import build_contextual_prompt
from scripts.ai.module_docstring_summarizer import summarize_module
from scripts.config.config_manager import ConfigManager
from scripts.ai.llm_optimization import build_strategic_recommendations_prompt
from scripts.refactor.compressor.merged_report_squeezer import (
    decompress_obj as decompress_merged,
)
from scripts.refactor.compressor.strictness_loader import (
    load as load_strictness_comp,
)

file_limit = 30
import fnmatch

# -----------------------------------------------------------------
# Files / folders we want to ignore, mirroring .coveragerc [run] omit
EXCLUDE_PATTERNS: list[str] = [
    "tests/*",
    "dashboard/*",
    "gui/*",
    "*/__init__.py",
]

def is_excluded(path: str) -> bool:
    filename = os.path.basename(path)
    return filename == "__init__.py" or any(fnmatch.fnmatch(path, pat) for pat in EXCLUDE_PATTERNS)

# -----------------------------------------------------------------


# ---------------------- Utility Functions ---------------------- #
def load_artifact(path: str) -> dict:
    """
    Load either the original JSON file or its compressed twin.
    Returns an **identical** Python structure in both cases.
    """
    # 1) compressed first (fast path)
    comp = f"{path}.comp.json"
    gz   = f"{comp}.gz"

    if os.path.exists(gz):
        # e.g. artifacts/merged_report.comp.json.gz
        with open(gz, "rb") as fh:
            import gzip, json
            blob = json.loads(gzip.decompress(fh.read()).decode())
    elif os.path.exists(comp):
        with open(comp, "r", encoding="utf-8") as fh:
            import json
            blob = json.load(fh)
    elif os.path.exists(path):
        # fall back to the big uncompressed original
        with open(path, "r", encoding="utf-8") as fh:
            import json
            return json.load(fh)
    else:
        return {}      # nothing found

    # pick the right decompressor
    if path.endswith("merged_report.json"):
        return decompress_merged(blob)
    if path.endswith("strictness_mapping.json"):
        return load_strictness_comp(blob)   # already returns decompressed
    return blob        # defensive fallback



def compute_severity(file_path: str, content: dict) -> dict:
    """
    Compute severity metrics for a file based on its linting errors, mypy errors,
    code complexity, and test coverage.

    Args:
        file_path: Path to the file being analyzed
        content: Dictionary containing analysis data for the file

    Returns:
        Dictionary with severity metrics
    """
    coverage_data = content.get("coverage", {}).get("complexity", {})
    linting = content.get("linting", {}).get("quality", {})
    mypy_errors = linting.get("mypy", {}).get("errors", [])
    pydocstyle_issues = linting.get("pydocstyle", {}).get("functions", {})

    num_lint_issues = sum(len(v) for v in pydocstyle_issues.values())
    num_mypy_errors = len(mypy_errors)

    complexities = [fn.get("complexity", 0) for fn in coverage_data.values()]
    coverages = [fn.get("coverage", 1.0) for fn in coverage_data.values()]

    avg_complexity = np.mean(complexities) if complexities else 0
    avg_coverage = weighted_coverage(coverage_data) if coverage_data else 1.0

    severity_score = (
            2.0 * num_mypy_errors +
            1.5 * num_lint_issues +
            1.0 * avg_complexity +
            2.0 * (1.0 - avg_coverage)
    )

    return {
        "File": os.path.basename(file_path),
        "Full Path": file_path,
        "Mypy Errors": num_mypy_errors,
        "Lint Issues": num_lint_issues,
        "Avg Complexity": round(avg_complexity, 2),
        "Avg Coverage %": round(avg_coverage * 100, 1),
        "Severity Score": round(severity_score, 2),
    }
def weighted_coverage(func_dict: dict) -> float:
    """
    Return overall coverage weighted by each function’s lines-of-code.
    Expects every func entry to have keys:
        - "coverage"  in [0, 1]
        - "loc"       number of source lines (fallback = 1)
    """
    covered_loc = 0
    total_loc   = 0
    for f in func_dict.values():
        loc = f.get("loc", 1)
        covered_loc += f.get("coverage", 0) * loc
        total_loc   += loc
    return covered_loc / total_loc if total_loc else 0.0

# ---------------------- Load Artifacts ---------------------- #
artifacts_dir = "artifacts"
merged_data = load_artifact(os.path.join(artifacts_dir, "merged_report.json"))
strictness_data = load_artifact(os.path.join(artifacts_dir, "strictness_mapping.json"))

# ---------------------- Streamlit Config ---------------------- #
st.set_page_config(page_title="CI Audit Dashboard", layout="wide")
st.title("📊 CI Audit Dashboard")

# Initialize AI components once
config = ConfigManager.load_config()
summarizer = AISummarizer()

# ---------------------- Executive Summary ---------------------- #
st.subheader("Executive Summary")
summary = strictness_data.get("summary", {})
total_tests = summary.get("total_tests", 0)
avg_strictness = round(summary.get("avg_strictness", 0), 2)
avg_severity = round(summary.get("avg_severity", 0), 2)
prod_files = summary.get("total_prod_files_covered", 0)

coverage_sum, coverage_count = 0, 0
for report in merged_data.values():
    complexity = report.get("coverage", {}).get("complexity", {})
    all_funcs: dict = {}
    for file_path, report in merged_data.items():
        if is_excluded(file_path):
            continue  # 🚫 skip tests / GUI
        all_funcs.update(report.get("coverage", {}).get("complexity", {}))

overall_cov_ratio = weighted_coverage(all_funcs) if all_funcs else 0
overall_coverage = round(overall_cov_ratio * 100, 2)

doc_total, doc_missing = 0, 0
for report in merged_data.values():
    doc_info = report.get("docstrings", {})
    module_doc = doc_info.get("module_doc", {})
    if module_doc.get("description") is None:
        doc_missing += 1
    classes = doc_info.get("classes", [])
    functions = doc_info.get("functions", [])
    doc_total += 1 + len(classes) + len(functions)
    doc_missing += sum(1 for cls in classes if not cls.get("description"))
    doc_missing += sum(1 for func in functions if not func.get("description"))
missing_doc_percent = round((doc_missing / doc_total) * 100, 2) if doc_total else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Tests", total_tests)
col2.metric("Avg Strictness", avg_strictness)
col3.metric("Avg Severity", avg_severity)

col4, col5, col6 = st.columns(3)
col4.metric("Prod Files", prod_files)
col5.metric("Coverage", f"{overall_coverage}%")
col6.metric("Missing Docstrings", f"{missing_doc_percent}%")

st.markdown("---")

# ---------------------- 📚 AI-Powered Report Summarization ---------------------- #
with st.expander("📚 AI Report Summary", expanded=True):
    if st.button("Generate AI Summary"):
        with st.spinner("Generating AI summary..."):
            prompt = get_prompt_template("Audit Summary", config)
            final_prompt = apply_persona(prompt, config.persona)

            # Add key metrics to the prompt for better context
            metrics_context = f"""
            Key metrics:
            - Total Tests: {total_tests}
            - Average Strictness: {avg_strictness}
            - Average Severity: {avg_severity}
            - Production Files: {prod_files}
            - Overall Coverage: {overall_coverage}%
            - Missing Docstrings: {missing_doc_percent}%
            """

            enriched_prompt = final_prompt + "\n\n" + metrics_context
            summary_text = summarizer.summarize_entry(enriched_prompt, subcategory="Audit Summary")
            st.success("AI summary generated successfully!")
            st.write(summary_text)

# ---------------------- 📈 Coverage by Module ---------------------- #
with st.expander("📈 Coverage by Module", expanded=True):
    coverage_data = {}
    for file_path, report in merged_data.items():
        if is_excluded(file_path):
            continue
        coverage_info = report.get("coverage", {}).get("complexity", {})
        if coverage_info:
            w_cov_ratio = weighted_coverage(coverage_info)
            if w_cov_ratio > 0:
                coverage_data[os.path.basename(file_path)] = round(w_cov_ratio * 100, 2)


    if coverage_data:
        sorted_coverage = dict(sorted(coverage_data.items(), key=lambda item: item[1]))
        display_data = dict(list(sorted_coverage.items())[:10])

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(list(display_data.keys()), display_data.values(), color="skyblue")
        ax.set_xlabel("Coverage (%)")
        ax.set_xlim(0, 100)
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        ax.bar_label(bars, fmt="%.1f%%", padding=5)
        ax.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("No files with non-zero coverage available.")

st.markdown("---")

# ---------------------- 🤖 Refactor Advisor (LLM Suggestions) ---------------------- #
with st.expander("🤖 Refactor Advisor (LLM Suggestions)", expanded=True):
    # Add file limit control for refactor analysis
    refactor_limit = st.slider("Number of files to analyze:", min_value=5, max_value=50, value=30, step=5,
                               key="refactor_file_limit")

    if st.button("Generate Refactor Suggestions"):
        with st.spinner("Analyzing code and generating suggestions..."):
            # Extract top offenders with the specified limit
            offenders = extract_top_offenders(merged_data, top_n=refactor_limit)

            # Categorize files by issue type for better visualization
            high_complexity_files = [os.path.basename(fp) for fp, _, _, _, cx, _ in offenders if cx > 8]
            low_coverage_files = [os.path.basename(fp) for fp, _, _, _, _, cov in offenders if cov < 50]
            many_errors_files = [os.path.basename(fp) for fp, _, errors, _, _, _ in offenders if len(errors) > 5]

            # Display issue categories metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("High Complexity Files", len(high_complexity_files))
            col2.metric("Low Coverage Files", len(low_coverage_files))
            col3.metric("Files with Many Errors", len(many_errors_files))

            # Process detailed information about the offenders
            offender_details = []
            for fp, score, errors, lint_issues, cx, cov in offenders:
                docstring_info = merged_data[fp].get("docstrings", {})
                missing_docs = sum(1 for func in docstring_info.get("functions", []) if not func.get("description"))
                total_funcs = len(docstring_info.get("functions", []))

                detail = {
                    "file": fp,
                    "score": score,
                    "mypy_errors": len(errors),
                    "lint_issues": lint_issues,
                    "complexity": cx,
                    "coverage": cov,
                    "missing_docs": missing_docs,
                    "total_funcs": total_funcs
                }
                offender_details.append(detail)

            # Generate optimized prompt with the specified verbosity and limit
            prompt = build_refactor_prompt(offenders, config, verbose=False, limit=refactor_limit)
            suggestions = summarizer.summarize_entry(prompt, subcategory="Refactor Advisor")

            # Display suggestions with improved formatting
            st.success("Refactor suggestions generated!")
            st.markdown(f"### AI-Generated Refactoring Suggestions\n{suggestions}")

            # Create dataframe for offender details
            offender_df = pd.DataFrame([{
                "File": os.path.basename(d["file"]),
                "Severity Score": round(d["score"], 2),
                "Missing Docs": f"{d['missing_docs']}/{d['total_funcs']}",
                "MyPy Errors": d["mypy_errors"],
                "Lint Issues": d["lint_issues"],
                "Complexity": round(d["complexity"], 2)
            } for d in offender_details])

            # Display the dataframe with improved styling
            st.subheader("Top Offending Files")

            # Apply color styling based on severity score
            styled_df = offender_df.style.background_gradient(
                subset=["Severity Score"], cmap="Reds"
            )

            st.dataframe(styled_df)

st.markdown("---")

# ---------------------- 🔥 Top Risk Files (By Severity) ---------------------- #
with st.expander("🔥 Top Risk Files (By Severity)", expanded=True):
    severity_data = [compute_severity(fp, content) for fp, content in merged_data.items()]
    severity_df = pd.DataFrame(severity_data).sort_values(by="Severity Score", ascending=False).reset_index(drop=True)

    if not severity_df.empty:
        # Add a way to see file details
        selected_file = st.selectbox(
            "Select a file to view details:",
            severity_df["Full Path"].tolist()[:10],
            format_func=lambda x: os.path.basename(x)
        )

        # Display file details
        if selected_file:
            st.subheader(f"Details for {os.path.basename(selected_file)}")
            file_data = merged_data.get(selected_file, {})

            # Show module docstring if available
            module_doc = file_data.get("docstrings", {}).get("module_doc", {})
            module_desc = module_doc.get("description", "No module docstring available.")
            st.markdown(f"**Module Description**: {module_desc}")

            # Show function list with complexity and coverage
            st.markdown("### Functions:")
            functions = []
            for func_name, func_data in file_data.get("coverage", {}).get("complexity", {}).items():
                functions.append({
                    "Function": func_name,
                    "Complexity": func_data.get("complexity", 0),
                    "Coverage": f"{func_data.get('coverage', 0) * 100:.1f}%"
                })

            if functions:
                st.dataframe(pd.DataFrame(functions))
            else:
                st.info("No function data available for this file.")

            # Show a summary of linting issues
            mypy_errors = file_data.get("linting", {}).get("quality", {}).get("mypy", {}).get("errors", [])
            if mypy_errors:
                st.markdown(f"### MyPy Errors ({len(mypy_errors)})")
                for error in mypy_errors[:5]:  # Show only first 5 errors
                    st.code(error)
                if len(mypy_errors) > 5:
                    st.info(f"{len(mypy_errors) - 5} more errors not shown")

        # Show the overall severity table
        st.subheader("All High Risk Files")
        styled_df = severity_df[
            ["File", "Severity Score", "Avg Complexity", "Avg Coverage %", "Mypy Errors", "Lint Issues"]].head(
            10).style.background_gradient(
            subset=["Severity Score"], cmap="Reds"
        )
        st.dataframe(styled_df)
    else:
        st.info("No risk files identified.")

st.markdown("---")

# ---------------------- 🧩 Strictness Analyzer (Production Coverage View) ---------------------- #
with st.expander("🧩 Strictness Analyzer (Production Coverage View)", expanded=True):
    mapping = strictness_data.get("test_to_prod_mapping", [])
    prod_to_tests = {}

    for entry in mapping:
        prod_files = entry.get("covers_prod_files", [])
        test_name = entry.get("name", "Unnamed Test")
        test_strictness = entry.get("strictness", 0)
        test_severity = entry.get("severity_score", 0)

        for prod_file in prod_files:
            cleaned_file = os.path.basename(prod_file)
            if cleaned_file not in prod_to_tests:
                prod_to_tests[cleaned_file] = []
            prod_to_tests[cleaned_file].append({
                "test_name": test_name,
                "strictness": test_strictness,
                "severity": test_severity
            })

    if prod_to_tests:
        # Create a more informative dataframe
        rows = []
        for prod_file, tests in prod_to_tests.items():
            test_names = ", ".join([t["test_name"] for t in tests])
            avg_strictness = sum(t["strictness"] for t in tests) / len(tests) if tests else 0
            avg_severity = sum(t["severity"] for t in tests) / len(tests) if tests else 0
            rows.append({
                "Production Module": prod_file,
                "Test Count": len(tests),
                "Avg Strictness": round(avg_strictness, 2),
                "Avg Severity": round(avg_severity, 2),
                "Covering Tests": test_names
            })

        prod_coverage_df = pd.DataFrame(rows).sort_values(by="Test Count", ascending=False)
        st.dataframe(prod_coverage_df)

        # Visual representation of test coverage
        fig, ax = plt.subplots(figsize=(10, 6))
        top_modules = prod_coverage_df.sort_values("Test Count", ascending=False).head(10)
        bars = ax.barh(top_modules["Production Module"], top_modules["Test Count"], color="lightgreen")
        ax.bar_label(bars)
        ax.set_xlabel("Number of Tests")
        ax.set_title("Test Coverage by Production Module")
        st.pyplot(fig)
    else:
        st.info("No production files are covered by tests.")

st.markdown("---")

# ---------------------- 📊 Severity Distribution ---------------------- #
with st.expander("📊 Severity Distribution", expanded=True):
    severity_buckets = {"Low": 0, "Medium": 0, "High": 0}
    for item in mapping:
        severity = item.get("severity_score", 0)
        if severity >= 0.7:
            severity_buckets["High"] += 1
        elif severity >= 0.3:
            severity_buckets["Medium"] += 1
        else:
            severity_buckets["Low"] += 1

    # Create a more informative chart
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Bar chart
    ax1.bar(severity_buckets.keys(), severity_buckets.values(), color=["green", "orange", "red"])
    ax1.set_ylabel("Number of Tests")
    ax1.set_title("Test Severity Distribution")
    for i, v in enumerate(severity_buckets.values()):
        ax1.text(i, v + 0.5, str(v), ha='center')

    # Pie chart
    ax2.pie(severity_buckets.values(), labels=severity_buckets.keys(),
            autopct='%1.1f%%', colors=["green", "orange", "red"])
    ax2.set_title("Severity Distribution (%)")

    plt.tight_layout()
    st.pyplot(fig2)

    # Add numeric summary
    st.markdown(f"""
    **Summary:**
    - **{severity_buckets['Low']}** tests have low severity (score < 0.3)
    - **{severity_buckets['Medium']}** tests have medium severity (score 0.3-0.7)
    - **{severity_buckets['High']}** tests have high severity (score > 0.7)
    """)

st.markdown("---")

# ---------------------- 💬 Chat-Style Risk Advisor ---------------------- #
with st.expander("💬 Ask the AI Assistant", expanded=True):
    # Tabs for different question types
    tab1, tab2, tab3 = st.tabs(["General Questions", "Code Analysis", "Documentation"])

    with tab1:
        st.markdown("Ask questions about overall code quality, test coverage, or any metrics.")
        user_query = st.text_input("Ask a question about code risk or quality:", key="general_query")
        if st.button("Get AI Response", key="general_btn"):
            if user_query.strip():
                with st.spinner("Analyzing your question..."):
                    prompt = build_contextual_prompt(user_query, merged_data, config)
                    response = summarizer.summarize_entry(prompt, subcategory="Risk Advisor Chat")
                    st.markdown(response)
            else:
                st.warning("Please enter a question before submitting.")

    with tab2:
        st.markdown("Ask specific questions about code structure, complexity, or refactoring needs.")
        file_options = ["Select a file..."] + [os.path.basename(f) for f in merged_data.keys()]
        selected_file = st.selectbox("Focus on a specific file:", file_options)

        code_query = st.text_input("Ask about code issues or improvements:", key="code_query")
        if st.button("Analyze Code", key="code_btn"):
            if code_query.strip() and selected_file != "Select a file...":
                with st.spinner("Performing code analysis..."):
                    # Find the full path
                    full_path = next((f for f in merged_data.keys() if os.path.basename(f) == selected_file), None)
                    if full_path:
                        # Build specialized prompt with file-specific context
                        file_data = merged_data[full_path]
                        complexity_info = file_data.get("coverage", {}).get("complexity", {})
                        lint_info = file_data.get("linting", {}).get("quality", {})

                        specialized_prompt = f"""
                        Analyze the file '{selected_file}' with the following issues:
                        - MyPy Errors: {len(lint_info.get('mypy', {}).get('errors', []))}
                        - Pydocstyle Issues: {sum(len(v) for v in lint_info.get('pydocstyle', {}).get('functions', {}).values())}
                        - Function Count: {len(complexity_info)}

                        User Question: {code_query}
                        """

                        response = summarizer.summarize_entry(specialized_prompt, subcategory="Code Analysis")
                        st.markdown(response)
            else:
                st.warning("Please select a file and enter a question.")

    with tab3:
        st.markdown("Get help with improving documentation or understanding module functionality.")
        module_options = ["Select a module..."] + [os.path.basename(f) for f in merged_data.keys()]
        selected_module = st.selectbox("Select a module:", module_options)

        if st.button("Summarize Module Functionality", key="doc_btn"):
            if selected_module != "Select a module...":
                with st.spinner("Generating module summary..."):
                    # Find the full path
                    full_path = next((f for f in merged_data.keys() if os.path.basename(f) == selected_module), None)
                    if full_path:
                        doc_info = merged_data[full_path].get("docstrings", {})
                        funcs = doc_info.get("functions", [])
                        module_summary = summarize_module(full_path, funcs, summarizer, config)

                        st.subheader(f"Module Summary: {selected_module}")
                        st.markdown(module_summary)

                        # Show docstring stats
                        total_funcs = len(funcs)
                        missing_docs = sum(1 for func in funcs if not func.get("description"))
                        doc_percentage = round(((total_funcs - missing_docs) / total_funcs) * 100,
                                               1) if total_funcs else 0

                        st.metric("Documentation Coverage", f"{doc_percentage}%",
                                  delta=None if doc_percentage >= 80 else f"{missing_docs} missing")
            else:
                st.warning("Please select a module.")

st.markdown("---")

# ---------------------- 📂 Reports & Downloads ---------------------- #
st.subheader("📂 Reports")
col_a, col_b, col_c = st.columns(3)
col_a.download_button(
    "Download Merged Report",
    data=json.dumps(merged_data, indent=2),
    file_name="merged_report.json",
    mime="application/json"
)
col_b.download_button(
    "Download Strictness Mapping",
    data=json.dumps(strictness_data, indent=2),
    file_name="strictness_mapping.json",
    mime="application/json"
)
if col_c.button("🔄 Refresh Data"):
    st.rerun()

# ---------------------- 📈 AI-Powered Recommendations ---------------------- #
st.subheader("📈 Strategic Recommendations")
with st.expander("Get AI-Powered Recommendations", expanded=True):
    if st.button("Generate Strategic Recommendations"):
        with st.spinner("Analyzing your codebase and generating recommendations..."):
            # Prepare comprehensive data for the AI
            summary_metrics = {
                "total_tests": total_tests,
                "avg_strictness": avg_strictness,
                "avg_severity": avg_severity,
                "coverage": overall_coverage,
                "missing_docs": missing_doc_percent,
                "high_severity_tests": severity_buckets["High"],
                "medium_severity_tests": severity_buckets["Medium"],
                "low_severity_tests": severity_buckets["Low"],
                "top_offenders": [f"{os.path.basename(s['Full Path'])} (Score: {s['Severity Score']})"
                                  for s in severity_data[:5]]
            }

            strategic_prompt = build_strategic_recommendations_prompt(severity_data, summary_metrics, limit=file_limit)
            recommendations = summarizer.summarize_entry(strategic_prompt, subcategory="Strategic Recommendations")
            st.markdown(recommendations)

st.markdown("---")