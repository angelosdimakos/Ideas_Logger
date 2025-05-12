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
from rapidfuzz import fuzz
import os

# ─── make "scripts." imports work when executed as a script ────────────────
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.refactor.test_discovery import normalize_test_name

# -------------------- Logging Setup --------------------
logger = logging.getLogger("AssignmentLogic")


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
    imports: Dict[str, List[str]] = Field(default_factory=dict)  # filename -> list of imports


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


def get_test_severity(
        test_entry: StrictnessEntry,
        coverage: Optional[float] = None,
        alpha: float = 0.7
) -> float:
    """
    Compute severity with implicit weighting from coverage.

    Args:
        test_entry: StrictnessEntry object with test data.
        coverage: Optional coverage value (0.0 to 1.0). If None, no weighting applied.
        alpha: Weighting factor for severity vs. coverage.
               Higher alpha means severity dominates.

    Returns:
        float: Adjusted severity score.
    """
    base_severity = test_entry.severity_score if test_entry.severity_score is not None else test_entry.strictness_score

    if coverage is None:
        return base_severity  # Fall back to pure severity if no coverage info.

    # Invert coverage (low coverage => higher severity weight), apply blending
    adjusted_severity = (alpha * base_severity) + ((1 - alpha) * (1 - coverage))

    return round(min(adjusted_severity, 1.0), 2)  # Cap at 1.0


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
        strictness_entries: List[StrictnessEntry],
        test_imports: Dict[str, List[str]]
) -> Dict[str, Any]:
    final_report = FinalReport()

    # Track assigned tests by normalized test name to prevent duplicates
    # (with and without class prefix)
    assigned_tests = set()  # Set of tuples (normalized_test_name, test_file)

    for prod_file, file_audit in audit_model.__root__.items():
        if os.path.basename(prod_file) == "__init__.py":
            continue

        prod_file_name = Path(prod_file).stem.lower()
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
        for test_entry in strictness_entries:
            # Create a normalized test identifier that will be the same regardless of class prefix
            test_method_name = test_entry.name.split('.')[-1] if '.' in test_entry.name else test_entry.name
            normalized_test_name = normalize_test_name(test_method_name, remove_test_prefix=False)

            # Create a unique identifier for each test by combining normalized name and file
            test_unique_id = (normalized_test_name, test_entry.file)

            if test_unique_id in assigned_tests:
                continue  # Skip if already assigned

            if should_assign_test_to_module(
                    prod_file_name,
                    list(method_metrics.keys()),
                    test_entry,
                    test_imports
            ):
                tests_for_module.append(
                    TestOutput(
                        test_name=test_entry.name,
                        strictness=round(test_entry.strictness_score, 2),
                        severity=round(get_test_severity(test_entry, coverage=avg_cov), 2)
                    )
                )
                # Mark the test as assigned using the normalized identifier
                assigned_tests.add(test_unique_id)

        normalized_path = Path(prod_file).as_posix()
        final_report.modules[normalized_path] = ModuleOutput(
            module_coverage=round(avg_cov, 2),
            methods=methods,
            tests=tests_for_module
        )

    return {module: output.dict() for module, output in final_report.modules.items()}

def fuzzy_match(a: str, b: str, threshold: int = 95) -> bool:
    """Fuzzy matching with partial ratio preference for looser matching."""
    partial_score = fuzz.partial_ratio(a, b)
    token_score = fuzz.token_sort_ratio(a, b)

    # Use the higher of the two scores to allow flexibility
    final_score = max(partial_score, token_score)
    return final_score >= threshold


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


def should_assign_test_to_module(
        prod_file_name: str,
        method_names: List[str],
        test_entry: StrictnessEntry,
        test_imports: Dict[str, List[str]],
        fuzzy_threshold: int = 95,
) -> bool:
    """
    Decide if a test should be assigned to a production module using strict matching.
    Prioritizes conventions and imports. Fuzzy matching is a last resort with a high bar.
    """
    test_file_name = Path(test_entry.file).stem.lower()
    normalized_test_name = normalize_test_name(test_entry.name.lower(), remove_test_prefix=True)

    # 1. Strong Convention-Based Check
    if f"test_{prod_file_name}" == test_file_name or f"{prod_file_name}_test" == test_file_name:
        logger.debug(f"✅ Strong convention match: prod='{prod_file_name}', test='{test_file_name}'")
        return True

    # 2. Strict Import Check
    imported_modules = test_imports.get(test_file_name, [])
    if imported_modules and prod_file_name in imported_modules:
        logger.debug(
            f"✅ Strict import match: prod='{prod_file_name}', test='{test_file_name}', imports={imported_modules}")
        return True

    # 💡 2b. Class Name Fuzzy Check
    class_name_raw = test_entry.name.split('.')[0].lower()
    normalized_class_name = normalize_test_name(class_name_raw, remove_test_prefix=True)
    if fuzzy_match(prod_file_name, normalized_class_name, fuzzy_threshold):
        logger.debug(f"✅ Class-based fuzzy match: prod='{prod_file_name}', test_class='{normalized_class_name}'")
        return True

    # 3. Very Strict Fuzzy Matching on Combined Names (last resort)
    prod_composite = "".join(
        [prod_file_name] + [normalize_test_name(m.lower(), remove_test_prefix=True) for m in method_names]).replace("_",
                                                                                                                    "").lower()
    test_composite = "".join([test_file_name, normalized_test_name]).replace("_", "").lower()
    holistic_match_score = max(fuzz.partial_ratio(prod_composite, test_composite),
                               fuzz.token_sort_ratio(prod_composite, test_composite))

    if holistic_match_score >= fuzzy_threshold:
        logger.debug(
            f"⚠️ Very strict fuzzy match (holistic): prod='{prod_composite}', test='{test_composite}', Score: {holistic_match_score}"
        )
        return True

    logger.debug(f"🛑 No strong match found for prod='{prod_file_name}' and test='{test_entry.name}' ({test_file_name})")
    return False


def main(test_report_path: str, audit_path: str, output_path: Optional[str] = None) -> None:
    logging.info("📚 Loading precomputed strictness report...")
    strictness_report = StrictnessReport.parse_obj(json.load(Path(test_report_path).open("r", encoding="utf-8")))
    test_results = strictness_report.tests
    test_imports = strictness_report.imports
    logging.info(f"✅ Loaded {len(test_results)} test evaluations.")

    logging.info("📈 Loading audit coverage report...")
    audit_model = load_audit_report(audit_path)

    logging.info("🔧 Merging reports into module-centric format...")
    module_report = generate_module_report(audit_model, test_results, test_imports)

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