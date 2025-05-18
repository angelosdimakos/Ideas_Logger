# Documentation with MkDocs

This project includes automatic documentation generation using MkDocs. The documentation is built automatically by the CI pipeline and published to GitHub Pages.

## Documentation Structure

The documentation includes:

- **API Documentation**: Generated from docstrings in the source code
- **Test Coverage Reports**: Details about test coverage across the codebase
- **Code Quality Metrics**: Information about linting, docstring coverage, and other quality metrics

## Local Development

To work with the documentation locally:

1. Install MkDocs and required plugins:

```bash
pip install mkdocs-material mkdocstrings mkdocstrings-python
```

2. Generate API documentation:

```bash
python scripts/refactor/parsers/docstring_parser.py --mkdocs --json
```

3. Run MkDocs development server:

```bash
mkdocs serve
```

This will start a local development server at http://127.0.0.1:8000/ where you can preview the documentation.

## Automatic Deployment

The documentation is automatically built and deployed when changes are pushed to the main branch. The process includes:

1. Running tests, linting, and other quality checks
2. Generating API documentation from docstrings
3. Creating coverage and quality reports
4. Building the MkDocs site
5. Deploying to GitHub Pages

## Documentation Files

- `mkdocs.yml`: MkDocs configuration
- `docs/`: Contains markdown files for documentation
- `docs/api/`: Auto-generated API documentation

## How It Works

The documentation generation is integrated into the CI pipeline:

1. `scripts/refactor/parsers/docstring_parser.py` extracts docstrings and generates markdown
2. `scripts/ci_analyzer/generate_coverage_docs.py` creates coverage reports
3. `scripts/ci_analyzer/generate_quality_docs.py` creates quality metric reports
4. GitHub Actions builds and deploys the MkDocs site

You can access the published documentation at: `https://angelosdimakos.github.io/Ideas_Logger/`