#!/usr/bin/env python3
"""
Test Coverage Mapper (Strictness Report Version)
Author: Angelos Dimakos
Version: 3.2.0

Loads precomputed strictness analysis and merges it with audit coverage data
into a module-centric report with consistent schema handling.

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
    """Model for storing code complexity and test coverage metrics for a single method."""
    complexity: int
    coverage: float
    hits: int
    lines: int
    covered_lines: List[int]
    missing_lines: List[int]
    loc: int = 1  # Default to 1 for weighted coverage calculation


class FileAudit(BaseModel):
    """Model for storing audit data for a specific file."""
    complexity: Dict[str, ComplexityMetrics] = Field(default_factory=dict)


class AuditReport(BaseModel):
    """Top-level model for the audit report."""
    __root__: Dict[str, FileAudit]


class StrictnessEntry(BaseModel):
    """Model for storing test strictness evaluation data."""
    name: str
    file: str
    strictness_score: float
    severity_score: Optional[float] = None


class StrictnessReport(BaseModel):
    """Top-level model for the strictness report."""
    tests: List[StrictnessEntry]


class MethodOutput(BaseModel):
    """Standardized output model for method data in the final report."""
    name: str
    coverage: float
    complexity: int


class TestOutput(BaseModel):
    """Standardized output model for test data in the final report."""
    test_name: str
    strictness: float
    severity: float


class ModuleOutput(BaseModel):
    """Standardized output model for module data in the final report."""
    module_coverage: float
    methods: List[MethodOutput] = Field(default_factory=list)
    tests: List[TestOutput] = Field(default_factory=list)


class FinalReport(BaseModel):
    """Top-level model for the final merged report."""
    modules: Dict[str, ModuleOutput] = Field(default_factory=dict)


# -------------------- Helper Functions --------------------

def weighted_coverage(func_dict: Dict[str, ComplexityMetrics]) -> float:
    """
    Return overall coverage weighted by each function's lines-of-code.

    Args:
        func_dict: Dictionary of function names to ComplexityMetrics

    Returns:
        float: Weighted coverage value between 0.0 and 1.0
    """
    covered_loc = 0
    total_loc = 0
    for f in func_dict.values():
        loc = getattr(f, "loc", 1)
        covered_loc += f.coverage * loc
        total_loc += loc
    return covered_loc / total_loc if total_loc else 0.0


def get_test_severity(test_entry: StrictnessEntry) -> float:
    """
    Get test severity, falling back to strictness if not available.

    Args:
        test_entry: StrictnessEntry object with test data

    Returns:
        float: Test severity score
    """
    return test_entry.severity_score if test_entry.severity_score is not None else test_entry.strictness_score


# -------------------- Loaders --------------------

def load_audit_report(audit_path: str) -> AuditReport:
    """
    Load the audit report JSON into the Pydantic model.

    Args:
        audit_path: Path to the audit report JSON file

    Returns:
        AuditReport: Pydantic model with audit data

    Raises:
        SystemExit: If file not found or invalid JSON
    """
    path = Path(audit_path)
    if not path.exists():
        logging.error(f"Audit report not found at {audit_path}")
        sys.exit(1)

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return AuditReport.parse_obj(data)
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in audit report: {audit_path}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error loading audit report: {e}")
        sys.exit(1)


def load_test_report(test_report_path: str) -> List[StrictnessEntry]:
    """
    Load the precomputed strictness analysis JSON.

    Args:
        test_report_path: Path to the test strictness report JSON file

    Returns:
        List[StrictnessEntry]: List of test strictness entries

    Raises:
        SystemExit: If file not found or invalid JSON
    """
    path = Path(test_report_path)
    if not path.exists():
        logging.error(f"Test report not found at {test_report_path}")
        sys.exit(1)

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return StrictnessReport.parse_obj(data).tests
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in test report: {test_report_path}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error loading test report: {e}")
        sys.exit(1)

# -------------------- Report Generator --------------------

def generate_module_report(
        audit_model: AuditReport,
        strictness_entries: List[StrictnessEntry]
) -> Dict[str, Any]:
    """
    Merge audit and strictness data into a standardized final report.

    Args:
        audit_model: AuditReport object with complexity and coverage data
        strictness_entries: List of StrictnessEntry objects with test data

    Returns:
        Dict[str, Any]: Mapping of module filenames to their report data
    """
    final_report = FinalReport()

    for prod_file, file_audit in audit_model.__root__.items():
        method_metrics = file_audit.complexity
        avg_cov = weighted_coverage(method_metrics) if method_metrics else 0.0

        methods = [
            MethodOutput(
                name=name,
                coverage=round(m.coverage, 2),
                complexity=m.complexity
            ) for name, m in method_metrics.items()
        ]

        tests_for_module = []
        prod_file_name = Path(prod_file).stem.lower()

        for test_entry in strictness_entries:
            test_name = test_entry.name.lower()
            test_file_name = Path(test_entry.file).stem.lower() if hasattr(test_entry, "file") else ""

            assigned = False
            if prod_file_name in test_file_name or prod_file_name in test_name:
                assigned = True
            else:
                for method_name in method_metrics.keys():
                    if method_name.lower() in test_name:
                        assigned = True
                        break

            if assigned:
                tests_for_module.append(
                    TestOutput(
                        test_name=test_entry.name,
                        strictness=round(test_entry.strictness_score, 2),
                        severity=round(get_test_severity(test_entry), 2)
                    )
                )

        final_report.modules[prod_file] = ModuleOutput(
            module_coverage=round(avg_cov, 2),
            methods=methods,
            tests=tests_for_module  # Will remain empty if no relevant tests were found
        )

    return {
        module: output.dict()
        for module, output in final_report.modules.items()
    }



def validate_report_schema(data: Dict[str, Any], report_type: str = "final") -> bool:
    try:
        if report_type == "final":
            FinalReport.parse_obj(data)
        elif report_type == "audit":
            AuditReport.parse_obj(data)
        elif report_type == "strictness":
            if "tests" not in data:
                logging.warning("Missing 'tests' key in strictness report")
                return False
            StrictnessReport.parse_obj(data)
        else:
            logging.warning(f"Unknown report type: {report_type}")
            return False
        return True
    except Exception as e:
        logging.warning(f"Schema validation failed: {e}")
        return False


def main(test_report_path: str, audit_path: str, output_path: Optional[str] = None) -> None:
    logging.info("📚 Loading precomputed strictness report...")
    test_results = load_test_report(test_report_path)
    logging.info(f"✅ Loaded {len(test_results)} test evaluations.")

    logging.info("📈 Loading audit coverage report...")
    audit_model = load_audit_report(audit_path)

    logging.info("🔧 Merging reports into module-centric format...")
    module_report = generate_module_report(audit_model, test_results)

    if not validate_report_schema(module_report):
        logging.warning("Generated report does not match expected schema!")

    if output_path:
        out_path = Path(output_path)
        out_path.write_text(json.dumps(module_report, indent=2), encoding="utf-8")
        logging.info(f"✅ Final report written to: {out_path}")
    else:
        print(json.dumps(module_report, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate module-centric report from strictness and audit data."
    )
    parser.add_argument("--test-report", required=True, help="Path to test strictness JSON report.")
    parser.add_argument("--audit", required=True, help="Path to refactor audit JSON file.")
    parser.add_argument("--output", help="Path to save final merged JSON report.")
    args = parser.parse_args()

    main(args.test_report, args.audit, args.output)
