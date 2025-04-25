from unittest.mock import patch
import runpy

@patch("scripts.ci_analyzer.orchestrator.main")
def test_cli_delegates_to_orchestrator(mock_main):
    runpy.run_path("scripts/ci_analyzer/cli.py", run_name="__main__")
    mock_main.assert_called_once()
