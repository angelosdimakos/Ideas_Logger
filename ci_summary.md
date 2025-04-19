
## 🔍 CI Audit Summary

Each section includes:
- 📊 Metric summaries
- 🚨 Emoji Risk Indicators (🟢 Low, 🟡 Medium, 🔴 High)
- ▓▓ Visual bar indicators (Markdown style)

### 🗒️ Overview

- **Total Files Audited:** `100`
- **Files with Missing Tests:** `30`
- **Total Missing Tests:** `158`
- **Methods (Complexity ≥10):** `11`
- **Files with Avg Complexity ≥10:** `2`
- **Average Method Complexity:** `3.3`
- **Total Flake8 Issues:** `104`
- **Files Needing Black Formatting:** `16`
- **Total MyPy Errors:** `211`
- **Total Pydocstyle Issues:** `616`
- **Average Coverage %:** `76.8%`
- **Testing Coverage:** `N/A`
- **Diff Coverage:** `N/A`

### 🎯 Prime Suspects

- **Top Flake8 Errors:**
  - `E501`: 49 occurrences
  - `F401`: 17 occurrences
  - `E402`: 11 occurrences
- **Top Pydocstyle Issues:**
  - `D100: Missing docstring in public module`: 45 occurrences
  - `D200: One-line docstring should fit on one line with quotes (found 3)`: 39 occurrences
  - `D102: Missing docstring in public method`: 36 occurrences
- **Top MyPy Error Codes:**
  - `no-untyped-def`: 152 occurrences
  - `call-arg`: 42 occurrences
  - `assignment`: 5 occurrences
- **Highest Complexity Methods:**
  - `refactor/refactor_guard.py::analyze_module`: Complexity 21
  - `refactor/coverage_parser.py::parse_coverage_xml_to_method_hits`: Complexity 18
  - `refactor/refactor_guard.py::analyze_tests`: Complexity 14

### 🧠 Code Complexity Summary
> **In brief:** Average complexity is 3.3, with 11 method(s) above high-risk threshold (≥10).
> **Hotspots:**
> • `refactor/refactor_guard.py::analyze_module` — complexity **21**
> • `refactor/coverage_parser.py::parse_coverage_xml_to_method_hits` — complexity **18**
> • `refactor/refactor_guard.py::analyze_tests` — complexity **14**
- 📈 **Methods ≥10 complexity:** `11` 🔴 ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜  
- 🗂️ **Total methods analyzed:** `235`  

### 🧪 Testing Insight
> **Heads‑up:** No testing metadata found—tests aren’t instrumented.
> *Action:* Instrument your test suite to collect coverage data.

### 🧼 Code Quality Insight
> **Warning:** Your code quality score is only **18.8%**—heavy lint and typing debt detected.
> *Action Items:*
> 1. Run `black .` to auto-format outstanding files.
> 2. Tackle top MyPy and Flake8 errors to harden CI.

- **Avg. Quality Score:** `18.8%` 🔴 🟩🟩⬜⬜⬜⬜⬜⬜⬜⬜  
- **Analyzed Files:** `100`  
- **Top Flake8 Errors:**
  - `E501`: 49×
  - `F401`: 17×
  - `E402`: 11×
- **Top MyPy Issues:**
  - `no-untyped-def`: 152×
  - `call-arg`: 42×
  - `assignment`: 5×

### 🔍 Diff Coverage Insight
> **Note:** No diffs were reported—either no changes or diff tracking is off.
> *Action:* Enable diff-based coverage in your CI.
