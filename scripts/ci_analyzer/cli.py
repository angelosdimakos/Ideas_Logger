# ci_analyzer/cli.py
import os
import sys

# Ensure repo root is in sys.path (so we can import scripts.*)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from orchestrator import main

if __name__ == "__main__":
    main()
