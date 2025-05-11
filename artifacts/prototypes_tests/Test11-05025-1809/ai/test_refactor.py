from scripts.prototypes.ai.documentation import Documenter


def test_generate_documentation():
    """
    Test that `Documenter` generates comprehensive documentation for specified code elements.
    """
    documenter = Documenter(modules=["module1", "module2"], functions=["function1", "function2"], classes=["class1"])
    expected_docs = {
        # Replace with actual expected dictionary structure and content
        ("module1", ): "Documentation for module1.",
        ("module2", ): "Documentation for module2.",
        ("function1",): "Documentation for function1.",
        ("function2",): "Documentation for function2.",
        ("class1",): "Documentation for class1."
    }

    assert Documenter.generate_documentation(documenter) == expected_docs
