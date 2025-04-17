def test_constants_importable():
    import scripts.config.constants as c
    assert c.TIMESTAMP_FORMAT == "%Y-%m-%d %H:%M:%S"
