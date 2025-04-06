import os
import json
import pytest
from scripts.refactor.refactor_guard import RefactorGuard, parse_coverage_with_debug

@pytest.fixture
def test_paths(tmp_path):
    # Create dummy files for original and refactored
    orig_file = tmp_path / "original.py"
    ref_file = tmp_path / "refactored.py"

    orig_file.write_text("""
class Example:
    def method_a(self): pass
""")

    ref_file.write_text("""
class Example:
    def method_a(self): pass
    def method_b(self): return 42
""")

    # Also write a fake coverage.xml with method_b having 100% coverage
    coverage_dir = tmp_path / "htmlcov"
    coverage_dir.mkdir()
    (coverage_dir / "coverage.xml").write_text('''
<coverage>
  <packages>
    <package name="example" >
      <classes>
        <class name="Example" filename="refactored.py">
          <methods>
            <method name="method_b">
              <lines>
                <line number="3" hits="1"/>
              </lines>
            </method>
          </methods>
        </class>
      </classes>
    </package>
  </packages>
</coverage>
''')

    return {
        "original": str(orig_file),
        "refactored": str(ref_file),
        "coverage_path": str(coverage_dir / "coverage.xml")
    }

def test_refactor_guard_enrichment(test_paths, monkeypatch):
    # Patch coverage search to only use our test coverage file
    monkeypatch.setattr("scripts.refactor.refactor_guard.parse_coverage_with_debug", lambda **_: parse_coverage_with_debug([test_paths["coverage_path"]], verbose=True))

    guard = RefactorGuard()
    result = guard.analyze_module(test_paths["original"], test_paths["refactored"])

    # Basic assertions
    assert "Example" in result["method_diff"]
    assert "method_b" in result["method_diff"]["Example"]["added"]
    assert "Example.method_b" in result["complexity"] or "method_b" in result["complexity"]

    method_data = result["complexity"].get("Example.method_b") or result["complexity"].get("method_b")
    assert method_data["coverage"] == 1.0
    assert method_data["hits"] == 1
    assert method_data["lines"] == 1
