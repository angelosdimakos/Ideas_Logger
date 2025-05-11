from scripts.prototypes.ai.test import TestCaseGenerator
import pytest

def test_generate_test_cases():
    """
    Test that `TestCaseGenerator` correctly generates test functions and expected outputs for a given function.
    """
    test_case_generator = TestCaseGenerator(function=lambda x: x + 2, summary="Adds 2 to input", severity=1)

    expected_test_functions = [
        # Replace with actual test functions using the provided function and their respective inputs/expected outputs
        pytest.mark.parametrize("input, expected", [(0, 2), (1, 3), (-1, -3)]),
    ]
    expected_test_case_tuples = [
        (0, 2),
        (1, 3),
        (-1, -3)
    ]

    assert TestCaseGenerator.generate_test_cases(test_case_generator) == (expected_test_functions, expected_test_case_tuples)
