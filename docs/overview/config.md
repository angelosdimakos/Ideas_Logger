

# ⚙️ Configuration Guide (`config.json`)

ZephyrusLogger is fully driven by a centralized `config.json` file located at:

config/config.json


This file controls everything from runtime behavior to GUI layout, LLM selection, vector indexing paths, and developer flags.

---

## 🔑 Top-Level Keys

| Key                     | Type     | Description |
|------------------------|----------|-------------|
| `mode`                 | string   | `"test"` or `"full"` – controls whether full indexing & vector storage are enabled |
| `use_gui`              | boolean  | Toggle GUI on launch |
| `test_mode`            | boolean  | If true, redirects paths to mock/test-safe folders |
| `dev_mode`             | boolean  | Enables logging/debugging flags |
| `markdown_export`      | boolean  | If true, allows Markdown export of entries |

---

## 🤖 LLM Settings

| Key               | Description |
|------------------|-------------|
| `llm_provider`   | `"openai"`, `"huggingface"`, `"ollama"` |
| `llm_model`      | Model name (e.g. `"gpt-3.5-turbo"`, `"mistral"`) |
| `embedding_model`| SentenceTransformers model name (e.g. `"all-MiniLM-L6-v2"`) – fallback if not defined |

---

## 🧠 Categories & Prompts

| Section             | Description |
|---------------------|-------------|
| `category_structure`| Maps each major category (e.g. `Narrative`, `World`) to subcategories (e.g. `Plot`, `Magic`, `Faction`) |
| `prompts_by_subcategory` | Maps each subcategory to a summarization prompt – this powers the AI guidance in the GUI or CLI |

Example:
```json
{
  "category_structure": {
    "Narrative": ["Plot", "Themes"],
    "World": ["Factions", "Magic"]
  },
  "prompts_by_subcategory": {
    "Plot": "Summarize this plot point...",
    "Magic": "Describe how this magic system functions..."
  }
}

📦 Storage Paths
Key	Description
summary_data_path	Where to save/load structured summary entries
raw_log_path	Where raw input text is saved
faiss_index_path	Vector index file (*.faiss)
faiss_metadata_path	JSON metadata matching vectors to entries
tracker_path	Saves overall category coverage tracker (summary_tracker.json)
gui_state_path	Remembers last selected dropdowns, inputs, etc.
🧪 Mock/Test Overrides

If test_mode: true, these paths override real ones:
Key	Description
test_summary_data_path	Summary JSON for test runs
test_raw_log_path	Raw logs for test runs
test_faiss_index_path	Temp index file
test_faiss_metadata_path	Temp metadata file
test_tracker_path	Tracker state for test runs
🧼 Tips

    You can reload config.json on-the-fly via CLI/GUI triggers.

    If any key is missing, ZephyrusLogger will log a warning and use a default.

    Invalid paths will not crash the app, but will skip indexing unless caught.