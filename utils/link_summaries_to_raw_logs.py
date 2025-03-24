import json
from pathlib import Path
from scripts.config_loader import load_config, get_config_value, get_absolute_path
from datetime import datetime


def flatten_raw_entries(raw_logs, main_cat, subcat):
    """
    Flatten raw log entries for a given main category and subcategory across all dates,
    sorted chronologically.

    Args:
        raw_logs (dict): Raw logs as loaded from zephyrus_log.json.
        main_cat (str): The main category.
        subcat (str): The subcategory.

    Returns:
        list: A list of entries (each is a dict) for the given category/subcategory in chronological order.
    """
    entries = []
    # Sort dates to get chronological order.
    for date in sorted(raw_logs.keys()):
        day_logs = raw_logs.get(date, {})
        if main_cat in day_logs:
            cat_logs = day_logs[main_cat]
            if subcat in cat_logs:
                # Append all entries from this day.
                entries.extend(cat_logs[subcat])
    return entries


def inject_entries_into_summaries():
    """
    Inject the raw entry contents into each summary batch by using the batch label (global index range)
    to select the corresponding entries from the flattened raw logs.
    """
    config = load_config()

    # Adjust these keys if needed based on your updated config.
    log_path = get_absolute_path(get_config_value(config, "raw_log_path", "logs/zephyrus_log.json"))
    summary_path = get_absolute_path(
        get_config_value(config, "correction_summaries_path", "logs/correction_summaries.json"))

    # Load raw logs and summaries.
    with open(log_path, "r", encoding="utf-8") as f:
        raw_logs = json.load(f)

    with open(summary_path, "r", encoding="utf-8") as f:
        correction_summaries = json.load(f)

    updated_count = 0

    # Iterate over categories and subcategories in the summaries.
    # Note: Under the global approach, the summaries are no longer nested by date.
    for main_cat, subcats in correction_summaries.items():
        for subcat, batches in subcats.items():
            # Flatten all raw entries for this category/subcategory in chronological order.
            flat_entries = flatten_raw_entries(raw_logs, main_cat, subcat)
            if not flat_entries:
                print(f"[⚠️ Warning] No raw entries found for {main_cat} → {subcat}")
                continue

            for batch in batches:
                batch_label = batch.get("batch", "")
                if not batch_label or "-" not in batch_label:
                    print(f"[⚠️ Warning] Skipping batch with invalid label: {batch_label}")
                    continue
                try:
                    start_str, end_str = batch_label.split("-")
                    start_idx = int(start_str)
                    end_idx = int(end_str)
                except Exception as e:
                    print(f"[⚠️ Warning] Could not parse batch label '{batch_label}': {e}")
                    continue

                # Adjust for zero-based indexing.
                selected_entries = flat_entries[start_idx - 1: end_idx]
                # Extract the "content" field from each entry.
                entries_to_inject = [entry.get("content", "") for entry in selected_entries if "content" in entry]
                batch["entries"] = entries_to_inject
                updated_count += 1

    # Save updated summaries back to file.
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(correction_summaries, f, indent=2, ensure_ascii=False)

    print(f"[✅] Injected raw entries into {updated_count} batches in correction_summaries.")


if __name__ == "__main__":
    inject_entries_into_summaries()
