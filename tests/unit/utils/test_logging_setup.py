from scripts.config import logging_setup
import logging


def test_logging_configuration_sets_root_logger():
    """
    Tests that the setup_logging function sets the root logger's level to DEBUG when specified.
    """
    logging_setup.setup_logging("DEBUG")
    assert logging.getLogger().getEffectiveLevel() == logging.DEBUG
