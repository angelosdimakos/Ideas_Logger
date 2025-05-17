# Docstring Report for `scripts/doc_generation/`


## `scripts\doc_generation\__init__`


## `scripts\doc_generation\coverage_doc_generation`


Split-by-Folder Coverage Documentation Generator
===============================================
Creates one Markdown file per folder:
- ai.md, core.md, etc.
Also generates:
- index.md with folder links


### Functions

#### render_folder_coverage

Renders the markdown content for a single folder's coverage.

#### generate_split_coverage_docs

#### main

## `scripts\doc_generation\quality_doc_generation`


Split-by-Folder Code Quality Markdown Generator
===============================================
Creates one Markdown file per top-level folder:
- ai.md, core.md, etc.
Each file includes:
- Missing documentation
- Linting issues
- Optional: MyPy errors (--verbose)


### Functions

#### render_folder_report

Renders the markdown content for a single folder.

#### generate_split_reports

#### main