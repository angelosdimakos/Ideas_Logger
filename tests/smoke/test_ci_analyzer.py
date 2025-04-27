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
    # 1) Try loading a canned file under tests/mock_data:
    sample_json = Path(__file__).parent.parent / "mock_data" / "refactor_audit.json"
    if sample_json.exists():
        return json.loads(sample_json.read_text(encoding="utf-8-sig"))
    # 2) Fallback: minimal audit
    return {
        "example.py": {
            "flake8": {"issues": []},
            "black": {"needs_formatting": False},
            "mypy": {"errors": []},
            "pydocstyle": {"issues": []},
            "coverage": {"percent": 0.0},
            "testing": {},
            "diff": {"changed": 0, "covered": 0},
            "complexity": {},
            "quality": {},
        }
    }


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
