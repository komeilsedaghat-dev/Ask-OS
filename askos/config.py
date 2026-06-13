import os
from pathlib import Path
from dotenv import load_dotenv

# Define global configuration paths
GLOBAL_CONFIG_DIR = Path.home() / ".config" / "askos"
GLOBAL_CONFIG_FILE = GLOBAL_CONFIG_DIR / ".env"

def load_configurations():
    """
    Loads configurations from both global and local directories.
    Local environment variables override global ones.
    """
    # 1. Load global settings first
    if GLOBAL_CONFIG_FILE.exists():
        load_dotenv(dotenv_path=GLOBAL_CONFIG_FILE)

    # 2. Load local settings, overriding any duplicate keys from global
    load_dotenv(override=True)

# Run loading immediately on import
load_configurations()

def get_api_key() -> str:
    """
    Retrieve the OpenAI-compatible API key from the environment.
    """
    return os.getenv("OPENAI_API_KEY", "")

def get_base_url() -> str:
    """
    Retrieve the custom API base URL from the environment.
    Defaults to OpenAI's public endpoint.
    """
    return os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

def get_model_name() -> str:
    """
    Retrieve the model name from the environment.
    """
    return os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

def save_global_config(api_key: str, base_url: str, model_name: str):
    """
    Save the configuration globally at ~/.config/askos/.env.
    """
    GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    content = (
        "# Ask-OS Global Configuration\n"
        f"OPENAI_API_KEY={api_key}\n"
        f"OPENAI_BASE_URL={base_url}\n"
        f"OPENAI_MODEL_NAME={model_name}\n"
    )
    # Write to a temporary file and rename it to make it atomic
    temp_file = GLOBAL_CONFIG_FILE.with_suffix(".tmp")
    with open(temp_file, "w") as f:
        f.write(content)
    temp_file.replace(GLOBAL_CONFIG_FILE)
