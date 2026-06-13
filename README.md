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

### Option 1: Global Installation using `pipx` (Recommended)
This is the easiest way to install Ask-OS globally on modern OS environments without encountering conflicts (PEP 668):

1. **Install `pipx`** if you don't have it already:
   - **Debian/Ubuntu**: `sudo apt install pipx && pipx ensurepath`
   - **macOS (Homebrew)**: `brew install pipx && pipx ensurepath`
   - **Windows**: `pip install pipx && pipx ensurepath`
   *(Note: Remember to restart your terminal after running `ensurepath` so the changes take effect)*

2. **Install Ask-OS**:
   ```bash
   pipx install git+https://github.com/komeilsedaghat-dev/Ask-OS.git
   ```

### Option 2: Local Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/komeilsedaghat-dev/Ask-OS.git
   cd Ask-OS
   ```
2. Set up a virtual environment and install the package in editable mode:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

---

## Configuration

Ask-OS supports both **global configuration** and **local directory overrides**:

### 1. Interactive Global Configuration (Recommended)
You can configure your settings globally without manually editing files:
```bash
askos configure
```
This will interactively prompt you for your API credentials and save them securely to `~/.config/askos/.env`.

### 2. Local Environment Variables (.env)
For project-specific settings, create a `.env` file in your current working directory. Values in your local `.env` take precedence over your global configurations:
```ini
OPENAI_API_KEY=your_local_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL_NAME=gpt-4o-mini
```

---

## Usage

Ask-OS dynamically routes your commands based on subcommands. 

### 1. Ask Command (Default Action)
To ask for a command, just call `askos` with your prompt:
```bash
askos "find all python files in the downloads directory"
```
#### Options & Overrides
You can override your configured settings dynamically at runtime using flags:
- **`-k, --api-key`**: Override OpenAI API key.
- **`-u, --base-url`**: Override API base URL.
- **`-m, --model`**: Override target model name.

*Example using custom endpoint and model:*
```bash
askos "list docker containers running on port 80" -u "http://localhost:11434/v1" -m "llama3"
```

### 2. Self-Correction Flow
If a command you confirmed fails (exits with a non-zero code), Ask-OS will ask:
```
⚠ Command failed. Would you like the AI to generate a corrected version? [y/N]:
```
If you choose `y`, the assistant will analyze the terminal error logs, construct a corrected command, and prompt you to run it.

### 3. Cache Management
View cache database statistics or clear saved queries:
```bash
# View cache usage, database size, and location
askos cache stats

# Remove all cached queries
askos cache clear
```
