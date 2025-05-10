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
from scripts.refactor.compressor.strictness_report_squeezer import decompress_obj as load_strictness_comp


file_limit = 30
import fnmatch

# -----------------------------------------------------------------
# Determine artifacts directory (fall back to current directory if not found)
default_artifacts_dir = "artifacts"
if os.path.isdir(default_artifacts_dir):
    artifacts_dir = default_artifacts_dir
else:
    artifacts_dir = "."

# -----------------------------------------------------------------
# Files / folders we want to ignore, mirroring .coveragerc [run] omit
EXCLUDE_PATTERNS: list[str] = [
    "tests/*",
    "dashboard/*",
    "gui/**",
    "*/__init__.py",
]

def is_excluded(path: str) -> bool:
    filename = os.path.basename(path)
    return filename == "__init__.py" or any(fnmatch.fnmatch(path, pat) for pat in EXCLUDE_PATTERNS)

# ---------------------- Utility Functions ---------------------- #
def load_artifact(path: str) -> dict:
    """
    Load either the original JSON file or its compressed twin.
    Strips out any entries matching exclusion patterns directly at load time.
    """
    base, _ = os.path.splitext(path)
    comp = f"{base}.comp.json"
    gz = f"{comp}.gz"

    # Try compressed versions first
    if os.path.exists(gz):
        with open(gz, "rb") as fh:
            import gzip
            blob = json.loads(gzip.decompress(fh.read()).decode())
    elif os.path.exists(comp):
        with open(comp, "r", encoding="utf-8") as fh:
            blob = json.load(fh)
    elif os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    else:
        return {}

    # Decompress if needed
    if path.endswith("merged_report.json"):
        blob = decompress_merged(blob)
    elif path.endswith("final_strictness_report.json"):
        blob = load_strictness_comp(blob)

    # Filter out excluded keys at the top level
    if isinstance(blob, dict):
        filtered = {k: v for k, v in blob.items() if not is_excluded(k)}
        return filtered

    return blob  # Defensive fallback


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
    total_loc = 0
    for f in func_dict.values():
        loc = f.get("loc", 1)
        covered_loc += f.get("coverage", 0) * loc
        total_loc += loc
    return covered_loc / total_loc if total_loc else 0.0

# ---------------------- Load Artifacts ---------------------- #
artifacts_dir = "artifacts"
merged_data = load_artifact(os.path.join(artifacts_dir, "merged_report.json"))

# ✅ Updated to load final strictness report
strictness_data = load_artifact(os.path.join(artifacts_dir, "final_strictness_report.json"))

# ---------------------- Streamlit Config ---------------------- #
st.set_page_config(page_title="CI Audit Dashboard", layout="wide")
st.title("📊 CI Audit Dashboard")

# Initialize AI components once
config = ConfigManager.load_config()
summarizer = AISummarizer()

# ---------------------- Executive Summary ---------------------- #
st.subheader("Executive Summary")
modules = strictness_data.get("modules", {})
unique_tests = set()
strictness_values, severity_values, coverage_values = [], [], []

for file_path, mod_data in modules.items():
    if is_excluded(file_path):
        continue  # 🚫 Skip excluded files (including gui/*)
    coverage = mod_data.get("module_coverage", 0)
    coverage_values.append(coverage)
    for test in mod_data.get("tests", []):
        test_name = test.get("test_name")
        if test_name:
            unique_tests.add(test_name)
        strictness_values.append(test.get("strictness", 0))
        severity_values.append(test.get("severity", 0))

total_tests = len(unique_tests)
avg_strictness = round(np.mean(strictness_values), 2) if strictness_values else 0.0
avg_severity = round(np.mean(severity_values), 2) if severity_values else 0.0


prod_files = len(modules)
overall_coverage = round(np.mean(coverage_values) * 100, 2) if coverage_values else 0.0


# ✅ Accurate Docstring Analysis from merged_report
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

missing_doc_percent = round((doc_missing / doc_total) * 100, 2) if doc_total else 0.0

# ✅ Display Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Unique Tests", total_tests)
col2.metric("Avg Strictness", avg_strictness)
col3.metric("Avg Severity", avg_severity)

col4, col5, col6 = st.columns(3)
col4.metric("Production Modules", prod_files)
col5.metric("Overall Coverage", f"{overall_coverage}%")
col6.metric("Missing Docstrings", f"{missing_doc_percent}%")

st.markdown("---")


# ---------------------- 📚 AI-Powered Report Summarization ---------------------- #
with st.expander("📚 AI Report Summary", expanded=True):
    if "ai_summary" not in st.session_state:
        st.session_state["ai_summary"] = ""  # Initialize if not set

    if st.button("Generate AI Summary"):
        with st.spinner("Generating AI summary..."):
            prompt = get_prompt_template("Audit Summary", config)
            final_prompt = apply_persona(prompt, config.persona)

            # Compute top low-coverage production modules
            low_cov_modules = []
            modules_data = strictness_data.get("modules", {})
            for mod_name, mod_data in modules_data.items():
                cov = mod_data.get("module_coverage", 0)
                low_cov_modules.append((mod_name, cov))

            low_cov_modules.sort(key=lambda x: x[1])

            metrics_context = f"""
            Key metrics:
            - Total Tests: {total_tests}
            - Average Strictness: {avg_strictness}
            - Average Severity: {avg_severity}
            - Production Files: {prod_files}
            - Overall Coverage: {overall_coverage}%
            - Missing Docstrings: {missing_doc_percent}%

            Top Low-Coverage Production Modules:"""
            for mod, cov in low_cov_modules[:5]:
                metrics_context += f"\n- {mod}: {cov * 100:.1f}% coverage"

            enriched_prompt = final_prompt + "\n\n" + metrics_context
            st.session_state["ai_summary"] = summarizer.summarize_entry(enriched_prompt, subcategory="Audit Summary")

    if st.session_state["ai_summary"]:
        st.success("AI summary generated successfully!")
        st.write(st.session_state["ai_summary"])



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
    # Initialize session state for persistence
    if "refactor_suggestions" not in st.session_state:
        st.session_state.refactor_suggestions = None
    if "offender_df" not in st.session_state:
        st.session_state.offender_df = None
    if "refactor_metrics" not in st.session_state:
        st.session_state.refactor_metrics = {
            "high_complexity": 0,
            "low_coverage": 0,
            "many_errors": 0
        }

    # Add file limit control for refactor analysis
    refactor_limit = st.slider(
        "Number of files to analyze:",
        min_value=5,
        max_value=50,
        value=30,
        step=5,
        key="refactor_file_limit"
    )

    if st.button("Generate Refactor Suggestions"):
        with st.spinner("Analyzing code and generating suggestions..."):
            # Extract top offenders with the specified limit
            offenders = extract_top_offenders(merged_data, top_n=refactor_limit)

            # Categorize files by issue type for better visualization
            high_complexity_files = [os.path.basename(fp) for fp, _, _, _, cx, _ in offenders if cx > 8]
            low_coverage_files = [os.path.basename(fp) for fp, _, _, _, _, cov in offenders if cov < 50]
            many_errors_files = [os.path.basename(fp) for fp, _, errors, _, _, _ in offenders if len(errors) > 5]

            # Store metrics in session state
            st.session_state.refactor_metrics = {
                "high_complexity": len(high_complexity_files),
                "low_coverage": len(low_coverage_files),
                "many_errors": len(many_errors_files)
            }

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

            # Store suggestions in session state
            st.session_state.refactor_suggestions = suggestions

            # Create dataframe for offender details and store it
            offender_df = pd.DataFrame([{
                "File": os.path.basename(d["file"]),
                "Severity Score": round(d["score"], 2),
                "Missing Docs": f"{d['missing_docs']}/{d['total_funcs']}",
                "MyPy Errors": d["mypy_errors"],
                "Lint Issues": d["lint_issues"],
                "Complexity": round(d["complexity"], 2)
            } for d in offender_details])

            st.session_state.offender_df = offender_df

    # Display metrics if available
    if st.session_state.refactor_metrics["high_complexity"] > 0 or \
            st.session_state.refactor_metrics["low_coverage"] > 0 or \
            st.session_state.refactor_metrics["many_errors"] > 0:
        col1, col2, col3 = st.columns(3)
        col1.metric("High Complexity Files", st.session_state.refactor_metrics["high_complexity"])
        col2.metric("Low Coverage Files", st.session_state.refactor_metrics["low_coverage"])
        col3.metric("Files with Many Errors", st.session_state.refactor_metrics["many_errors"])

    # Display suggestions if available
    if st.session_state.refactor_suggestions:
        st.success("Refactor suggestions generated!")
        st.markdown(f"### AI-Generated Refactoring Suggestions\n{st.session_state.refactor_suggestions}")

    # Display the dataframe if available
    if st.session_state.offender_df is not None:
        st.subheader("Top Offending Files")

        # Apply color styling based on severity score
        styled_df = st.session_state.offender_df.style.background_gradient(
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
    modules_data = strictness_data.get("modules", {})
    prod_to_tests = {}

    for prod_path, module_info in modules_data.items():
        cleaned_file = os.path.basename(prod_path)
        tests = module_info.get("tests", [])
        for entry in tests:
            test_name = entry.get("test_name", "Unnamed Test")
            test_strictness = entry.get("strictness", 0)
            test_severity = entry.get("severity", 0)
            prod_to_tests.setdefault(cleaned_file, []).append({
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
    modules = strictness_data.get("modules", {})

    for module_data in modules.values():
        for test in module_data.get("tests", []):
            severity = test.get("severity", 0)
            if severity <= 0.3:
                severity_buckets["Low"] += 1
            elif severity <= 0.7:
                severity_buckets["Medium"] += 1
            else:
                severity_buckets["High"] += 1

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

with st.expander("💬 Ask the AI Assistant", expanded=True):
    tab1, tab2, tab3 = st.tabs(["General Questions", "Code Analysis", "Documentation"])

    with tab1:
        st.markdown("Ask questions about overall code quality, test coverage, or any metrics.")
        user_query = st.text_input("Ask a question about code risk or quality:", key="general_query")

        if st.button("Get AI Response", key="general_btn"):
            if user_query.strip():
                with st.spinner("Analyzing your question..."):
                    prompt = build_contextual_prompt(user_query, merged_data, config)
                    st.session_state["general_response"] = summarizer.summarize_entry(prompt, subcategory="Risk Advisor Chat")
            else:
                st.warning("Please enter a question before submitting.")

        if "general_response" in st.session_state:
            st.markdown(st.session_state["general_response"])

    with tab2:
        st.markdown("Ask specific questions about code structure, complexity, or refactoring needs.")
        file_options = ["Select a file..."] + [os.path.basename(f) for f in merged_data.keys()]
        selected_file = st.selectbox("Focus on a specific file:", file_options, key="selected_file")

        code_query = st.text_input("Ask about code issues or improvements:", key="code_query")

        if st.button("Analyze Code", key="code_btn"):
            if code_query.strip() and selected_file != "Select a file...":
                with st.spinner("Performing code analysis..."):
                    full_path = next((f for f in merged_data.keys() if os.path.basename(f) == selected_file), None)
                    if full_path:
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
                        st.session_state["code_response"] = summarizer.summarize_entry(specialized_prompt, subcategory="Code Analysis")
            else:
                st.warning("Please select a file and enter a question.")

        if "code_response" in st.session_state:
            st.markdown(st.session_state["code_response"])

    with tab3:
        st.markdown("Get help with improving documentation or understanding module functionality.")
        module_options = ["Select a module..."] + [os.path.basename(f) for f in merged_data.keys()]
        selected_module = st.selectbox("Select a module:", module_options, key="selected_module")

        folder_options = ["Select a folder..."] + sorted(set(os.path.dirname(f) for f in merged_data.keys()))
        selected_folder = st.selectbox("Or select a folder:", folder_options, key="selected_folder")

        if st.button("Summarize Module Functionality", key="doc_btn"):
            if selected_module != "Select a module...":
                with st.spinner("Generating module summary..."):
                    full_path = next((f for f in merged_data.keys() if os.path.basename(f) == selected_module), None)
                    if full_path:
                        doc_info = merged_data[full_path].get("docstrings", {})
                        funcs = doc_info.get("functions", [])
                        st.session_state["doc_response"] = summarize_module(full_path, funcs, summarizer, config)

            elif selected_folder != "Select a folder...":
                with st.spinner("Generating folder summary..."):
                    folder_files = [f for f in merged_data.keys() if os.path.dirname(f) == selected_folder]
                    combined_funcs = []
                    for f_path in folder_files:
                        funcs = merged_data[f_path].get("docstrings", {}).get("functions", [])
                        combined_funcs.extend(funcs)

                    if combined_funcs:
                        st.session_state["doc_response"] = summarize_module(selected_folder, combined_funcs, summarizer, config)
                    else:
                        st.session_state["doc_response"] = "No documented functions found in this folder."
            else:
                st.warning("Please select either a module or a folder.")

        if "doc_response" in st.session_state:
            st.markdown(st.session_state["doc_response"])

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
    "Download Final Strictness Report",
    data=json.dumps(strictness_data, indent=2),
    file_name="final_strictness_report.json",
    mime="application/json"
)
if col_c.button("🔄 Refresh Data"):
    st.rerun()


# ---------------------- 📈 AI-Powered Recommendations ---------------------- #
with st.expander("Get AI-Powered Recommendations", expanded=True):
    if "strategic_recommendations" not in st.session_state:
        st.session_state["strategic_recommendations"] = ""

    if st.button("Generate Strategic Recommendations"):
        with st.spinner("Analyzing your codebase and generating recommendations..."):
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

            low_cov_modules = []
            modules_data = strictness_data.get("modules", {})
            for mod_name, mod_data in modules_data.items():
                cov = mod_data.get("module_coverage", 0)
                low_cov_modules.append((mod_name, cov))

            low_cov_modules.sort(key=lambda x: x[1])

            low_cov_context = "\nTop Low-Coverage Production Modules:"
            for mod, cov in low_cov_modules[:5]:
                low_cov_context += f"\n- {mod}: {cov * 100:.1f}% coverage"

            strategic_prompt = build_strategic_recommendations_prompt(
                severity_data, summary_metrics, limit=file_limit
            )
            enriched_prompt = strategic_prompt + "\n\n" + low_cov_context

            st.session_state["strategic_recommendations"] = summarizer.summarize_entry(
                enriched_prompt, subcategory="Strategic Recommendations"
            )

    if st.session_state["strategic_recommendations"]:
        st.markdown(st.session_state["strategic_recommendations"])



st.markdown("---")