# tests/unit/refactor/test_coverage_parser.py

import os
import pytest
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring

from scripts.refactor.coverage_parser import parse_coverage_xml_to_method_hits


def _write_xml(tmp_path, root):
    xml_bytes = tostring(root, encoding="utf-8", xml_declaration=True)
    p = tmp_path / "coverage.xml"
    p.write_bytes(xml_bytes)
    return str(p)


def test_no_coverage_file_raises(tmp_path):
    missing = tmp_path / "nope.xml"
    with pytest.raises(FileNotFoundError):
        parse_coverage_xml_to_method_hits(
            str(missing), {"m": (1,1)}, source_file_path="foo.py"
        )


def test_malformed_xml_raises(tmp_path):
    p = tmp_path / "coverage.xml"
    p.write_text("<coverage><class></coverage>", encoding="utf-8")
    with pytest.raises(ET.ParseError):
        parse_coverage_xml_to_method_hits(
            str(p), {"m": (1,1)}, source_file_path="foo.py"
        )


def test_single_file_method_coverage(tmp_path):
    root = Element("coverage")
    cls = SubElement(root, "class", filename="foo.py")
    lines = SubElement(cls, "lines")
    SubElement(lines, "line", number="1", hits="1")
    SubElement(lines, "line", number="2", hits="1")
    SubElement(lines, "line", number="3", hits="0")
    xml_path = _write_xml(tmp_path, root)

    method_ranges = {"m1": (1,2), "m2": (2,4)}
    result = parse_coverage_xml_to_method_hits(
        xml_path, method_ranges, source_file_path="foo.py"
    )

    assert result["m1"]["coverage"] == 1.0
    assert result["m1"]["hits"] == 2
    assert result["m1"]["lines"] == 2

    assert pytest.approx(result["m2"]["coverage"], rel=1e-6) == 1/3
    assert result["m2"]["hits"] == 1
    assert result["m2"]["lines"] == 3


def test_path_normalization(tmp_path):
    root = Element("coverage")
    cls = SubElement(root, "class", filename="./bar.py")
    lines = SubElement(cls, "lines")
    SubElement(lines, "line", number="10", hits="1")
    xml_path = _write_xml(tmp_path, root)

    method_ranges = {"a": (10,10)}
    result = parse_coverage_xml_to_method_hits(
        xml_path, method_ranges, source_file_path="bar.py"
    )

    assert result["a"]["coverage"] == 1.0
    assert result["a"]["hits"] == 1
    assert result["a"]["lines"] == 1
