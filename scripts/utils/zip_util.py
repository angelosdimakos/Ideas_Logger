import argparse
from scripts.utils.file_utils import zip_python_files
import logging

logger = logging.getLogger(__name__)


def main():
    """
    Parses command-line arguments to zip all .py files in a project, excluding specified directories.
    Calls the internal utility to create the zip archive and logs the output path.
    """
    parser = argparse.ArgumentParser(
        description="Zip all .py files in a project (excluding .venv, .git, etc.)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        required=True,
        help="Path to output zip file (e.g., py_backup.zip)",
    )
    parser.add_argument(
        "--root",
        "-r",
        type=str,
        default=".",
        help="Root directory to start from (default: current directory)",
    )
    parser.add_argument(
        "--exclude",
        "-e",
        nargs="*",
        default=[".venv", ".git", "__pycache__", "node_modules"],
        help="Directories to exclude (default: .venv, .git, __pycache__, node_modules)",
    )

    args = parser.parse_args()
    zip_python_files(args.output, args.root, args.exclude)
    logger.info(f"✅ Zipped .py files into: {args.output}")


if __name__ == "__main__":
    main()
