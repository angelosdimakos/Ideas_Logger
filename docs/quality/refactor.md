# Code Quality Report for `refactor/`

**Folder Totals:** 31 issues (Critical: 0, High: 14, Medium: 17, Low: 0)

## 📄 Missing Documentation
| File | Module Doc | Missing Classes | Missing Functions |
| ---- | -----------| ----------------| ------------------ |
| ast_extractor.py | Present | ClassMethodExtractor | __init__, visit_ClassDef |
| refactor_guard.py | Present | All Documented | __init__, attach_coverage_hits, analyze_tests, analyze_module, _simple_name, analyze_directory_recursive |
| refactor_guard_cli.py | Missing | All Documented | _ensure_utf8_stdout, _parse_args, _merge_coverage, handle_full_scan, handle_single_file, main |
| strictness_analyzer.py | Present | All Documented | generate_module_report, validate_report_schema, main |

## 🧹 Linting Issues
| File | Critical | High | Medium | Low | Total |
| ---- | -------- | ---- | ------ | --- | ----- |
| ast_extractor.py | 0 | 5 | 0 | 0 | 5 |
| merge_audit_reports.py | 0 | 0 | 2 | 0 | 2 |
| method_line_ranges.py | 0 | 0 | 3 | 0 | 3 |
| refactor_guard.py | 0 | 0 | 5 | 0 | 5 |
| refactor_guard_cli.py | 0 | 2 | 3 | 0 | 5 |
| strictness_analyzer.py | 0 | 1 | 4 | 0 | 5 |
| test_discovery.py | 0 | 6 | 0 | 0 | 6 |
