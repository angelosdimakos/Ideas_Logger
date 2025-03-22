# Zephyrus Idea Logger 🧠📝

A powerful, AI-integrated idea capture and summarization tool designed for:
- Narrative design
- Worldbuilding
- AI system architecture
- Research logging

Zephyrus combines a streamlined GUI, automated local LLM summarization, and lightning-fast semantic search via FAISS.

---

## ✨ Features

- ⬜ **Clean GUI:** Log structured entries using dropdowns for category/subcategory.
- 🤖 **AI Summarization:** Automatically summarizes every 5 entries per subcategory (via local Ollama).
- ⚖️ **Correction System:** Lets you manually revise summaries, with both `original_summary` and `corrected_summary` saved.
- 🔎 **FAISS Vector Search:** Search your summaries semantically using cosine similarity.
- 📅 **Time-Aware Batching:** Entries are grouped per date and subcategory, each with metadata.
- 📃 **Obsidian-Ready:** Markdown export enabled for seamless PKM workflows.

---

## ⚡ Quickstart

```bash
# 1. Clone the repo
$ git clone https://github.com/YOUR_USERNAME/zephyrus-idea-logger.git
$ cd zephyrus-idea-logger

# 2. Create virtual env & install dependencies
$ python -m venv venv && source venv/bin/activate
$ pip install -r requirements.txt

# 3. Launch the GUI
$ python scripts/main.py
```

---

## 🎓 How It Works

### Logging
- Choose a main category and subcategory
- Type your idea and save
- Every 5 entries: AI generates a summary, saved to `correction_summaries.json`

### Summarization
- Uses `llama3` or your configured Ollama model
- Summaries stored alongside original entries
- Manual corrections are versioned and stored as `corrected_summary`

### Search
- FAISS indexes all summaries
- You can rebuild the index and search via GUI
- Supports batch + metadata display for fast context

### Double Linking
- Each summary knows which log entries it came from
- Entries can be traced back via their `log_YYYYMMDD_###` ID

---

## 📂 Folder Structure

```
.
├── scripts/
│   ├── main.py                # Entry point
│   ├── gui.py                 # Full Tkinter GUI
│   ├── core.py                # Handles saving logs + summaries
│   ├── ai_summarizer.py      # Local LLM-based summarizer
│   ├── summary_indexer.py    # FAISS summary search logic
│   ├── raw_log_indexer.py    # FAISS indexing for raw log content
│   ├── base_indexer.py       # Shared FAISS logic
│   ├── config_loader.py      # Handles config.json loading
├── logs/
│   ├── zephyrus_log.json     # Main idea log
│   └── correction_summaries.json  # Summary metadata
├── exports/                      # Obsidian-compatible .md output
├── vector_store/                # FAISS index and metadata
├── config.json                  # All app configuration
```

---

## 🚀 Configuration

All behavior is controlled via `config.json`:

```json
"summarization": true,
"llm_model": "llama3",
"batch_size": 5,
"correction_summaries_path": "logs/correction_summaries.json",
"json_log_file": "logs/zephyrus_log.json"
```

> ⚠️ You must have **Ollama** installed and the selected model available locally.

---

## 📝 Testing

```bash
# Coming soon - tests for:
# - Summarization logic
# - FAISS index build/search
# - Data structure validation
```

---

## ✨ Roadmap

- [x] GUI Logger w/ Dropdowns
- [x] AI Summarization via Ollama
- [x] FAISS Vector Search (Summaries)
- [x] Correction + Double Link Tracking
- [ ] Raw Log Vector Search
- [ ] Plugin Support (Obsidian + Exports)
- [ ] Automated Testing & CLI

---

## 🙌 Contributing

Pull requests, ideas, and feature suggestions welcome!
- Fork + PR
- Raise an issue
- Or DM me if you want to collaborate deeper!

---

## 📄 License

MIT License. Use it freely, but don't resell without giving credit.

---

Built with ❤️ by Angelos Dimakos and his sentient AI archivist.

