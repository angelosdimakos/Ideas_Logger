# analysis.py

from typing import Optional, Dict, Any
from scripts.ai import llm_refactor_advisor as advisor
from scripts.ai import llm_optimization as optim
from scripts.ci_analyzer.metrics_summary import generate_metrics_summary

def analyze_report(report_data: Dict[str, Any], top_n: int = 20, path_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze the report data to extract top offenders, severity data, and metrics.

    Args:
        report_data (Dict): The parsed analysis report.
        top_n (int): Number of top files to consider.
        path_filter (Optional[str]): Optional path substring to filter files.

    Returns:
        Dict[str, Any]: Dict containing top offenders, severity info, and summary metrics.
    """
    top_offenders = advisor.extract_top_offenders(report_data, top_n=top_n)

    severity_data = [
        optim.compute_severity(fp, report_data[fp])
        for fp, *_ in top_offenders
        if not path_filter or path_filter in fp
    ]

    metrics = generate_metrics_summary(report_data)
    if isinstance(metrics, str):
        metrics = {
            "total_tests": "N/A",
            "avg_strictness": "N/A",
            "avg_severity": "N/A",
            "coverage": "N/A",
            "missing_docs": "N/A",
            "high_severity_tests": "N/A",
            "medium_severity_tests": "N/A",
            "low_severity_tests": "N/A"
        }

    return {
        "top_offenders": top_offenders,
        "severity_data": severity_data,
        "summary_metrics": metrics
    }
