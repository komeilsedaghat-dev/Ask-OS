import sqlite3
from pathlib import Path

# Locate or create the cache directory in the user's home directory
CACHE_DIR = Path.home() / ".cache" / "askos"
CACHE_FILE = CACHE_DIR / "query_cache.db"

def init_cache():
    """
    Ensure the cache directory and database exist with the correct schema.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(CACHE_FILE) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS command_cache (
                prompt TEXT,
                model_name TEXT,
                command TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (prompt, model_name)
            )
            """
        )

def get_cached_command(prompt: str, model_name: str) -> str:
    """
    Retrieve a cached command for a given prompt and model.
    Returns None if cache miss.
    """
    try:
        init_cache()
        # Strip and lowercase the prompt to normalize matches (e.g. ignoring case/trailing spaces)
        normalized_prompt = prompt.strip().lower()
        with sqlite3.connect(CACHE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT command FROM command_cache WHERE prompt = ? AND model_name = ?",
                (normalized_prompt, model_name),
            )
            row = cursor.fetchone()
            return row[0] if row else None
    except Exception:
        # Fallback gracefully if database read fails
        return None

def set_cached_command(prompt: str, model_name: str, command: str):
    """
    Store a generated command in the cache.
    """
    try:
        init_cache()
        normalized_prompt = prompt.strip().lower()
        with sqlite3.connect(CACHE_FILE) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO command_cache (prompt, model_name, command)
                VALUES (?, ?, ?)
                """,
                (normalized_prompt, model_name, command),
            )
    except Exception:
        # Fallback gracefully if database write fails
        pass
