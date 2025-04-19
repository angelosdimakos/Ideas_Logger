# coverage_parser.py

import os
import xml.etree.ElementTree as ET
from typing import Dict, Tuple, Set, Any


def parse_coverage_xml_to_method_hits(
    xml_path: str, method_ranges: Dict[str, Tuple[int, int]], source_file_path: str
) -> Dict[str, Dict[str, Any]]:
    """
    Parse coverage XML and map line-level coverage to method-level stats for a single source file.

    Args:
        xml_path: Path to coverage.xml
        method_ranges: { method_name: (start_line, end_line) } for one file
        source_file_path: Path to the source file corresponding to method_ranges.
            Only hits for this file will be counted.

    Returns:
        dict: {
            method_name: {
                "coverage": float,   # fraction 0.0–1.0
                "hits": int,         # number of covered lines
                "lines": int         # total lines in method
            }
        }

    Raises:
        FileNotFoundError: if xml_path does not exist.
        ET.ParseError: if XML is malformed.
    """

    if not os.path.exists(xml_path):
        # Let Python raise FileNotFoundError
        raise FileNotFoundError(f"No coverage.xml found at {xml_path}")

    if not os.path.exists(xml_path):
        # Missing file → FileNotFoundError as expected by tests
        raise FileNotFoundError(f"No coverage.xml found at {xml_path}")

    # Malformed XML → ET.ParseError bubbles up to caller
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Build a map of normalized file paths to their covered line numbers
    hits_by_file: Dict[str, Set[int]] = {}

    # 1) <class filename="...">
    for cls in root.findall(".//class"):
        raw_path = cls.attrib.get("filename")
        if not raw_path:
            continue
        norm = os.path.normpath(raw_path)
        lines = {
            int(line.attrib["number"])
            for line in cls.findall(".//line")
            if int(line.attrib.get("hits", "0")) > 0
        }
        hits_by_file.setdefault(norm, set()).update(lines)

    # 2) <file name="..."> (fallback for other XML schemas)
    for fnode in root.findall(".//file"):
        raw_path = fnode.attrib.get("name") or fnode.attrib.get("filename")
        if not raw_path:
            continue
        norm = os.path.normpath(raw_path)
        lines = {
            int(line.attrib["number"])
            for line in fnode.findall(".//line")
            if int(line.attrib.get("hits", "0")) > 0
        }
        hits_by_file.setdefault(norm, set()).update(lines)

    # Normalize the requested source path
    norm_source = os.path.normpath(source_file_path)

    # Direct match
    file_hits = hits_by_file.get(norm_source, set())

    # Fallback: match by basename if no direct key
    if not file_hits:
        base = os.path.basename(norm_source)
        for path_key, lines in hits_by_file.items():
            if os.path.basename(path_key) == base:
                file_hits = lines
                break

    # Compute method-level coverage
    result: Dict[str, Dict[str, Any]] = {}
    for method, (start, end) in method_ranges.items():
        total = end - start + 1
        hits = sum(1 for ln in range(start, end + 1) if ln in file_hits)
        coverage = (hits / total) if total > 0 else 0.0
        result[method] = {"coverage": coverage, "hits": hits, "lines": total}

    return result
