"""
tests/test_merge_audit_reports.py
================================

Strict regression-tests for merge_audit_reports.py

• 100 % fixture-driven (no monkey-patching side-effects)
• OOP wrapper for clarity (unittest-style)
• Pytest parametrisation for path-normalisation edge-cases
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import pytest
from dataclasses import dataclass

# ── system under test ──────────────────────────────────────────────────────────
from scripts.refactor.merge_audit_reports import merge_reports, normalize_path


# ── helper dataclass to manage temp-fixture copies ─────────────────────────────
@dataclass(slots=True)
class FixtureRepo:
    doc: Path
    cov: Path
    lint: Path
    out: Path

    @classmethod
    def create(cls, tmp_path: Path) -> "FixtureRepo":
        """
        Copy JSON fixture files into a fresh temp repo and return their paths.

        Priority of search:
        1. tests/fixtures/            (canonical location)
        2. project root               (fallback)
        """
        root = tmp_path / "repo"
        root.mkdir()

        proj_root = Path(__file__).resolve().parents[3]
        fixtures_dir = proj_root / "tests" / "fixtures"

        copies: dict[str, Path] = {}
        for stem in ("docstring_summary", "refactor_audit", "linting_report"):
            # try <tests/fixtures> first, then project root
            for base in (fixtures_dir, proj_root):
                src = base / f"{stem}.json"
                if src.exists():
                    break
            else:  # not found anywhere
                raise FileNotFoundError(
                    f"Fixture '{stem}.json' not found in "
                    f"{fixtures_dir} or project root"
                )

            tgt = root / src.name
            shutil.copy(src, tgt)
            copies[stem.split("_")[0]] = tgt  # keys: doc, refactor, linting

        return cls(
            doc=copies["docstring"],
            cov=copies["refactor"],
            lint=copies["linting"],
            out=root / "merged.json",
        )


# ───────────────────────────────────────────────────────────────────────────────
class TestMergeAuditReports:
    """OOP wrapper holding all strict tests for the merge routine."""

    # -------- fixtures --------------------------------------------------------
    @pytest.fixture(autouse=True)
    def _repo(self, tmp_path) -> None:
        """Set up fresh repo per test method."""
        self.repo = FixtureRepo.create(tmp_path)

    # -------- path-normalisation guarantees -----------------------------------
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            (r"C:\repo\project\scripts\core\file.py", "core/file.py"),
            ("/home/user/project/scripts/utils/helper.py", "utils/helper.py"),
            ("scripts/module/sub/file.py", "module/sub/file.py"),
        ],
    )
    def test_normalize_examples(self, raw: str, expected: str):
        """Explicit OS-agnostic examples must produce identical rel-paths."""
        assert normalize_path(raw) == expected

    # -------- happy-path full merge -------------------------------------------
    def test_merge_preserves_all_data(self):
        """Union of keys & deep equality for every sub-block."""
        merge_reports(
            self.repo.doc, self.repo.cov, self.repo.lint, self.repo.out
        )
        merged = json.loads(self.repo.out.read_text(encoding="utf-8"))
        doc = json.loads(self.repo.doc.read_text(encoding="utf-8"))
        cov = json.loads(self.repo.cov.read_text(encoding="utf-8"))
        lint = json.loads(self.repo.lint.read_text(encoding="utf-8"))

        # 1️⃣ exact key-set equality
        expected_keys = (
            {normalize_path(k) for k in doc}
            | {normalize_path(k) for k in cov}
            | {normalize_path(k) for k in lint}
        )
        assert set(merged) == expected_keys

        # 2️⃣ deep sub-dict equality
        # Normalize all keys once to avoid lookup mismatches
        doc_norm = {normalize_path(k): v for k, v in doc.items()}
        cov_norm = {normalize_path(k): v for k, v in cov.items()}
        lint_norm = {normalize_path(k): v for k, v in lint.items()}

        for fp, bundle in merged.items():
            if fp in doc_norm:
                assert bundle.get("docstrings", {}) == doc_norm[fp]
            else:
                assert "docstrings" not in bundle

            if fp in cov_norm:
                assert bundle.get("coverage", {}) == cov_norm[fp]
            else:
                assert "coverage" not in bundle

            if fp in lint_norm:
                assert bundle.get("linting", {}) == lint_norm[fp]
            else:
                assert "linting" not in bundle

    # -------- guard against mutating inputs -----------------------------------
    def test_inputs_not_mutated(self):
        """Byte hash of original doc JSON must remain identical."""
        before = self.repo.doc.read_bytes()
        merge_reports(
            self.repo.doc, self.repo.cov, self.repo.lint, self.repo.out
        )
        assert self.repo.doc.read_bytes() == before

    # -------- strict failure on corrupt JSON ----------------------------------
    def test_bad_json_raises(self, tmp_path):
        """Any malformed input must raise JSONDecodeError."""
        bad = tmp_path / "broken.json"
        bad.write_text("{ not : json", encoding="utf-8")  # invalid

        good = tmp_path / "good.json"
        good.write_text("{}", encoding="utf-8")

        with pytest.raises(json.JSONDecodeError):
            # supply the bad file as `linting`
            merge_reports(good, good, bad, tmp_path / "out.json")
