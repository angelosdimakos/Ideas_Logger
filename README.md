Zephyrus Idea Logger 🧠📝

Zephyrus Idea Logger is a personal idea-capturing tool designed for worldbuilding, AI design, and narrative development. It combines an intuitive GUI for logging ideas, automated AI-driven summarization, and fast semantic search using FAISS. With Obsidian-ready markdown exports and a structured JSON log, it’s built for creative workflows and rapid retrieval.
🔧 Features

    GUI Logger: Easy-to-use interface with category dropdowns for logging ideas.

    Automated Summarization: Uses local AI (via Ollama) to generate summaries from logged ideas.

    FAISS Integration: Builds a vector index from summaries (using cosine similarity) for fast semantic search.

    Obsidian-Ready Exports: Generates markdown logs in /exports/ for seamless integration with Obsidian.

    Structured JSON Logging: Timestamps and organizes ideas for easy tracking and future processing.

    Extensible Architecture: Designed to incorporate additional features like bidirectional linking, custom tagging, and more.

📁 Project Structure

Zephyrus_Idea_Logger/
├── main.py                     # Entry point for launching the application
├── core.py                     # Core logging and summarization logic
├── gui.py                      # Tkinter-based GUI for logging and FAISS search
├── ai_summarizer.py            # AI summarization using local Ollama inference
├── summary_indexer.py          # FAISS indexer for semantic search (with cosine similarity)
├── vector_indexer.py           # Alternate indexer implementation (if needed)
├── logs/                       # JSON logs, correction summaries, and error logs
├── exports/                    # Obsidian-compatible markdown logs
├── config.json                 # Configuration file (e.g., batch size, etc.)
└── README.md                   # This file

🚀 Roadmap & Future Upgrades

While the project is feature complete for core idea logging, summarization, and vector search, the roadmap below outlines several enhancements to further boost productivity and extend functionality:
Phase 1: Documentation & Core Polish (Weeks 1–2)

    Improve README and developer guides.

    Refactor code and add tests for core features.

Phase 2: Productivity Enhancements (Weeks 3–5)

    Obsidian-Style Features:

        Introduce [[double-bracket]] linking and automatic network graph generation.

        Create daily notes and predefined templates for various idea types.

Phase 3: Structured Data & UI Enhancements (Weeks 6–8)

    Notion-Inspired Organization:

        Add structured metadata (e.g., Priority, Status) to entries.

        Implement filtering, sorting, and a Kanban view in the GUI.

Phase 4: Workflow & Task Management (Weeks 9–11)

    Trello-Like Features:

        Introduce simple status tracking (To-Do, In Review, Completed).

        Set deadlines and reminders for revisiting critical ideas.

Phase 5: Advanced AI Integration (Weeks 12–14)

    Enhanced AI Capabilities:

        Improve real-time summarization and schedule periodic reports.

        Implement AI-driven tagging to suggest and auto-assign relevant keywords.

Phase 6: Extensibility & Analytics (Weeks 15–18)

    Extensible Architecture:

        Develop a plugin system and customizable keyboard shortcuts.

        Integrate version history for entries and remote syncing.

        Add visual analytics (e.g., word clouds, heatmaps) for trend analysis.

🛠️ Installation & Setup

    Clone the repository:

git clone https://your-repo-url.git
cd Zephyrus_Idea_Logger

Install dependencies:

pip install -r requirements.txt

Ensure you have installed packages such as ollama, faiss, sentence_transformers, and tkinter.

Run the application:

    python main.py

🔍 Usage

    Logging Ideas:
    Input your ideas using the GUI. Entries are automatically logged, summarized in batches, and exported as markdown files.

    FAISS Search:
    Build or refresh the FAISS index and use the search panel to quickly find summaries using semantic search.

    Markdown Exports:
    Check the /exports/ directory for organized, Obsidian-ready markdown files.

🤝 Contributing

Contributions are welcome! Fork the repository, create a feature branch, and open a pull request with your improvements. Please update documentation and tests as appropriate.
📄 License

MIT License
📚 Acknowledgments

This project draws inspiration from leading productivity tools such as Obsidian, Notion, Trello, and VSCode, combined with modern AI summarization and vector search techniques.