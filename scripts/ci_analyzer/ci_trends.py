import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import argparse


def load_audit(path: str = "refactor_audit.json") -> Dict[str, Any]:
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def extract_metrics(audit: Dict[str, Any]) -> Dict[str, Any]:
    total_files = len(audit)
    total_methods = sum(len(file.get("complexity", {})) for file in audit.values())

    total_missing_tests = sum(len(file.get("missing_tests", [])) for file in audit.values())

    risky_methods = 0
    for file in audit.values():
        for method in file.get("complexity", {}).values():
            if method.get("coverage") == 0 or method.get("cyclomatic", 0) > 10:
                risky_methods += 1

    return {
        "files": total_files,
        "methods": total_methods,
        "missing_tests": total_missing_tests,
        "risky": risky_methods,
    }


def compare_metrics(current: Dict[str, Any], previous: Dict[str, Any]) -> Dict[str, Any]:
    delta = {}
    for key in current:
        prev = previous.get(key, 0)
        delta[key] = current[key] - prev
    return delta


def save_metrics(metrics: Dict[str, Any], out_path: str = ".ci-history/last_metrics.json"):
    Path(".ci-history").mkdir(exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


def load_previous_metrics(path: str = ".ci-history/last_metrics.json") -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def print_comparison(current: Dict[str, Any], delta: Dict[str, Any]):
    print("\n🔁 CI Metric Comparison:")
    for key in current:
        sign = "🔺" if delta[key] > 0 else "🔻" if delta[key] < 0 else "➡️"
        print(f"- {key}: {current[key]} ({sign} {delta[key]})")


def main():
    parser = argparse.ArgumentParser(description="Compare audit metrics with previous CI run.")
    parser.add_argument("--audit", type=str, default="refactor_audit.json", help="Path to audit JSON")
    args = parser.parse_args()

    audit = load_audit(args.audit)
    current_metrics = extract_metrics(audit)
    previous_metrics = load_previous_metrics()
    delta = compare_metrics(current_metrics, previous_metrics)

    print_comparison(current_metrics, delta)
    save_metrics(current_metrics)


if __name__ == "__main__":
    main()
