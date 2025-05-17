import json
import re
from pathlib import Path
import argparse
import os
import ast

from scripts.ai.ai_summarizer import AISummarizer
from scripts.config.config_manager import ConfigManager
from scripts.ai.llm_router import get_prompt_template, apply_persona


def suggest_new_modules(
    artifact_path: str,
    config: ConfigManager,
    subcategory: str = "Architecture Planning",
    path_filter: str | None = None,
) -> tuple[str, str]:
    """
    Generates new module or package suggestions and corresponding Python prototype code based on an architecture report.
    
    Reads a JSON report of existing modules and their documented functions, optionally filtered by path substring. Summarizes current functionality, prompts an AI summarizer to propose complementary modules/packages with technical justifications, and then generates Python code stubs for the suggested modules following strict naming conventions.
    
    Args:
        artifact_path: Path to the JSON architecture report.
        subcategory: Optional subcategory for prompt context (default: "Architecture Planning").
        path_filter: Optional substring to filter modules by file path.
    
    Returns:
        A tuple containing the textual module/package suggestions and the generated Python prototype code stubs.
    """
    with open(artifact_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    summaries = []
    for file_path, data in report.items():
        if path_filter and path_filter not in file_path:
            continue
        funcs = data.get("docstrings", {}).get("functions", [])
        for entry in funcs:
            name = entry.get("name", "unknown")
            desc = (entry.get("description") or "").strip()
            summaries.append(f"- `{name}`: {desc}")

    if not summaries:
        return "No modules with docstrings matched the filter.", ""

    module_context = "\n".join(summaries)
    prompt = get_prompt_template(subcategory, config)
    full_prompt = f"""{prompt}

The following is a detailed breakdown of functional modules under {f'`{path_filter}`' if path_filter else 'the entire project'}:

{module_context}

Based on these implemented components, propose new modules or packages that would complement this area.

For each suggestion, provide:
- 📁 **Module/Package Name**
- 🎯 **Purpose**
- 🛠 **Suggested Integrations**
- 📝 **Justification**

Keep the output succinct but highly technical.

IMPORTANT: Follow these naming conventions strictly:
- Use snake_case for module names (e.g., data_processor, not DataProcessor)
- Use PascalCase for class names (e.g., DataProcessor, not data_processor)
- Use snake_case for function names (e.g., process_data, not processData)
"""
    final_prompt = apply_persona(full_prompt.strip(), config.persona)
    summarizer = AISummarizer()
    suggestions = summarizer.summarize_entry(final_prompt, subcategory=subcategory)

    prototype_prompt = f"""
Using the following module suggestions, generate Python code stubs.

Guidelines:
- Provide realistic module and class/function names.
- Include proper docstrings specifying purpose and parameters.
- Provide only structural scaffolding.
- Output clearly using Markdown code blocks and filenames.
- Include "# Suggested Integrations: ..." comments where appropriate.
- Always specify the correct module filename using "# Filename: <path/module.py>", matching the proposed module name.

STRICT NAMING CONVENTIONS:
- Module names MUST use snake_case (e.g., data_processor.py)
- Class names MUST use PascalCase (e.g., DataProcessor)
- Function names MUST use snake_case (e.g., process_data)
- Follow PEP 8 style guide for Python code

Module Suggestions:
{suggestions}
"""
    prototype_prompt_final = apply_persona(prototype_prompt.strip(), config.persona)
    prototype_code = summarizer.summarize_entry(
        prototype_prompt_final, subcategory="Module Prototype"
    )

    return suggestions, prototype_code


def generate_test_stubs(prototype_code: str, config: ConfigManager) -> str:
    """
    Generates pytest unit test stubs for the provided module prototype code.
    
    The generated test stubs follow naming conventions, include multiple test functions per original function or method, use pytest fixtures where appropriate, and are formatted with filename annotations for easy export.
    
    Args:
        prototype_code: The Python prototype code for which to generate test stubs.
        config: Configuration manager containing persona and summarizer settings.
    
    Returns:
        A string containing the generated pytest test stubs in Markdown code blocks.
    """
    summarizer = AISummarizer()
    prompt = f"""
Using the following module prototypes, generate corresponding pytest unit test stubs.

Guidelines:
- Test modules MUST be named with test_ prefix (e.g., test_data_processor.py)
- Test functions MUST be named with test_ prefix (e.g., test_process_data)
- Include at least 2 test functions for EACH function/method in the original modules
- Use realistic function names like `test_<function>_expected_behavior`
- Include `assert` statements with placeholders
- Use pytest fixtures where appropriate
- Cover each function/class in the prototypes
- Prepend each code block with a comment '# Filename: test_<module_name>.py' where <module_name> is the original module filename without extension
- Output clearly using Markdown code blocks and filenames

Module Prototypes:
{prototype_code}
"""
    final_prompt = apply_persona(prompt.strip(), config.persona)
    return summarizer.summarize_entry(final_prompt, subcategory="Test Generation")


def extract_filenames_from_code(code: str) -> list[str]:
    """
    Extracts Python filenames from code blocks by searching for '# Filename: <filename.py>' comments.
    
    Args:
        code: A string containing code blocks with embedded filename comments.
    
    Returns:
        A list of extracted Python filenames found in the code.
    """
    return [match.group(1).strip() for match in re.finditer(r"# Filename:\s*([^\n]+\.py)", code)]


def export_prototypes_to_files(
    prototype_code: str,
    output_dir: str = "prototypes",
    suggestions: str = "",
    is_test: bool = False,
):
    """
    Writes generated prototype or test code blocks to files based on embedded filename comments.
    
    Extracts Python code blocks from the input string, determines target filenames from `# Filename:` comments, and writes each code block to the specified output directory. For test files, ensures filenames are prefixed with `test_` and prepends necessary imports. Skips code blocks without filename annotations and prints status messages for each file created.
    """
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    code_blocks = re.findall(r"```python\n(.*?)```", prototype_code, re.DOTALL)

    if not code_blocks:
        print("⚠️ No code blocks found to export!")
        return

    for block in code_blocks:
        # Determine filename
        filename_match = re.search(r"# Filename:\s*([^\n]+\.py)", block)
        if filename_match:
            filename = filename_match.group(1).strip()
        else:
            print("⚠️ Could not find '# Filename' in code block, skipping.")
            continue

        # Adjust for tests
        if is_test and not os.path.basename(filename).startswith("test_"):
            dirname = os.path.dirname(filename)
            base = os.path.basename(filename)
            filename = os.path.join(dirname, f"test_{base}") if dirname else f"test_{base}"

        normalized = Path(filename)
        file_path = output_dir_path / normalized
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Prepare imports
        imports = []
        if is_test:
            imports.append("import pytest")
        cleaned = re.sub(r"# Filename:.*?\n", "", block).strip()

        # Write file
        with open(file_path, "w", encoding="utf-8") as f:
            if imports:
                f.write("\n".join(imports) + "\n\n")
            f.write(cleaned + "\n")

        print(f"✅ Created file: {file_path}")

    print(f"📂 Files written to '{output_dir}/'.")


def validate_test_coverage(module_dir: str, test_dir: str) -> list[str]:
    """
    Checks that all public functions and methods in a module directory have corresponding pytest test functions.
    
    Parses Python source files to identify public functions and methods, scans test files for matching test functions, reports missing coverage, and returns a list of uncovered items.
    
    Args:
        module_dir: Path to the directory containing module source files.
        test_dir: Path to the directory containing pytest test files.
    
    Returns:
        A list of public function and method names (with module and class context) that lack corresponding tests.
    """
    module_functions: dict[str, bool] = {}

    # Traverse module files and collect public functions and methods
    for module_file in Path(module_dir).rglob("*.py"):
        module_name = module_file.stem
        tree = ast.parse(module_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                module_functions[f"{module_name}.{node.name}"] = False
            elif isinstance(node, ast.ClassDef):
                class_name = node.name
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                        module_functions[f"{module_name}.{class_name}.{item.name}"] = False

    tested_names: set[str] = set()
    # Scan test files for test function definitions
    for test_file in Path(test_dir).rglob("test_*.py"):
        content = test_file.read_text(encoding="utf-8")
        for match in re.finditer(r"def\s+test_(\w+)", content):
            tested_names.add(match.group(1))

    # Mark tested modules
    for full_name in list(module_functions.keys()):
        func_name = full_name.split(".")[-1]
        if func_name in tested_names:
            module_functions[full_name] = True

    # Identify missing tests
    missing = [name for name, covered in module_functions.items() if not covered]

    if missing:
        print("\n⚠️ Missing test coverage for these items:")
        for m in missing:
            print(f"  - {m}")
    else:
        print("\n✅ All public functions and methods are tested!")

    total = len(module_functions)
    covered = total - len(missing)
    percent = (covered / total * 100) if total else 100.0
    print(f"📊 Test coverage: {percent:.1f}% ({covered}/{total})")

    return missing


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate module and test stubs based on architecture report."
    )
    parser.add_argument("input", help="Path to merged_report.json")
    parser.add_argument("--to", help="Optional path to save suggestions (Markdown).")
    parser.add_argument(
        "--prototype", action="store_true", help="Generate and export prototype .py stubs."
    )
    parser.add_argument(
        "--proto-dir", help="Directory to save prototype .py files. Defaults to 'prototypes/'."
    )
    parser.add_argument("--tests", action="store_true", help="Generate pytest test stubs.")
    parser.add_argument(
        "--test-dir", help="Directory to save test stubs. Defaults to 'prototypes_tests/'."
    )
    parser.add_argument(
        "--filter", help="Only include modules matching this substring in the path."
    )
    parser.add_argument(
        "--validate-tests", action="store_true", help="Validate test coverage after generation."
    )
    args = parser.parse_args()

    config = ConfigManager.load_config()
    suggestions, prototype_code = suggest_new_modules(args.input, config, path_filter=args.filter)

    if args.to:
        Path(args.to).write_text(suggestions, encoding="utf-8")
        print(f"📄 Suggestions written to {args.to}")

    if args.prototype:
        proto_out = args.proto_dir or "prototypes"
        export_prototypes_to_files(prototype_code, output_dir=proto_out, is_test=False)

        if args.tests:
            test_out = args.test_dir or "prototypes_tests"
            test_code = generate_test_stubs(prototype_code, config)
            export_prototypes_to_files(test_code, output_dir=test_out, is_test=True)

            if args.validate_tests:
                untested = validate_test_coverage(proto_out, test_out)
                if untested:
                    print("⚠️ Missing tests for:", untested)
