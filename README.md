# Ask-OS 🤖💻

**Ask-OS** is an AI-powered terminal assistant that translates natural language requests into OS commands, allowing you to review and safely execute them directly in your shell. 

To save costs and improve performance, it includes a local SQLite3-backed caching layer that intercepts queries and resolves duplicate prompts in sub-milliseconds at $0.00 cost.

---

## Features

- **Natural Language Translation**: Describe what you want to achieve, and Ask-OS will generate the corresponding terminal command.
- **Safe Subprocess Execution**: Visual confirmation prompt stops any commands from executing until you review and explicitly authorize them.
- **Local SQLite3 Caching**: Repeated requests are cached locally per-model, saving LLM tokens and API costs.
- **OpenAI-Compatible Integration**: Works with any OpenAI-compatible API (e.g., OpenAI, OpenRouter, Local Ollama, DeepSeek).
- **Beautiful Terminal Interface**: Clean styling, boxes, and icons powered by `rich` and `typer`.

---

## Tech Stack

- **[Typer](https://typer.tiangolo.com/)**: For the CLI interface.
- **[Rich](https://rich.readthedocs.io/)**: For beautiful terminal outputs and layouts.
- **[OpenAI Python SDK](https://github.com/openai/openai-python)**: For API integration.
- **[Python-dotenv](https://github.com/theofidry/django-dotenv)**: For loading configuration environment variables.
- **SQLite3**: For query caching.

---

## Installation

### Option 1: Install directly from GitHub (Recommended)
Install globally or inside your active virtual environment:
```bash
pip install git+https://github.com/komeilsedaghat-dev/Ask-OS.git
```

### Option 2: Local Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/komeilsedaghat-dev/Ask-OS.git
   cd Ask-OS
   ```
2. Set up virtual environment and install packages in editable mode:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

---

## Configuration

Ask-OS reads your credentials from environment variables. You can configure them by creating a `.env` file in your project or home directory:

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```
2. Populate `.env` with your API credentials:
   ```ini
   OPENAI_API_KEY=your_actual_api_key
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENAI_MODEL_NAME=gpt-4o-mini
   ```

---

## Usage

Run the `askos` command followed by your natural language prompt:

```bash
askos "find all python files in the downloads directory"
```

### Options & Overrides
You can override your `.env` settings dynamically at runtime using flags:

- **`-k, --api-key`**: Override OpenAI API key.
- **`-u, --base-url`**: Override API base URL (e.g., for custom endpoints or Ollama).
- **`-m, --model`**: Override target model name.

**Example using custom endpoint and model:**
```bash
askos "list docker containers running on port 80" -u "http://localhost:11434/v1" -m "llama3"
```
