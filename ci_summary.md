
## 🔍 CI Audit Summary

Each section includes:
- 📊 Metric summaries
- 🚨 Emoji Risk Indicators (🟢 Low, 🟡 Medium, 🔴 High)
- ▓▓ Visual bar indicators (Markdown style)

### 🗒️ Overview

- **Total Files Audited:** `98`
- **Files with Missing Tests:** `26`
- **Total Missing Tests:** `149`
- **Methods (Complexity ≥10):** `16`
- **Files with Avg Complexity ≥10:** `5`
- **Average Method Complexity:** `3.7`
- **Total Flake8 Issues:** `216`
- **Files Needing Black Formatting:** `0`
- **Total MyPy Errors:** `224`
- **Total Pydocstyle Issues:** `639`
- **Average Coverage %:** `62.1%`
- **Testing Coverage:** `N/A`
- **Diff Coverage:** `N/A`

### 🎯 Prime Suspects

- **Top Flake8 Errors:**
  - `E501`: 50 occurrences
  - `E231`: 29 occurrences
  - `E225`: 24 occurrences
- **Top Pydocstyle Issues:**
  - `D100: Missing docstring in public module`: 49 occurrences
  - `D103: Missing docstring in public function`: 44 occurrences
  - `D200: One-line docstring should fit on one line with quotes (found 3)`: 41 occurrences
- **Top MyPy Error Codes:**
  - `no-untyped-def`: 161 occurrences
  - `call-arg`: 41 occurrences
  - `attr-defined`: 5 occurrences
- **Highest Complexity Methods:**
  - `insights\overview.py::generate_overview_insights`: Complexity 41
  - `ci_analyzer\ci_trends.py::extract_metrics`: Complexity 21
  - `refactor\refactor_guard.py::analyze_module`: Complexity 21

### 🧠 Code Complexity Summary
> **In brief:** Average complexity is 3.7, with 16 method(s) above high-risk threshold (≥10).
> **Hotspots:**
> • `insights\overview.py::generate_overview_insights` — complexity **41**
> • `ci_analyzer\ci_trends.py::extract_metrics` — complexity **21**
> • `refactor\refactor_guard.py::analyze_module` — complexity **21**
- 📈 **Methods ≥10 complexity:** `16` 🔴 🟩⬜⬜⬜⬜⬜⬜⬜⬜⬜  
- 🗂️ **Total methods analyzed:** `247`  

### 🧪 Testing Insight
> **Heads‑up:** No testing metadata found—tests aren’t instrumented.
> *Action:* Instrument your test suite to collect coverage data.

### 🧼 Code Quality Insight
> **Warning:** Your code quality score is only **15.1%**—heavy lint and typing debt detected.
> *Action Items:*
> 1. Run `black .` to auto-format outstanding files.
> 2. Tackle top MyPy and Flake8 errors to harden CI.

- **Avg. Quality Score:** `15.1%` 🔴 🟩🟩⬜⬜⬜⬜⬜⬜⬜⬜  
- **Analyzed Files:** `89`  
- **Top Flake8 Errors:**
  - `E501`: 50×
  - `E231`: 29×
  - `E225`: 24×
- **Top MyPy Issues:**
  - `no-untyped-def`: 161×
  - `call-arg`: 41×
  - `attr-defined`: 5×

### 🔍 Diff Coverage Insight
> **Note:** No diffs were reported—either no changes or diff tracking is off.
> *Action:* Enable diff-based coverage in your CI.
