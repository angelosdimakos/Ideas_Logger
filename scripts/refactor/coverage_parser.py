import os
import xml.etree.ElementTree as ET
from typing import Dict, Tuple, Set

def parse_coverage_xml_to_method_hits(xml_path: str, method_ranges: Dict[str, Tuple[int, int]]) -> Dict[str, Dict]:
    """
    Parse coverage.xml and map line-level coverage to method-level stats.

    Args:
        xml_path (str): Path to coverage.xml
        method_ranges (dict): { method_name: (start_line, end_line) }

    Returns:
        dict: { method_name: {coverage, hits, lines} }
    """
    if not os.path.exists(xml_path):
        print(f"❌ No coverage.xml found at {xml_path}")
        return {}

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"❌ Failed to parse XML: {e}")
        return {}

    file_line_hits = _extract_file_line_hits(root)
    return _compute_method_coverage(method_ranges, file_line_hits)

def _extract_file_line_hits(root: ET.Element) -> Dict[str, Set[int]]:
    file_line_hits = {}
    for cls in root.findall(".//class"):
        file_path = cls.attrib.get("filename")
        if not file_path:
            continue
        hit_lines = {
            int(line.attrib["number"])
            for line in cls.findall("lines/line")
            if int(line.attrib.get("hits", 0)) > 0
        }
        file_line_hits[file_path] = hit_lines
    return file_line_hits

def _compute_method_coverage(method_ranges: Dict[str, Tuple[int, int]], file_line_hits: Dict[str, Set[int]]) -> Dict[str, Dict]:
    method_coverage = {}
    for method, (start, end) in method_ranges.items():
        total_lines = end - start + 1
        hit_count = 0
        for lineno in range(start, end + 1):
            if any(lineno in hits for hits in file_line_hits.values()):
                hit_count += 1

        method_coverage[method] = {
            "coverage": hit_count / total_lines if total_lines > 0 else 0.0,
            "hits": hit_count,
            "lines": total_lines
        }
    return method_coverage