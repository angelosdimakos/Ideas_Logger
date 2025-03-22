import json
from pathlib import Path
from config_loader import load_config, get_config_value, get_absolute_path
from datetime import datetime

def inject_entries_into_summaries():
    config = load_config()
    
    log_path = get_absolute_path(get_config_value(config, "json_log_file", "logs/zephyrus_log.json"))
    summary_path = get_absolute_path(get_config_value(config, "correction_summaries_path", "logs/correction_summaries.json"))

    # Load raw logs and summaries
    with open(log_path, "r", encoding="utf-8") as f:
        raw_logs = json.load(f)

    with open(summary_path, "r", encoding="utf-8") as f:
        correction_summaries = json.load(f)

    updated_count = 0

    # Iterate summaries and inject actual entries
    for date, main_cats in correction_summaries.items():
        for main_cat, subcats in main_cats.items():
            for subcat, batches in subcats.items():
                for batch in batches:
                    entry_ids = batch.get("entry_ids", [])
                    entries_to_inject = []

                    for entry_id in entry_ids:
                        try:
                            parts = entry_id.split("_")
                            entry_date = f"{parts[1][:4]}-{parts[1][4:6]}-{parts[1][6:]}"
                            index = int(parts[2]) - 1
                            entry_content = raw_logs[entry_date][main_cat][subcat][index]
                            entries_to_inject.append(entry_content)
                        except Exception as e:
                            print(f"[⚠️ Warning] Could not inject entry '{entry_id}': {e}")

                    batch["entries"] = entries_to_inject
                    updated_count += 1

    # Save updated summaries
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(correction_summaries, f, indent=2, ensure_ascii=False)

    print(f"[✅] Injected raw entries into {updated_count} batches in correction_summaries.")
