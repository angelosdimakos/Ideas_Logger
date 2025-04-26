import json

# ✅ Correct absolute import based on project structure
from scripts.utils.link_summaries_to_raw_logs import inject_entries_into_summaries


def test_inject_entries_into_summaries(tmp_path, monkeypatch):
    """
    Tests the inject_entries_into_summaries function by creating temporary raw log and summary files,
    mocking configuration and path resolution, and verifying that the correct raw log entries are injected
    into the summary batches.
    """
    # Create fake raw logs
    raw_log = {
        "2024-01-01": {
            "Test": {
                "Flow": [
                    {"timestamp": "2024-01-01 10:00:00", "content": "entry A"},
                    {"timestamp": "2024-01-01 10:01:00", "content": "entry B"},
                ]
            }
        }
    }

    summaries = {"Test": {"Flow": [{"batch": "1-2"}]}}

    raw_path = tmp_path / "zephyrus_log.json"
    summaries_path = tmp_path / "correction_summaries.json"
    raw_path.write_text(json.dumps(raw_log), encoding="utf-8")
    summaries_path.write_text(json.dumps(summaries), encoding="utf-8")

    # Monkeypatch config resolution
    monkeypatch.setattr("scripts.utils.link_summaries_to_raw_logs.load_config", lambda: {})
    monkeypatch.setattr(
        "scripts.utils.link_summaries_to_raw_logs.get_absolute_path",
        lambda path: str(raw_path if "zephyrus_log" in path else summaries_path),
    )
    monkeypatch.setattr(
        "scripts.utils.link_summaries_to_raw_logs.get_config_value",
        lambda conf, key, default=None: str(raw_path if "raw_log" in key else summaries_path),
    )

    inject_entries_into_summaries()

    # Confirm entries injected
    updated = json.loads(summaries_path.read_text())
    assert updated["Test"]["Flow"][0]["entries"] == ["entry A", "entry B"]
