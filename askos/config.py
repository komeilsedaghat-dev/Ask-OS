import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Define global configuration paths
GLOBAL_CONFIG_DIR = Path.home() / ".config" / "askos"
PROFILES_DIR = GLOBAL_CONFIG_DIR / "profiles"
ACTIVE_CONFIG_FILE = GLOBAL_CONFIG_DIR / "config.json"

def get_active_profile() -> str:
    """
    Retrieve the active profile name. Defaults to 'default'.
    """
    if ACTIVE_CONFIG_FILE.exists():
        try:
            with open(ACTIVE_CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data.get("active_profile", "default")
        except Exception:
            pass
    return "default"

def set_active_profile(profile_name: str):
    """
    Save the active profile name.
    """
    GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(ACTIVE_CONFIG_FILE, "w") as f:
        json.dump({"active_profile": profile_name}, f)

def get_profile_path(profile_name: str) -> Path:
    return PROFILES_DIR / f"{profile_name}.env"

def migrate_old_config():
    """
    Migrates ~/.config/askos/.env to ~/.config/askos/profiles/default.env if needed.
    """
    old_file = GLOBAL_CONFIG_DIR / ".env"
    default_profile_file = get_profile_path("default")
    if old_file.exists():
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        if not default_profile_file.exists():
            try:
                old_file.rename(default_profile_file)
            except Exception:
                pass
        else:
            try:
                old_file.unlink()
            except OSError:
                pass

def load_configurations():
    """
    Loads configurations from both global and local directories.
    Local environment variables override global ones.
    """
    migrate_old_config()
    
    # Load settings from active profile
    active_profile = get_active_profile()
    profile_file = get_profile_path(active_profile)
    if profile_file.exists():
        load_dotenv(dotenv_path=profile_file)

    # Load local settings, overriding any duplicate keys from global
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
    Save the configuration globally at the active profile config path.
    """
    active_profile = get_active_profile()
    save_profile_config(active_profile, api_key, base_url, model_name)

def save_profile_config(profile_name: str, api_key: str, base_url: str, model_name: str):
    """
    Save a profile configuration at ~/.config/askos/profiles/<name>.env.
    """
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    profile_file = get_profile_path(profile_name)
    content = (
        f"# Ask-OS Profile: {profile_name}\n"
        f"OPENAI_API_KEY={api_key}\n"
        f"OPENAI_BASE_URL={base_url}\n"
        f"OPENAI_MODEL_NAME={model_name}\n"
    )
    temp_file = profile_file.with_suffix(".tmp")
    with open(temp_file, "w") as f:
        f.write(content)
    temp_file.replace(profile_file)

def list_profiles() -> list[str]:
    """
    List all available profiles.
    """
    migrate_old_config()
    if not PROFILES_DIR.exists():
        return ["default"]
    
    profiles = []
    for file in PROFILES_DIR.glob("*.env"):
        profiles.append(file.stem)
    
    if not profiles:
        return ["default"]
    return sorted(profiles)

def delete_profile(profile_name: str) -> bool:
    """
    Delete a profile. Returns True if deleted successfully.
    """
    profile_file = get_profile_path(profile_name)
    if profile_file.exists():
        try:
            profile_file.unlink()
            return True
        except OSError:
            pass
    return False
