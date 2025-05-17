# analysis.py

from typing import Optional, Dict, Any
from scripts.ai import llm_refactor_advisor as advisor
from scripts.ai import llm_optimization as optim
from scripts.ci_analyzer.metrics_summary import generate_metrics_summary

def analyze_report(report_data: Dict[str, Any], top_n: int = 20, path_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze the report data to extract top offenders, severity data, and metrics.
    """
    raw_offenders = advisor.extract_top_offenders(report_data, top_n=top_n)

    # Apply path filter early to stay consistent
    top_offenders = [
        offender for offender in raw_offenders
        if not path_filter or path_filter in offender[0]
    ]

    severity_data = [
        optim.compute_severity(fp, report_data[fp])
        for fp, *_ in top_offenders
    ]

    metrics = generate_metrics_summary(report_data)
    if isinstance(metrics, str):  # fallback in case of error
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
