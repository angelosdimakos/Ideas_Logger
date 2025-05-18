🧠 Zephyrus LLM-Powered CI Advisors
📦 Tools Overview
1. llm_refactor_advisor.py

Analyzes your merged_report.json and generates a prioritized list of files most in need of refactor, based on metrics like MyPy errors, lint issues, complexity, and coverage.
LLM Role: Summarizes this analysis with a concise recommendation on what to refactor first and why.

Invocation:

python scripts/ai/llm_refactor_advisor.py merged_report.json

2. chat_refactor.py

Interactive CLI tool that answers dev questions like “What should I fix first?” using the context from the merged report.
LLM Role: Constructs contextual prompts with severity data and responds to your questions with actionable advice.

Invocation:

python scripts/ai/chat_refactor.py merged_report.json

3. module_docstring_summarizer.py

Generates concise summaries of module-level functionality by synthesizing function docstrings.
LLM Role: Reads per-function descriptions and creates one-paragraph summaries for each file.

Invocation:

python scripts/ai/module_docstring_summarizer.py merged_report.json

🔧 How it Works

    Prompts are fetched via llm_router.py using configurable subcategories.

    Persona-modified responses (e.g. mentor, reviewer) are enabled.

    Models like Mistral (via Ollama) are configured through config.json.

📁 Configuration

Ensure your config/config.json includes appropriate subcategory prompts like:

"prompts_by_subcategory": {
  "Tooling & Automation": "Summarize the workflow, tool, or automation concept in a concise technical format.",
  "Module Functionality": "Summarize the purpose of this module based on the provided function-level docstrings.",
  "_default": "Summarize the following idea into concise, meaningful bullet points."
}

