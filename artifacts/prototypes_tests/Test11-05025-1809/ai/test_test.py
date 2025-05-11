from scripts.prototypes.ai.linting import Linter

def test_lint():
    """
    Test that `Linter` correctly identifies and records issues when performing lint checks.
    """
    linter = Linter({".py": ["rule1", "rule2"]})
    file_path = "test_file.py"

    # Replace with actual code violating the rules in the specified file
    Linter.lint(file_path)

    assert len(linter.issues) > 0

def test_suggest_linting_actions():
    """
    Test that `Linter` correctly suggests linting actions based on identified issues.
    """
    linter = Linter({".py": ["rule1", "rule2"]})
    # Replace with actual code violating the rules and their respective suggested fixes
    suggestions = [("rule1 violation", "Fix by adding this line: 'fix_rule1'"), ("rule2 violation", "Fix by adding this line: 'fix_rule2'")]

    assert Linter.suggest_linting_actions(linter) == suggestions
