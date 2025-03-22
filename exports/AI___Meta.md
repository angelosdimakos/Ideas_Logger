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
- **AI System Design**: Included configurations in a global config.json file to enable better configuration with different templates depending on use.
- **Meta Reflection**: Using a script folder enables easier organisation of programmatic logic, but proper pathing is crucial to write to correct folders.
- **Tooling & Automation**: Automating category and subcategory selection based on entry would enable smoother usage, instead of dropdown categories.
- **Tooling & Automation**: Integration with Obsidian would enable easier construction of mindmaps.
- **Tooling & Automation**: Idea logger can be used for weaker machines, if summarisation is disabled. An exe file can be created for portability.
- **AI System Design**: Different LLMs can be used depending on user's available computational power (OpenAI for internet access with weaker rigs, and local LLMs for power users).
- **AI System Design**: Tighter command line integration is crucial, as GUI development is excellent for debugging, but not overall automation.
- **Tooling & Automation**: Structured hierarchy is essential for json files to enable faster lookup, with different subcategories.
- **Tooling & Automation**: Different config.json can be developed based on context use for idea logger (writing, lab use, development, etc.)
- **Tooling & Automation**: A prompt database will be created for easier lookup and future injection into local LLMs.
- **Tooling & Automation**: A python script will be used to automatically select settings, positive and negative prompts and output directory
- **Tooling & Automation**: I will shift from Automatic1111 to a programmatic apporach to invoke image generation from command line interface.
- **Tooling & Automation**: An important limitation I need to test is that if 5 entries are not created in a single session, this might lead to unsummarised entries.
- **Tooling & Automation**: Images can be programmatically generated, instead of relying on the webpage, which is currently under development.
- **Meta Reflection**: Will try to inject 10 entries to validate summaries, but probably need Claude subscriptions for programming, and ChatGPT for strategising.

- **Meta Reflection**: Troubleshooting 4o after 4.5 performance is extremely demoralising.
