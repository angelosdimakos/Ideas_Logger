"""
Tests for scripts.refactor.parsers.json_coverage_parser
------------------------------------------------------
Targets the critical branches:

1. Exact-path match with function-level summaries.
2. Suffix-fallback match (mix of POSIX/Windows separators) + executed-lines path.
3. No match at all ⇒ fully uncovered result.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

import pytest

# import the module under test
MODULE = "scripts.refactor.parsers.json_coverage_parser"
jcov = pytest.importorskip(MODULE, reason="target package must be importable")
parse_json_coverage = jcov.parse_json_coverage
FIXTURES_DIR = Path(__file__).parent.parent.parent.parent / "fixtures"
METHOD_RANGES: Dict[str, Tuple[int, int]] = {"foo": (1, 5), "bar": (6, 10)}


# ---------------------------------------------------------------------------
# helpers / fixtures
# ---------------------------------------------------------------------------


def _write_cov_json(tmp_path: Path, files_mapping: dict) -> Path:
    cov = {"files": files_mapping}
    p = tmp_path / "cov.json"
    p.write_text(json.dumps(cov, indent=2), encoding="utf-8")
    return p


@pytest.fixture
def coverage_json_path():
    return str(FIXTURES_DIR / "coverage.json")


@pytest.fixture
def method_ranges():
    return {
        "AISummarizer.__init__": (30, 45),
        "AISummarizer._fallback_summary": (50, 70),
        "AISummarizer.summarize_entry": (75, 100),
    }


def test_exact_path_match(coverage_json_path, method_ranges):
    result = parse_json_coverage(coverage_json_path, method_ranges, "scripts/ai/ai_summarizer.py")
    assert "scripts/ai/ai_summarizer.py" in result
    assert "AISummarizer.__init__" in result["scripts/ai/ai_summarizer.py"]
    assert result["scripts/ai/ai_summarizer.py"]["AISummarizer.__init__"]["coverage"] >= 0.0


def test_suffix_path_match(coverage_json_path, method_ranges):
    # Simulate a non-normalized path that should still match via suffix
    result = parse_json_coverage(coverage_json_path, method_ranges, "ai/ai_summarizer.py")
    assert "ai/ai_summarizer.py" in result or "scripts/ai/ai_summarizer.py" in result


def test_no_coverage_fallback(coverage_json_path):
    fake_ranges = {"NonExistent.method": (10, 20)}
    result = parse_json_coverage(coverage_json_path, fake_ranges, "scripts/nonexistent.py")
    assert "scripts/nonexistent.py" in result
    assert result["scripts/nonexistent.py"]["NonExistent.method"]["coverage"] == 0.0
    assert result["scripts/nonexistent.py"]["NonExistent.method"]["hits"] == 0


def test_summary_usage_over_executed_lines(coverage_json_path, method_ranges):
    result = parse_json_coverage(coverage_json_path, method_ranges, "scripts/ai/ai_summarizer.py")
    coverage_val = result["scripts/ai/ai_summarizer.py"]["AISummarizer.__init__"]["coverage"]
    assert coverage_val == 1.0  # According to summary, this should be 100% covered


def test_executed_lines_fallback_when_summary_missing(tmp_path, method_ranges):
    # Simulate a minimal JSON file with no summaries, only executed_lines
    dummy_json = {
        "files": {
            "scripts/ai/ai_summarizer.py": {
                "executed_lines": [31, 32, 33]
            }
        }
    }
    json_path = tmp_path / "dummy_coverage.json"
    json_path.write_text(json.dumps(dummy_json))

    result = parse_json_coverage(str(json_path), method_ranges, "scripts/ai/ai_summarizer.py")
    assert result["scripts/ai/ai_summarizer.py"]["AISummarizer.__init__"]["hits"] == 3


def test_empty_method_ranges(coverage_json_path):
    result = parse_json_coverage(coverage_json_path, {}, "scripts/ai/ai_summarizer.py")
    assert result == {"scripts/ai/ai_summarizer.py": {}}

# ---------------------------------------------------------------------------
# 1. exact path match, uses function-level summaries
# ---------------------------------------------------------------------------
def test_exact_match_with_func_summaries(tmp_path: Path) -> None:
    file_path = tmp_path / "pkg" / "mod.py"
    file_path.parent.mkdir()
    file_path.touch()

    files = {
        file_path.as_posix(): {
            "functions": {
                "foo": {
                    "summary": {
                        "percent_covered": 60.0,
                        "covered_lines": 3,
                        "num_statements": 5,
                        "missing_lines": 2,
                    }
                },
                "bar": {
                    "summary": {
                        "percent_covered": 50.0,
                        "covered_lines": 2,
                        "num_statements": 4,
                        "missing_lines": 2,
                    }
                },
            }
        }
    }
    cov_json = _write_cov_json(tmp_path, files)

    out = parse_json_coverage(str(cov_json), METHOD_RANGES, str(file_path))
    res = out[file_path.as_posix()]
    assert res["foo"]["coverage"] == 0.60  # 60 % → 0.60 normalised
    assert res["foo"]["hits"] == 3
    assert res["bar"]["coverage"] == 0.50
    assert res["bar"]["hits"] == 2


# ---------------------------------------------------------------------------
# 2. suffix-fallback match, executed-lines fallback path, mixed slashes
# ---------------------------------------------------------------------------
def test_suffix_fallback_and_executed_lines(tmp_path: Path) -> None:
    # real file lives nested deeper than what’s in coverage json
    real_file = tmp_path / "project" / "src" / "pkg" / "mod.py"
    real_file.parent.mkdir(parents=True)
    real_file.touch()

    # coverage key simulates a Windows path two directories shorter
    coverage_key = r"src\pkg\mod.py"  # back-slashes on purpose
    executed_lines = list(range(1, 6))  # foo fully covered; bar none

    files = {
        coverage_key: {
            "executed_lines": executed_lines,
            # no "functions" dict ⇒ parser falls back to executed_lines slice
        }
    }
    cov_json = _write_cov_json(tmp_path, files)

    result = parse_json_coverage(str(cov_json), METHOD_RANGES, str(real_file))
    res = result[real_file.as_posix()]

    # foo lines 1-5 all executed → 100 % coverage
    assert res["foo"]["coverage"] == 1.0
    assert res["foo"]["hits"] == 5
    # bar lines 6-10 none executed → 0 %
    assert res["bar"]["coverage"] == 0.0
    assert res["bar"]["hits"] == 0
    assert set(res["bar"]["missing_lines"]) == set(range(6, 11))


# ---------------------------------------------------------------------------
# 3. no match at all → fully uncovered
# ---------------------------------------------------------------------------
def test_no_coverage_match_returns_uncovered(tmp_path: Path) -> None:
    target_file = tmp_path / "pkg" / "orphan.py"
    target_file.parent.mkdir()
    target_file.touch()

    # coverage json points to unrelated file
    unrelated = tmp_path / "elsewhere.py"
    unrelated.touch()
    cov_json = _write_cov_json(tmp_path, {unrelated.as_posix(): {}})

    out = parse_json_coverage(str(cov_json), METHOD_RANGES, str(target_file))
    res = out[target_file.as_posix()]
    for method, (start, end) in METHOD_RANGES.items():
        info = res[method]
        assert info["coverage"] == 0.0
        assert info["hits"] == 0
        assert info["lines"] == end - start + 1
        assert info["missing_lines"] == list(range(start, end + 1))