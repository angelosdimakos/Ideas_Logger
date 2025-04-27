# 🚀 Ideas Logger – CI-Tested AI-Augmented GUI for Structured Thought

[![codecov](https://codecov.io/gh/angelosdimakos/Ideas_Logger/graph/badge.svg?token=C49N6JTFXY)](https://codecov.io/gh/angelosdimakos/Ideas_Logger)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Codecov](https://codecov.io/gh/angelosdimakos/Ideas_Logger/graphs/sunburst.svg?token=C49N6JTFXY)](...)



> `python` • `tkinter` • `ollama` • `faiss` • `gui-app` • `llm` • `summarization` • `productivity`

A powerful, locally-run GUI tool for capturing, organizing, summarizing, and exporting your best ideas — all powered by local LLMs like **Ollama**, and rigorously tested via full-stack **CI/CD** pipelines.

🧠 Built for creative thinkers, engineers, and productivity junkies who want their ideas to **survive the chaos** and become **automatically structured**, **summarized**, and **searchable**.


---

## 🖥️ Features

✅ Cross-platform **Tkinter GUI**  
✅ **Local LLM summarization** using Ollama  
✅ **FAISS vector search** for semantic lookup  
✅ **Markdown export**, JSON logging, and autosave  
✅ Category + subcategory classification  
✅ Configurable AI prompts by category  
✅ Complete **CI/CD coverage with GitHub Actions**  
✅ Mocked AI backends for fast, reproducible tests  
✅ Strict "test mode" to prevent config or data overwrite  
✅ Plugin-ready architecture for future expansion (LangChain, mind maps, Gantt views)

---

## 💡 Why It’s Different

| Feature                     | Ideas Logger                           | Most Note-Takers            |
|----------------------------|-----------------------------------------|-----------------------------|
| ✅ Local LLM Summarization | Uses Ollama + fallback AI modes         | ❌ Requires OpenAI API keys |
| ✅ GUI Bootstrap Testing   | Tkinter startup tested in CI (mocked)   | ❌ Usually skipped entirely |
| ✅ FAISS Indexing          | Fast vector search with metadata        | ❌ No semantic search       |
| ✅ GitHub-Tested Workflows | Mocked LLMs, config isolation, and CI   | ❌ Unverified edge cases    |

---

## 🧪 Testing Highlights

This repo is **battle-tested** with:

- Full **mocking of Ollama**'s `generate()` and `chat()` endpoints  
- Integration tests for summarization + file I/O pipelines  
- `temp_dir` + isolated test config injection  
- ✅ **Tkinter GUI bootstrap tested in CI (mocked `run()`)**  
- ⚠️ **Full GUI rendering/interactions are skipped in headless CI**  
- 🧪 GUI tests are runnable locally (or with `xvfb` if needed)  
- Summary workflows and trackers are tested *without real LLM latency*
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

