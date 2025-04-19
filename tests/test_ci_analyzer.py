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
    audit_path = Path("refactor_audit.json")
    assert audit_path.exists(), "Missing refactor_audit.json file for tests"
    with audit_path.open(encoding="utf-8-sig") as f:
        return json.load(f)

def test_overview_insights_generate(sample_audit):
    lines = generate_overview_insights(sample_audit)
    assert any("Total Files Audited" in line for line in lines)

def test_prime_suspects_generate(sample_audit):
    lines = generate_prime_insights(sample_audit)
    assert "### 🎯 Prime Suspects" in lines[0]
    assert any("Top Flake8 Errors" in line for line in lines)

def test_complexity_insights_generate(sample_audit):
    lines = generate_complexity_insights(sample_audit)
    assert "### 🧠 Code Complexity Summary" in lines[0]
    assert any("complexity" in line.lower() for line in lines)

def test_testing_insights_generate(sample_audit):
    lines = generate_testing_insights(sample_audit)
    assert any("Testing" in line for line in lines)

def test_quality_insights_generate(sample_audit):
    lines = generate_quality_insights(sample_audit)
    assert any("Quality Score" in line for line in lines)

def test_diff_insights_generate(sample_audit):
    lines = generate_diff_insights(sample_audit)
    assert any("Diff" in line for line in lines)
