# scripts/ci_analyzer/ci_trends.py
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Store metrics in the module-local .ci-history folder
METRIC_PATH = Path(__file__).parent / ".ci-history"
METRIC_PATH.mkdir(exist_ok=True)

KEY_METRICS = [
    "coverage", "quality_score", "methods_over_threshold", "files_with_avg_complexity_gt_10"
]

def extract_metrics(audit: Dict[str, any]) -> Dict[str, float]:
    """Compute a minimal metrics dict from the audit."""
    comp_scores = []
    file_avgs = []
    for d in audit.values():
        complexity_data = d.get("complexity", {})
        scores = []
        for v in complexity_data.values():
            if isinstance(v, dict):
                score = v.get("complexity") or v.get("score")
                if isinstance(score, (int, float)):
                    scores.append(score)
        if scores:
            comp_scores.extend(scores)
            file_avgs.append(sum(scores) / len(scores))
    methods_over_10 = sum(1 for s in comp_scores if s >= 10)
    files_avg_10 = sum(1 for avg in file_avgs if avg >= 10)

    quality_scores = []
    for d in audit.values():
        q = d.get("quality", {})
        checks = 0
        score = 0
        if isinstance(q, dict):
            if "flake8" in q: checks += 1; score += int(len(q["flake8"].get("issues", [])) == 0)
            if "black" in q: checks += 1; score += int(not q["black"].get("needs_formatting", False))
            if "mypy" in q: checks += 1; score += int(len(q["mypy"].get("errors", [])) == 0)
            if "pydocstyle" in q: checks += 1; score += int(len(q["pydocstyle"].get("issues", [])) == 0)
            if "coverage" in q: checks += 1; score += int(q["coverage"].get("percent", 0) >= 80)
        if checks:
            quality_scores.append(score / checks * 100)
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

    coverages = [
        d.get("quality", {}).get("coverage", {}).get("percent", 0)
        for d in audit.values()
        if d.get("quality", {}).get("coverage")
    ]
    avg_cov = sum(coverages) / len(coverages) if coverages else 0

    return {
        "coverage": round(avg_cov, 2),
        "quality_score": round(avg_quality, 2),
        "methods_over_threshold": methods_over_10,
        "files_with_avg_complexity_gt_10": files_avg_10,
    }

def save_metrics(metrics: Dict[str, float]) -> Path:
    now = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
    out_file = METRIC_PATH / f"metrics_{now}.json"
    out_file.write_text(json.dumps(metrics, indent=2))
    return out_file

def load_last_metrics() -> Optional[Dict[str, float]]:
    all = sorted(METRIC_PATH.glob("metrics_*.json"))
    if len(all) < 2:
        return None
    with open(all[-2], encoding="utf-8") as f:
        return json.load(f)

def generate_trend_summary(new: Dict[str, float], old: Optional[Dict[str, float]]) -> str:
    lines = ["### 📉 Trends Compared to Last Run\n"]
    if not old:
        lines.append("> No previous run to compare.\n")
        return "\n".join(lines)
    for k in KEY_METRICS:
        prev = old.get(k, 0)
        curr = new.get(k, 0)
        delta = curr - prev
        sign = "+" if delta >= 0 else ""
        lines.append(f"- `{k}`: `{curr}` ({sign}{delta:.2f} from last)")
    lines.append("")
    return "\n".join(lines)

if __name__ == "__main__":
    audit_path = Path("refactor_audit.json")
    audit = json.loads(audit_path.read_text(encoding="utf-8-sig"))
    latest_metrics = extract_metrics(audit)
    print("🔍 Extracted Metrics:", latest_metrics)
    previous_metrics = load_last_metrics()
    print(generate_trend_summary(latest_metrics, previous_metrics))
    save_metrics(latest_metrics)
    print(f"✅ Metrics recorded at {METRIC_PATH.relative_to(Path.cwd())}/")