# tests/test_ci_analyzer.py
import pytest
import json
from pathlib import Path

from scripts.ci_analyzer.insights.overview import generate_overview_insights
from scripts.ci_analyzer.insights.prime_suspects import generate_prime_insights
from scripts.ci_analyzer.insights.descriptive_insights import (
    generate_complexity_insights,
    generate_testing_insights,
    generate_quality_insights,
    generate_diff_insights,
)


@pytest.fixture
def sample_audit() -> dict:
    """
    Smoke tests for CI analyzer insight generators, verifying that each insight function
    produces expected output when given a sample audit report. Ensures correct integration
    of overview, prime suspects, complexity, testing, quality, and diff insights.
    """
    audit_path = Path("refactor_audit.json")
    assert audit_path.exists(), "Missing refactor_audit.json file for tests"
    with audit_path.open(encoding="utf-8-sig") as f:
        return json.load(f)


def test_overview_insights_generate(sample_audit):
    """
    Smoke tests for CI analyzer insight generators.

    Verifies that each insight function (overview, prime suspects, complexity, testing, quality, diff)
    produces expected output when given a sample audit report, ensuring correct integration and output format.
    """
    lines = generate_overview_insights(sample_audit)
    assert any("Total Files Audited" in line for line in lines)


def test_prime_suspects_generate(sample_audit):
    """
    Smoke tests for CI analyzer insight generators.

    Verifies that each insight function (overview, prime suspects, complexity, testing, quality, diff)
    produces the expected output format when given a sample audit report, ensuring correct integration
    and output structure for all insight modules.
    """
    lines = generate_prime_insights(sample_audit)
    assert isinstance(lines, list)
    assert len(lines) >= 1
    assert lines[0].startswith("### 🎯 Prime Suspects")


def test_complexity_insights_generate(sample_audit):
    """
    Smoke tests for CI analyzer insight generators.

    This module verifies that each insight function (overview, prime suspects, complexity, testing, quality, diff)
    produces the expected output and integrates correctly when provided with a sample audit report.
    """
    lines = generate_complexity_insights(sample_audit)
    assert "### 🧠 Code Complexity Summary" in lines[0]
    assert any("complexity" in line.lower() for line in lines)


def test_testing_insights_generate(sample_audit):
    """
    Smoke tests for CI analyzer insight generators.

    This module verifies that each insight function (overview, prime suspects, complexity, testing, quality, diff)
    produces the expected output and integrates correctly when provided with a sample audit report.
    """
    lines = generate_testing_insights(sample_audit)
    assert any("Testing" in line for line in lines)


def test_quality_insights_generate(sample_audit):
    """
    Smoke tests for CI analyzer insight generators.

    Verifies that each insight function (overview, prime suspects, complexity, testing, quality, diff)
    produces the expected output and integrates correctly when provided with a sample audit report.
    """
    lines = generate_quality_insights(sample_audit)
    assert any("Quality Score" in line for line in lines)


def test_diff_insights_generate(sample_audit):
    """
    Smoke tests for CI analyzer insight generators.

    Verifies that each insight function (overview, prime suspects, complexity, testing, quality, diff)
    produces the expected output and integrates correctly when provided with a sample audit report.
    Ensures correct output format and integration for all insight modules using a real audit JSON file.
    """
    lines = generate_diff_insights(sample_audit)
    assert any("Diff" in line for line in lines)
