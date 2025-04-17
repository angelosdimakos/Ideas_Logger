## 🚀 Ideas Logger – CI-Tested AI-Augmented GUI for Structured Thought

[![Run Tests](https://github.com/angelosdimakos/Ideas_Logger/actions/workflows/pytest.yml/badge.svg)](https://github.com/angelosdimakos/Ideas_Logger/actions/workflows/pytest.yml)
[![codecov](https://codecov.io/gh/angelosdimakos/Ideas_Logger/graph/badge.svg?token=C49N6JTFXY)](https://codecov.io/gh/angelosdimakos/Ideas_Logger)![Lint](https://img.shields.io/badge/lint-pass-brightgreen)
![Docs](https://img.shields.io/badge/doc--coverage-85%25-yellowgreen)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
> `python` • `tkinter` • `ollama` • `faiss` • `gui-app` • `llm` • `summarization` • `productivity`
A powerful, locally-run GUI tool for capturing, organizing, summarizing, and exporting your best ideas — all powered by local LLMs like **Ollama**, and rigorously tested via full-stack **CI/CD** pipelines.  

🧠 Built for creative thinkers, engineers, and productivity junkies who want their ideas to **survive the chaos** and get **automatically structured**, **summarized**, and **searchable**.

---

### 🖥️ Features

✅ **Tkinter GUI** (Cross-platform)  
✅ **Automatic Summarization** using local Ollama model  
✅ **FAISS Vector Search** for similarity lookups  
✅ **Markdown Export**, JSON logs, and batch autosave  
✅ **Category + Subcategory Classification**  
✅ **Configurable Prompts by Subcategory**  
✅ **Complete CI/CD Coverage with Pytest on GitHub Actions**  
✅ **Mocked Ollama AI for deterministic test coverage**  
✅ **Strict Test Mode** to prevent data leakage or config overwrite  
✅ **Plugin-ready architecture** for future expansion (e.g., LangChain agents, mind map UI, Gantt charts)

---

### 💡 Why It’s Different

| Feature                     | Ideas Logger                          | Most Note-Takers            |
|----------------------------|----------------------------------------|-----------------------------|
| ✅ Local LLM Summarization | Uses Ollama + fallback AI modes        | ❌ Requires OpenAI API keys |
| ✅ GUI CI Testing          | Tkinter elements tested in CI on push  | ❌ Usually skipped          |
| ✅ FAISS Indexing          | Fast vector search with metadata       | ❌ No semantic search       |
| ✅ GitHub-Tested Workflows | Mocked LLMs, config isolation, and CI  | ❌ Unverified edge cases    |

---

### 🧪 Testing Highlights

This repo is **battle-tested** with 🔬:

- Full **mocking of Ollama**'s `generate()` and `chat()` endpoints
- Integration tests for **summarization workflows**
- Isolated `temp_dir` + test config generation on the fly
- ✅ GUI testing (Tkinter) *in CI*
- `AISummarizer` is fully tested **without hitting real LLMs** — no latency, no cost, no flakes

```bash
pytest tests/ --disable-warnings -v
```

---

### 📁 Project Structure

```bash
scripts/
├── core/                # Log orchestration, trackers, and summary logic
├── ai/                  # AISummarizer wrapper around Ollama
├── gui/                 # Tkinter-based UI with logging integration
├── config/              # JSON loader, test mode, logging setup
├── indexers/            # FAISS-backed vector indexing
├── utils/               # File tools, guards, helpers
tests/
├── unit/                # Fine-grained component tests
├── integration/         # Full-stack AI workflow testing
├── mocks/               # Test utilities and patchable mocks
```

---

### 🧠 Ollama Integration (Mocked in CI!)

AI summarization is performed using:

```python
response = ollama.generate(model=self.model, prompt=your_prompt)
```

But during tests:

- Replaced with `MagicMock`
- Controlled return values
- Fully reproducible summaries

✅ This lets **all AI-dependent workflows** run on GitHub Actions **without actually invoking** the model.

---

### 📦 Install & Run

```bash
git clone https://github.com/The-Mechid-Archivist-69/Ideas_Logger.git
cd Ideas_Logger
pip install -r requirements.txt
python scripts/main.py
```

> ⚠ Requires [Ollama](https://ollama.com/) and a model like `mistral` running locally:
> ```
> ollama run mistral
> ```

---

### 🌍 Roadmap

- [x] Ollama integration (mocked for CI)
- [x] CI-tested GUI pipeline
- [x] Config override + temp test directories
- [x] Summary Tracker
- [x] Raw log ↔ Summary linking
- [ ] Gantt chart support
- [ ] Mind-map visual UI
- [ ] Plugin execution from GUI

---
### 📚 Full Documentation

Want the full breakdown?

- [Installation Guide](docs/install.md)
- [Configuration Reference](docs/config.md)
- [CLI / GUI Usage](docs/usage.md)
- [Testing & CI Workflows](docs/testing.md)
- [RefactorGuard & Dev Tools](docs/dev_tools.md)
- [Architecture Overview](docs/architecture.md)
- [Troubleshooting & FAQ](docs/troubleshooting.md)

> Prefer it in one scroll? See [📘 Full Docs (Single Page)](docs/README_Full.md)
---

### 🔒 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for full details.

> You're free to use, modify, and distribute — just keep attribution.

---



### 🧙‍♂️ Author’s Note

> _This isn’t just a logger. This is a spellbook for your mind._  
> _Built in madness. Tested in fire. Documented with love._

