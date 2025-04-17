from scripts.config import logging_setup
import logging

def test_logging_configuration_sets_root_logger():
    logging_setup.setup_logging("DEBUG")
    assert logging.getLogger().getEffectiveLevel() == logging.DEBUG
