# AI / Meta

## 2025-03-21
- **Tooling & Automation**: Embedded LLaMA3 to ensure summarisation every ten entries, on which I will include my corrected summary.
- **Execution Strategy**: Will need to carefully update database assistant will use in order to ensure safety and data integrity.
- **Execution Strategy**: Instead of migrating existing validated knowledge from the AI Assistant Database to the Ideas Logger, maintain the database as the structured, finalized knowledge base. Keep the Ideas Logger for rapid, spontaneous ideation and early-stage concepts. Only transition ideas from the Logger into the AI Assistant Database after they've been reviewed, refined, and validated. This ensures clear workflow separation, optimizes the ideation-to-execution pipeline, and preserves database integrity.
- **AI System Design**: Evaluated fine-tuning vs. RAG; chose RAG for faster context adaptation.
- **AI System Design**: Designed prompt templates optimized for efficient RAG summarization.
- **AI System Design**: Planned local Ollama inference pipeline to minimize external API dependency.
- **Tooling & Automation**: Will begin integrating RAG with FAISS in order to enable automated summarisation and tagging.
- **AI System Design**: Will need some initial entries for each subcategory, around 3, to ensure the model can use more context, and improve early accuracy.
- **AI System Design**: Will need approximately 100-200 entries for RAG to ensure high quality summaries with minimal corrections
- **AI System Design**: Will be using ChatGPT to ensure quality of ingested entries for RAG system is high.
- **AI System Design**: Logs need to be brief, but elaborate on key concepts to facilitate better RAG training.
- **Tooling & Automation**: Retrieval Augmented Generation through FAISS will enable automated summarisation to train LLM, to automate summarisation and tagging in the future.
- **Tooling & Automation**: Implemented modulirisation to seperate core logic from UI
- **Tooling & Automation**: Created logger for personal ideas across different domains.
- **Tooling & Automation**: Used nested hierarchy in JSON for faster injection
- **Tooling & Automation**: GPT 4.5 was able to modularise code
- **Tooling & Automation**: Modulirised code, created seperate classes

- **Tooling & Automation**: Claude is extremely efficient for proper software engineering.

- **AI System Design**: Chat GPT prefers destructive logic

## 2025-03-22
- **Meta Reflection**: Will try to inject 10 entries to validate summaries, but probably need Claude subscriptions for programming, and ChatGPT for strategising.

- **Meta Reflection**: Troubleshooting 4o after 4.5 performance is extremely demoralising.
