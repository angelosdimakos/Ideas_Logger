# Zephyrus Idea Logger ✨

The **Zephyrus Idea Logger** is a modular, AI-powered idea capture and summarization system designed for researchers, writers, and creative thinkers. It allows you to log, structure, and summarize bursts of inspiration across categories using a fully local pipeline powered by **Ollama**, **FAISS**, and custom AI models like **Mistral** or **LLaMA3**.

---

## 🚀 Features

| Capability                    | Description                                                                 |
|------------------------------|-----------------------------------------------------------------------------|
| ✅ **Structured Idea Logging** | Logs ideas into nested JSON and Markdown by date, category, subcategory     |
| 🧠 **AI Summarization**     | Batch-based summarization using local LLMs via **Ollama** (default: Mistral) |
| 📉 **Correction Layer**       | Editable summaries with versioning and correction tracking                  |
| 🔗 **FAISS Indexing**         | Vector search of summaries for semantic recall                             |
| 🌐 **Markdown Export**         | Clean human-readable logs for future RAG workflows or creative use         |
| 🔍 **Summary Search**         | GUI-integrated vector-based search with real-time metadata filters         |
| 🚧 **Fully Local**             | No cloud dependencies, everything runs offline with `ollama`, `pytest`, etc |

---

## 🌐 Use Cases
- Research and PhD note summarization
- Story/plot outlining for writers
- Worldbuilding and visual prompt generation
- Multimodal content planning (Markdown + Images + JSON)
- AI training data preparation

---

## 💡 Philosophy
> *Don't just capture ideas. Understand them.*

This tool isn't a dump for raw thoughts. It's a **processing pipeline**. Every log entry flows through:
1. **Timestamped Logging**
2. **Batch Summarization**
3. **Manual Correction** (for AI reliability)
4. **Semantic Searchability**
5. **Long-Term Export** (Markdown or structured JSON)

---

## 🛠️ Installation
### 1. Install [Ollama](https://ollama.com)
```bash
# Windows/Mac/Linux
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull Mistral or another model
```bash
ollama pull mistral
```

### 3. Clone & Setup
```bash
git clone https://github.com/The-Mechid-Archivist-69/zephyrus-logger.git
cd zephyrus-logger
python -m venv .venv
source .venv/bin/activate  # Or `.venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

---

## 💡 How It Works

### File Structure
```
zephyrus-logger/
├── scripts/
│   ├── ai_summarizer.py        # Handles prompt-based LLM summarization
│   ├── base_indexer.py         # FAISS + metadata indexing
│   ├── config_loader.py        # Configuration and environment utilities
│   ├── summary_indexer.py      # Summary-specific indexing/search
│   └── core.py                 # Main ZephyrusLoggerCore logic
│
├── utils/
│   ├── file_utils.py           # JSON/Markdown file helpers
│   └── zip_util.py             # CLI: Zip .py files excluding virtualenvs, etc
│
├── logs/                       # Auto-created logs & error reports
├── exports/                    # Markdown output by category
├── config/config.json          # Model & prompt configurations
├── correction_summaries.json  # Human-editable corrections
├── zephyrus_log.json          # Core log file
└── README.md                   # This file
```

---

## 🔎 AI Summary Lifecycle
1. **Entries** are logged per subcategory in `zephyrus_log.json`.
2. When a batch of 5 is reached (default), `AISummarizer` triggers.
3. Summary is generated using **`generate()`** or fallback to **`chat()`**.
4. Result is stored in `correction_summaries.json` with:
   - `original_summary`
   - `corrected_summary` (optional)
   - `batch range` + `timestamp`
5. All logs are also exported to **Markdown** by category.

---

## 📄 Example Entry
```json
{
  "2025-03-23": {
    "Creative": {
      "Visual or Audio Prompt": [
        { "timestamp": "2025-03-23 10:00:00", "content": "Use AI to generate concept art for Mechids." },
        { "timestamp": "2025-03-23 10:02:00", "content": "Integrate Reaper audio notes with image metadata." }
      ]
    }
  }
}
```
---

## 💧 Testing

```bash
pytest tests/
```

All core modules (logger, summarizer, utils, vector indexer, GUI helpers) have **unit tests with mocks**. Even FAISS is covered.

---

## 🎓 Future Roadmap
- [ ] Visual tagging in Markdown for AI-generated image triggers
- [ ] Full image pipeline CLI (e.g., auto-send prompts to SDXL)
- [ ] CLI interface for search + correction
- [ ] Scheduled backups + git snapshots

---

## 🌊 Credits
Built with:
- [Ollama](https://ollama.com) for blazing-fast LLM inference
- [FAISS](https://github.com/facebookresearch/faiss) for vector search
- [Tkinter](https://docs.python.org/3/library/tkinter.html) for GUI support
- [pytest](https://docs.pytest.org/) for thorough testing

Crafted by a slightly caffeinated architect with a taste for structured chaos.

---

## 🌟 Final Thoughts
> *You don’t need more ideas. You need better processing.*

Welcome to Zephyrus. Let the ideas flow. 🌬️

[![Run Tests (Windows Only)](https://github.com/The-Mechid-Archivist-69/Ideas_Logger/actions/workflows/pytest.yml/badge.svg)](https://github.com/The-Mechid-Archivist-69/Ideas_Logger/actions/workflows/pytest.yml)
