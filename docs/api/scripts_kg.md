# Docstring Report for `scripts/kg/`


## `scripts\kg\__init__`


## `scripts\kg\generate_codebase_kg`


generate_codebase_kg.py
Builds Knowledge Graphs for a Python codebase using docstring summaries.
Analyzes module complexity (density, degree, busyness).
Colors graphs based on complexity.
Usage:
- Load JSON docstring summary
- Build Parent Graph (subpackages)
- Build Child Graphs (per subpackage)
- Analyze complexity
- Visualize with color-coding


### Functions

#### main

Main entry point for the script.
Parses command-line arguments and initializes the CodebaseAnalyzer.