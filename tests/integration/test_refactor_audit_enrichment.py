import os
import json
import pytest
from scripts.refactor.refactor_guard import RefactorGuard
from scripts.refactor.coverage_parser import parse_coverage_xml_to_method_hits
from scripts.refactor.method_line_ranges import extract_method_line_ranges

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

def test_refactor_guard_enrichment(test_paths):
    guard = RefactorGuard()

    # Extract method ranges from the refactored file
    method_ranges = extract_method_line_ranges(test_paths["refactored"])

    # Load coverage data and attach
    coverage_data = parse_coverage_xml_to_method_hits(test_paths["coverage_path"], method_ranges)
    guard.attach_coverage_hits(coverage_data)

    result = guard.analyze_module(test_paths["original"], test_paths["refactored"])

    # Basic assertions
    assert "Example" in result["method_diff"]
    assert "method_b" in result["method_diff"]["Example"]["added"]
    assert "Example.method_b" in result["complexity"] or "method_b" in result["complexity"]

    method_data = result["complexity"].get("Example.method_b") or result["complexity"].get("method_b")
    assert method_data["coverage"] == 1.0
    assert method_data["hits"] == 1
    assert method_data["lines"] == 1