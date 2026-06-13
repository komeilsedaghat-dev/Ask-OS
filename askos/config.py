import os
from dotenv import load_dotenv

# Automatically load the environment variables from .env if present
load_dotenv()

def get_api_key() -> str:
    """
    Retrieve the OpenAI-compatible API key from the environment.
    """
    return os.getenv("OPENAI_API_KEY", "")

def get_base_url() -> str:
    """
    Retrieve the custom API base URL from the environment.
    Defaults to OpenAI's default.
    """
    return os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

def get_model_name() -> str:
    """
    Retrieve the model name from the environment.
    """
    return os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
