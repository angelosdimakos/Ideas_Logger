import os
import xml.etree.ElementTree as ET
from typing import Dict, Tuple, Any, Set


def parse_coverage_xml_to_method_hits(
    xml_path: str,
    method_ranges: Dict[str, Tuple[int, int]],
    source_file_path: str,
) -> Dict[str, Dict[str, Any]]:
    """
    Parse coverage XML and map line-level coverage to method-level stats for a single source file.

    - Only lines with hits>0 are considered 'covered'.
    - Matches on the basename of `source_file_path`.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Build a map: normalized_xml_filename -> set(line_numbers_with_hits>0)
    hits_by_file: Dict[str, Set[int]] = {}
    for cls in root.findall(".//class"):
        fname = cls.get("filename")
        if not fname:
            continue
        norm = os.path.normpath(fname)
        file_hits: Set[int] = set()
        lines_elem = cls.find("lines")
        if lines_elem is None:
            continue
        for ln in lines_elem.findall("line"):
            num = int(ln.get("number", "0"))
            count = int(ln.get("hits", "0"))
            if count > 0:
                file_hits.add(num)
        hits_by_file.setdefault(norm, set()).update(file_hits)

    # Pick out only the hits for our one source file
    base = os.path.basename(os.path.normpath(source_file_path))
    file_hits: Set[int] = set()
    for path_key, lines in hits_by_file.items():
        if os.path.basename(path_key) == base:
            file_hits = lines
            break

    # Now compute per-method coverage
    result: Dict[str, Dict[str, Any]] = {}
    for method, (start, end) in method_ranges.items():
        total = end - start + 1
        hits = sum(1 for ln in range(start, end + 1) if ln in file_hits)
        coverage = (hits / total) if total > 0 else 0.0
        result[method] = {"coverage": coverage, "hits": hits, "lines": total}

    return result
