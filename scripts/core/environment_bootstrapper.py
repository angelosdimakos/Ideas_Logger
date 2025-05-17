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
        Initializes the EnvironmentBootstrapper with paths and a default batch size.
        
        Args:
        	paths: Contains locations for logs, exports, and configuration files.
        	default_batch_size: Default batch size used if the configuration file is missing.
        """
        self.paths = paths  # Store the paths for later use
        self.default_batch_size = default_batch_size  # Set default batch size

    def bootstrap(self) -> None:
        """
        Prepares the application environment by ensuring required directories and files exist.
        
        Calls internal methods to create necessary directories and initialize essential files for the Zephyrus Logger application, guaranteeing all resources are ready before startup.
        """
        self._make_directories()  # Create necessary directories
        self._initialize_files()  # Initialize required files

    def _make_directories(self) -> None:
        """
        Creates required directories for logs, exports, and configuration files if they do not exist.
        """
        self.paths.log_dir.mkdir(parents=True, exist_ok=True)  # Create log directory
        self.paths.export_dir.mkdir(parents=True, exist_ok=True)  # Create export directory
        self.paths.config_file.parent.mkdir(parents=True, exist_ok=True)  # Create config directory

    def _initialize_files(self) -> None:
        """
        Initializes required log and configuration files for the Zephyrus Logger environment.
        
        Creates empty or default-initialized files if they do not exist, including the JSON log, text log, correction summaries, and configuration files. If the correction summaries file exists but is empty, it is reinitialized as an empty JSON file. The configuration file is recreated with a default batch size if missing.
        """
        if not self.paths.json_log_file.exists():  # Check if log file exists
            logger.info("Creating empty log file: %s", self.paths.json_log_file)
            write_json(self.paths.json_log_file, {})  # Create empty log file

        if not self.paths.txt_log_file.exists():  # Check if text log file exists
            self.paths.txt_log_file.write_text(
                "=== Zephyrus Idea Logger ===\n", encoding="utf-8"
            )  # Create text log file

        if (
            not self.paths.correction_summaries_file.exists()
        ):  # Check if correction summaries file exists
            logger.info(
                "Creating correction summaries file: %s", self.paths.correction_summaries_file
            )
            write_json(self.paths.correction_summaries_file, {})  # Create correction summaries file
        elif (
            self.paths.correction_summaries_file.stat().st_size == 0
        ):  # Check if correction summaries file is empty
            logger.warning("Correction summaries file is empty. Initializing to empty JSON.")
            write_json(
                self.paths.correction_summaries_file, {}
            )  # Initialize correction summaries file

        if not self.paths.config_file.exists():  # Check if config file exists
            logger.warning("Missing config file. Recreating with default batch size.")
            write_json(
                self.paths.config_file, {"batch_size": self.default_batch_size}
            )  # Recreate config file
