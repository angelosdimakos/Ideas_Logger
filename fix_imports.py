#!/usr/bin/env python
"""
Fix import statements in the specific problematic test files.

This script directly applies the needed fixes to the four test files
that are failing in the pytest output.
"""

import os
from pathlib import Path


def fix_test_chat_refactor():
    """Fix imports in test_chat_refactor.py"""
    file_path = "tests/unit/ai/test_chat_refactor.py"

    replacements = [
        ("    with patch('chat_refactor.apply_persona'",
         "    with patch('scripts.ai.chat_refactor.apply_persona'")
    ]

    apply_replacements(file_path, replacements)


def fix_test_llm_router():
    """Fix imports in test_llm_router.py"""
    file_path = "tests/unit/ai/test_llm_router.py"

    replacements = [
        ("    with patch('llm_router.ConfigManager.load_config'",
         "    with patch('scripts.ai.llm_router.ConfigManager.load_config'")
    ]

    apply_replacements(file_path, replacements)


def fix_test_module_docstring_summarizer():
    """Fix imports in test_module_docstring_summarizer.py"""
    file_path = "tests/unit/ai/test_module_docstring_summarizer.py"

    replacements = [
        ("    with patch('module_docstring_summarizer.get_prompt_template',",
         "    with patch('scripts.ai.module_docstring_summarizer.get_prompt_template',"),
        ("    with patch('module_docstring_summarizer.apply_persona',",
         "    with patch('scripts.ai.module_docstring_summarizer.apply_persona',"),
        ("    with patch('module_docstring_summarizer.ConfigManager.load_config')",
         "    with patch('scripts.ai.module_docstring_summarizer.ConfigManager.load_config')"),
        ("    with patch('module_docstring_summarizer.AISummarizer')",
         "    with patch('scripts.ai.module_docstring_summarizer.AISummarizer')")
    ]

    apply_replacements(file_path, replacements)


def fix_test_refactor_advisor():
    """Fix imports in test_refactor_advisor.py"""
    file_path = "tests/unit/ai/test_refactor_advisor.py"

    replacements = [
        ("    with patch('llm_refactor_advisor.get_prompt_template',",
         "    with patch('scripts.ai.llm_refactor_advisor.get_prompt_template',"),
        ("    with patch('llm_refactor_advisor.apply_persona',",
         "    with patch('scripts.ai.llm_refactor_advisor.apply_persona',")
    ]

    apply_replacements(file_path, replacements)


def apply_replacements(file_path, replacements):
    """
    Apply specific replacements to a file.

    Args:
        file_path: Path to the file to modify
        replacements: List of (old_text, new_text) tuples
    """
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        content = None

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"Successfully read {file_path} with encoding {encoding}")
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            print(f"Error: Could not read {file_path} with any encoding")
            return

        # Apply replacements
        modified = False
        new_content = content

        for old_text, new_text in replacements:
            if old_text in new_content:
                new_content = new_content.replace(old_text, new_text)
                modified = True
                print(f"  Replaced: {old_text}")

        if modified:
            # Write the modified content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed {file_path}")
        else:
            print(f"No changes needed for {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")


def main():
    """Fix all problematic test files."""
    # Ensure we're in the project root
    project_root = Path.cwd()

    print("Fixing test files...")
    fix_test_chat_refactor()
    fix_test_llm_router()
    fix_test_module_docstring_summarizer()
    fix_test_refactor_advisor()

    print("\nDone!")


if __name__ == "__main__":
    main()