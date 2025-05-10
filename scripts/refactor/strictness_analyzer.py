#!/usr/bin/env python3
"""
Test Coverage Mapper (Strictness Report Version)
Author: Angelos Dimakos
Version: 3.1.0

Loads precomputed strictness analysis and merges it with audit coverage data
to produce a module-centric report.

Usage:
    python test_coverage_mapper.py --test-report test_report.json --audit refactor_audit.json --output final_report.json
"""

import argparse
import json
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

# -------------------- Logging Setup --------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


# -------------------- Pydantic Models --------------------

class ComplexityMetrics(BaseModel):
    complexity: int
    coverage: float
    hits: int
    lines: int
    covered_lines: List[int]
    missing_lines: List[int]


class FileAudit(BaseModel):
    complexity: Dict[str, ComplexityMetrics] = Field(default_factory=dict)


class AuditReport(BaseModel):
    __root__: Dict[str, FileAudit]


class StrictnessEntry(BaseModel):
    name: str
    file: str
    strictness_score: float
    hit_ratio: Optional[float] = 0.0
    severity_score: Optional[float] = None


class StrictnessReport(BaseModel):
    tests: List[StrictnessEntry]


# -------------------- Loaders --------------------

def load_audit_report(audit_path: str) -> AuditReport:
    """Load the audit report JSON into the Pydantic model."""
    path = Path(audit_path)
    if not path.exists():
        logging.error(f"Audit report not found at {audit_path}")
        sys.exit(1)

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return AuditReport.parse_obj(data)


def load_test_report(test_report_path: str) -> List[StrictnessEntry]:
    """Load the precomputed strictness analysis JSON."""
    path = Path(test_report_path)
    if not path.exists():
        logging.error(f"Test report not found at {test_report_path}")
        sys.exit(1)

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return StrictnessReport.parse_obj(data).tests


# -------------------- Report Generator --------------------

def generate_module_report(
    audit_model: AuditReport,
    strictness_entries: List[StrictnessEntry]
) -> Dict[str, Any]:
    """Merge audit and strictness data into a final report."""
    report: Dict[str, Any] = {}

    for prod_file, file_audit in audit_model.__root__.items():
        method_metrics = file_audit.complexity
        avg_cov = round(
            sum(m.coverage for m in method_metrics.values()) / len(method_metrics), 2
        ) if method_metrics else 0.0

        methods = [
            {
                "name": name,
                "coverage": round(m.coverage, 2),
                "complexity": m.complexity
            }
            for name, m in method_metrics.items()
        ]

        prod_file_name = Path(prod_file).stem.lower()
        tests_for_module = []

        for test_entry in strictness_entries:
            test_name = test_entry.name.lower()
            test_file_name = Path(test_entry.file).stem.lower() if hasattr(test_entry, "file") else ""

            # Try to match based on test filename or test name content
            if prod_file_name in test_file_name or prod_file_name in test_name:
                tests_for_module.append({
                    "test_name": test_entry.name,
                    "strictness": round(test_entry.strictness_score, 2),
                    "hit_ratio": round(test_entry.hit_ratio or 0.0, 2),
                    "severity": round(
                        test_entry.severity_score or test_entry.strictness_score, 2
                    )
                })
            else:
                for method_name in method_metrics.keys():
                    if method_name.lower() in test_name:
                        tests_for_module.append({
                            "test_name": test_entry.name,
                            "strictness": round(test_entry.strictness_score, 2),
                            "hit_ratio": round(test_entry.hit_ratio or 0.0, 2),
                            "severity": round(
                                test_entry.severity_score or test_entry.strictness_score, 2
                            )
                        })
                        break

        report[prod_file] = {
            "module_coverage": avg_cov,
            "methods": methods,
            "tests": tests_for_module
        }

    return report



# -------------------- Main Execution --------------------

def main(test_report_path: str, audit_path: str, output_path: Optional[str] = None) -> None:
    """Main execution pipeline for merging test and audit reports."""
    logging.info("📚 Loading precomputed strictness report...")
    test_results = load_test_report(test_report_path)
    logging.info(f"✅ Loaded {len(test_results)} test evaluations.")

    logging.info("📈 Loading audit coverage report...")
    audit_model = load_audit_report(audit_path)

    logging.info("🔧 Merging reports into module-centric format...")
    module_report = generate_module_report(audit_model, test_results)
    report = {"modules": module_report}

    if output_path:
        out_path = Path(output_path)
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        logging.info(f"✅ Final report written to: {out_path}")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate module-centric report from strictness and audit data."
    )
    parser.add_argument("--test-report", required=True, help="Path to test strictness JSON report.")
    parser.add_argument("--audit", required=True, help="Path to refactor audit JSON file.")
    parser.add_argument("--output", help="Path to save final merged JSON report.")
    args = parser.parse_args()

    main(args.test_report, args.audit, args.output)
