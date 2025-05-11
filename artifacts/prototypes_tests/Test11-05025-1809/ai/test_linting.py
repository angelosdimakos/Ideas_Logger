from scripts.prototypes.ai.refactor import RefactoringSuggestions


def test_generate_refactor_suggestions():
    """
    Test that `RefactoringSuggestions` correctly generates refactoring suggestions for top offenders.
    """
    refactoring = RefactoringSuggestions(top_offenders=["function1", "function2"], issues={"function1": ["issue1", "issue2"], "function2": ["issue3"]})
    expected_suggestions = {
        # Replace with actual suggested refactoring actions for each function
        "function1": ["refactor action 1", "refactor action 2"],
        "function2": ["refactor action 1", "refactor action 2"]
    }

    assert RefactoringSuggestions.generate_refactor_suggestions(refactoring) == expected_suggestions
