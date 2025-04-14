# ZephyrusLogger

ZephyrusLogger is a robust, modular logging and summarization framework designed for developers, designers, and writers working with iterative ideas, creative systems, or AI-driven workflows.

It combines the power of LLMs, semantic indexing (via FAISS), and user-friendly interfaces to help you track, analyze, and reflect on evolving concepts over time.

---

## ✨ Core Features

- 🧠 **AI Summarization**: Automatically distill raw ideas into structured summaries based on subcategories you define.
- 🔍 **Searchable Vector Index**: Store and retrieve summaries using semantic similarity via FAISS.
- 📊 **Coverage Tracking**: View real-time coverage stats across creative or technical categories.
- 🖥️ **Dual Interface**: Use the CLI for automation or launch a GUI for interactive logging and inspection.
- 🧪 **RefactorGuard**: Analyze Python code refactors with method diffs, complexity scoring, and test coverage checks.
- 🧰 **Developer Utilities**: Built-in tools for zipping, auditing, and maintaining high-code-quality standards.

---

## 📌 Use Cases

- Creative writing or game design logs with narrative + worldbuilding structure
- Technical notes or R&D experiments organized by functional areas
- Long-term AI system tracking with category-level reflection prompts
- Internal tooling for auditing and summarizing refactor progress

---

## 🔧 Tech Stack

- Python 3.11+
- PyQt5 (GUI)
- FAISS (vector similarity search)
- sentence-transformers (`all-MiniLM-L6-v2` by default)
- Optional: HuggingFace, OpenAI, Ollama

---

## 💡 Philosophy

ZephyrusLogger was built for power-users who want to *reason about their thinking*. It offers flexible logging with structured meaning, while remaining light enough for rapid prototyping and iteration.

Think of it as a **semantic journal**, backed by LLMs and embeddable search.

---

## 🔗 Next Steps

- [Installation Guide](install.md)
- [Configuration Reference](config.md)
- [Using the GUI or CLI](usage.md)
- [Testing & Coverage](testing.md)
