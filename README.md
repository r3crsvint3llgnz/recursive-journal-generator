# ⚡ Sovereign Journal Agent

An automated serverless pipeline that captures raw LLM cognitive streams and distills them into structured, first-person journal entries.

## 🎯 Purpose

Modern LLM workflows generate massive amounts of cognitive exhaust—deep reasoning, architectural decisions, and creative breakthroughs that are often lost in chat history. This agent preserves that intelligence by:

1. **Ingesting**: Capturing raw conversation exports (ChatGPT/Claude).
2. **Analyzing**: Running sentiment analysis and identifying key architectural patterns.
3. **Synthesizing**: Using LLMs (**Gemini 1.5/2.5**) to rewrite logs into first-person journal entries.
4. **Exporting**: Generating clean, tagged Markdown files ready for Obsidian injection.

## 🏗️ Architecture (Serverless)

Built on **AWS SAM** for maximum scalability and minimal overhead:

- **AWS Lambda**: Core Python processing logic and LLM orchestration.
- **API Gateway**: Endpoint for triggered ingests.
- **Gemini AI**: High-context processing for stylization and synthesis.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- AWS SAM CLI
- Gemini API Key

### Installation
1. `poetry install` (or `pip install -r requirements.txt`)
2. `sam local start-api` to test locally.
3. `sam deploy` to push to AWS.

## 📄 License

MIT © 2026 Seth Robins / Recursive Intelligence
