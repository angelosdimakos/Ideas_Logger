# scripts/ci_analyzer/insights/descriptive_insights.py
from typing import Any, Dict, List, Tuple
import re
from collections import Counter
from ..utils.visuals import render_bar, risk_emoji

def generate_complexity_insights(audit: Dict[str, Any]) -> List[str]:
    """
    Generate descriptive complexity insights with narrative and hotspots.
    """
    comp_methods: List[Tuple[str,str,int]] = []
    for fp, data in audit.items():
        for m, obj in data.get('complexity', {}).items():
            if isinstance(obj, dict) and 'complexity' in obj:
                comp_methods.append((fp, m, obj['complexity']))
    total_methods = len(comp_methods)
    high_risk = [(fp,m,s) for fp,m,s in comp_methods if s >=10]
    avg_complexity = sum(s for _,_,s in comp_methods)/total_methods if total_methods else 0
    hotspots = sorted(comp_methods, key=lambda t:-t[2])[:3]

    # One-liner summary
    parts = ["### 🧠 Code Complexity Summary", \
             f"> **In brief:** {total_methods and f'Average complexity is {avg_complexity:.1f}, with {len(high_risk)} method(s) above high-risk threshold (≥10).' or 'No complexity data.'}"]
    # Hotspots
    if hotspots:
        parts.append("> **Hotspots:**")
        for fp,m,s in hotspots:
            parts.append(f"> • `{fp}::{m}` — complexity **{s}**")
    # Metrics
    bar = render_bar((len(high_risk)/total_methods*100) if total_methods else 0)
    emoji = risk_emoji((len(high_risk)/total_methods*100) if total_methods else 0)
    parts += [
        f"- 📈 **Methods ≥10 complexity:** `{len(high_risk)}` {emoji} {bar}  ",
        f"- 🗂️ **Total methods analyzed:** `{total_methods}`  ",
        ""
    ]
    return parts

def generate_testing_insights(audit: Dict[str, Any]) -> List[str]:
    """
    Generate descriptive testing insights with narrative.
    """
    total = sum(len(d.get('testing',{})) for d in audit.values())
    missing = sum(1 for d in audit.values() for v in d.get('testing',{}).values() if v.get('tested') is False)
    if total == 0:
        return ["### 🧪 Testing Insight", \
                "> **Heads‑up:** No testing metadata found—tests aren’t instrumented.", \
                "> *Action:* Instrument your test suite to collect coverage data.", ""]
    covered = total - missing
    pct = covered/total*100
    bar = render_bar(pct)
    emoji = risk_emoji(pct)
    return [
        "### 🧪 Testing Insight",
        f"> **In brief:** Testing coverage is {pct:.1f}% with {covered}/{total} methods covered.",
        f"- **Total Methods:** `{total}`  ",
        f"- **Untested Methods:** `{missing}`  {emoji} {bar}",
        ""
    ]

def generate_quality_insights(audit: Dict[str, Any]) -> List[str]:
    """
    Generate descriptive quality insights with narrative and top errors.
    """
    flake8 = Counter()
    pydoc = Counter()
    mypy = Counter()
    total_files=0
    score_sum=0
    for data in audit.values():
        q = data.get('quality',{})
        if not q: continue
        total_files+=1
        checks=0; pass_count=0
        # collect errors
        for issue in q.get('flake8',{}).get('issues',[]): flake8[issue.get('code')] +=1
        for msg in q.get('pydocstyle',{}).get('issues',[]): pydoc[msg]+=1
        for err in q.get('mypy',{}).get('errors',[]):
            m = re.search(r"\[([^]]+)\]", err)
            if m: mypy[m.group(1)]+=1
        # scoring
        if 'flake8' in q: checks+=1; pass_count += len(q['flake8'].get('issues',[]))==0
        if 'black' in q: checks+=1; pass_count += not q['black'].get('needs_formatting',False)
        if 'mypy' in q: checks+=1; pass_count += len(q['mypy'].get('errors',[]))==0
        if 'pydocstyle' in q: checks+=1; pass_count += len(q['pydocstyle'].get('issues',[]))==0
        if 'coverage' in q: checks+=1; pass_count += q['coverage'].get('percent',0)>=80
        score_sum += (pass_count/checks*100 if checks else 0)
    avg_score = score_sum/total_files if total_files else 0
    bar = render_bar(avg_score); emoji = risk_emoji(avg_score)
    parts = ["### 🧼 Code Quality Insight", \
             f"> **Warning:** Your code quality score is only **{avg_score:.1f}%**—heavy lint and typing debt detected.", \
             "> *Action Items:*", \
             "> 1. Run `black .` to auto-format outstanding files.", \
             "> 2. Tackle top MyPy and Flake8 errors to harden CI.", ""]
    # summary
    parts += [
        f"- **Avg. Quality Score:** `{avg_score:.1f}%` {emoji} {bar}  ",
        f"- **Analyzed Files:** `{total_files}`  ",
        "- **Top Flake8 Errors:**"]
    for code,ct in flake8.most_common(3): parts.append(f"  - `{code}`: {ct}×")
    parts.append("- **Top MyPy Issues:**")
    for code,ct in mypy.most_common(3): parts.append(f"  - `{code}`: {ct}×")
    parts.append("")
    return parts

def generate_diff_insights(audit: Dict[str, Any]) -> List[str]:
    """
    Generate descriptive diff insights with narrative.
    """
    diffs=[d for d in audit.values() if d.get('diff')]
    if not diffs:
        return ["### 🔍 Diff Coverage Insight", \
                "> **Note:** No diffs were reported—either no changes or diff tracking is off.", \
                "> *Action:* Enable diff-based coverage in your CI.", ""]
    total_changed=sum(d.get('changed',0) for d in diffs)
    total_covered=sum(d.get('covered',0) for d in diffs)
    pct= total_covered/total_changed*100 if total_changed else 0
    bar=render_bar(pct); emoji=risk_emoji(pct)
    return [
        "### 🔍 Diff Coverage Insight", \
        f"> **In brief:** New code test coverage is {pct:.1f}% across {len(diffs)} changed files.",
        f"- **Files Changed:** `{len(diffs)}`  ",
        f"- **Diff Coverage:** `{pct:.1f}%` {emoji} {bar}",
        ""
    ]
