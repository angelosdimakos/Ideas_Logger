"""
Environment Bootstrapper Module
===============================
This module provides the EnvironmentBootstrapper class, which is responsible 
for setting up the necessary directories and files for the Zephyrus Logger 
application. It ensures that all required resources are in place before 
the application starts.
"""

import logging
from scripts.utils.file_utils import write_json
from scripts.paths import ZephyrusPaths  # Import ZephyrusPaths

logger = logging.getLogger(__name__)

class EnvironmentBootstrapper:
    """
    A class to bootstrap the environment for the Zephyrus Logger application.

    This class handles the creation of necessary directories and files, 
    ensuring that the application has all required resources available.

    Attributes:
        paths (ZephyrusPaths): An instance containing paths for logs, exports, 
                                and configuration files.
        default_batch_size (int): The default batch size to use if the 
                                   configuration file is missing.
    """

    def __init__(self, paths: ZephyrusPaths, default_batch_size: int = 5) -> None:
        """
        Initialize the EnvironmentBootstrapper.

        Parameters:
            paths (ZephyrusPaths): The paths object containing locations for 
                                    logs, exports, and configuration.
            default_batch_size (int): The default batch size for processing 
                                       entries. Defaults to 5.
        """
        self.paths = paths  # Store the paths for later use
        self.default_batch_size = default_batch_size  # Set default batch size

    def bootstrap(self) -> None:
        """
        Bootstrap the environment by creating necessary directories and 
        initializing required files.
        """
        self._make_directories()  # Create necessary directories
        self._initialize_files()  # Initialize required files

    def _make_directories(self) -> None:
        """
        Create necessary directories for logs and exports.
        """
        self.paths.log_dir.mkdir(parents=True, exist_ok=True)  # Create log directory
        self.paths.export_dir.mkdir(parents=True, exist_ok=True)  # Create export directory
        self.paths.config_file.parent.mkdir(parents=True, exist_ok=True)  # Create config directory

    def _initialize_files(self) -> None:
        """
        Initialize log and configuration files. Creates empty files if they 
        do not exist and sets up default values where necessary.
        """
        if not self.paths.json_log_file.exists():  # Check if log file exists
            logger.info("Creating empty log file: %s", self.paths.json_log_file)
            write_json(self.paths.json_log_file, {})  # Create empty log file

        if not self.paths.txt_log_file.exists():  # Check if text log file exists
            self.paths.txt_log_file.write_text("=== Zephyrus Idea Logger ===\n", encoding="utf-8")  # Create text log file

        if not self.paths.correction_summaries_file.exists():  # Check if correction summaries file exists
            logger.info("Creating correction summaries file: %s", self.paths.correction_summaries_file)
            write_json(self.paths.correction_summaries_file, {})  # Create correction summaries file
        elif self.paths.correction_summaries_file.stat().st_size == 0:  # Check if correction summaries file is empty
            logger.warning("Correction summaries file is empty. Initializing to empty JSON.")
            write_json(self.paths.correction_summaries_file, {})  # Initialize correction summaries file

        if not self.paths.config_file.exists():  # Check if config file exists
            logger.warning("Missing config file. Recreating with default batch size.")
            write_json(self.paths.config_file, {"batch_size": self.default_batch_size})  # Recreate config file
