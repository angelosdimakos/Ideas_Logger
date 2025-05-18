# 🛠 Installation Guide

This guide walks you through setting up ZephyrusLogger in a local development or production environment.

---

## ✅ Requirements

- Python **3.11.x** (avoid 3.11.9 on Windows if using GUI — known tkinter issue)
- pip >= 21.0
- OS: Windows, macOS, Linux (tested on Windows + Ubuntu)

---

## 📦 1. Clone the Repo

```bash
git clone https://github.com/your-org/zephyrus-logger.git
cd zephyrus-logger

🐍 2. Set Up a Virtual Environment

python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

📦 3. Install Dependencies

python -m pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

    💡 For Windows + FAISS, install with:

pip install faiss-cpu --only-binary=faiss-cpu

💾 4. Optional: GPU Support (FAISS)

FAISS GPU isn't required, but if needed:

pip install faiss-gpu  # ⚠️ may require CUDA & compilation support

🧠 5. Optional: LLM Support

ZephyrusLogger supports multiple backends:

    OpenAI → Requires OPENAI_API_KEY or key in config.json

    Ollama → Local model serving, e.g., Mistral

Install dependencies for LLMs:

pip install openai sentence-transformers

🧪 6. Verify Installation

Run the canary test:

pytest tests/test_canary.py

Then launch the app:

python scripts/main.py

🧪 Troubleshooting
Problem	Solution
ModuleNotFoundError: scripts	Set PYTHONPATH=. or inject sys.path manually
FAISS file write error	Ensure vector_store/ directory exists
GUI fails to load	Check use_gui: true in config.json and tkinter installed