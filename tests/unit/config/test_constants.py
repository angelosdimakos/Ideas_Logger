def test_constants_importable():
    """
    Tests that the constants module can be imported and that TIMESTAMP_FORMAT has the expected value.
    """
    import scripts.config.constants as c

    assert c.TIMESTAMP_FORMAT == "%Y-%m-%d %H:%M:%S"
