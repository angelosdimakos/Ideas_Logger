"""
Markdown Logger Module
===============================
This module provides the MarkdownLogger class, which is responsible
for logging entries to Markdown files. It handles the creation and
updating of Markdown files in the specified export directory.
"""

from pathlib import Path
import re
import logging
from scripts.utils.file_utils import sanitize_filename

logger = logging.getLogger(__name__)


class MarkdownLogger:
    """
    A class to log entries to Markdown files.

    This class manages the logging of entries into Markdown format,
    creating new files or updating existing ones as necessary.

    Attributes:
        export_dir (Path): The directory where Markdown files will be saved.
    """

    def __init__(self, export_dir: Path) -> None:
        """
        Initialize the MarkdownLogger.

        Parameters:
            export_dir (Path): The directory where Markdown files will be saved.
        """
        self.export_dir = export_dir

    def log(self, date_str: str, main_category: str, subcategory: str, entry: str) -> bool:
        """
        Log an entry to a Markdown file.

        Parameters:
            date_str (str): The date string to be used as a header.
            main_category (str): The main category for the log entry.
            subcategory (str): The subcategory for the log entry.
            entry (str): The content of the log entry.

        Returns:
            bool: True if logging was successful, False otherwise.
        """
        try:
            md_filename = sanitize_filename(main_category) + ".md"
            md_path = self.export_dir / md_filename
            date_header = f"## {date_str}"
            md_content = f"- **{subcategory}**: {entry}\n"

            if md_path.exists():
                content = md_path.read_text(encoding="utf-8")
                if date_header in content:
                    updated = re.sub(f"({date_header}\n)", f"\1{md_content}", content, count=1)
                else:
                    updated = f"{content}\n{date_header}\n\n{md_content}"
            else:
                updated = f"# {main_category}\n\n{date_header}\n\n{md_content}"

            md_path.write_text(updated, encoding="utf-8")
            return True

        except Exception as e:
            logger.error("Markdown log failed: %s", e, exc_info=True)
            return False
