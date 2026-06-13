import sqlite3
from pathlib import Path

# Locate or create the cache directory in the user's home directory
CACHE_DIR = Path.home() / ".cache" / "askos"
CACHE_FILE = CACHE_DIR / "query_cache.db"

def init_cache():
    """
    Ensure the cache directory and database exist with the correct schemas.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(CACHE_FILE) as conn:
        # Table 1: Command Caching
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
        # Table 2: Execution History Audits
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT,
                command TEXT,
                exit_code INTEGER,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        pass

def log_execution(prompt: str, command: str, exit_code: int):
    """
    Log an executed command to the execution history.
    """
    try:
        init_cache()
        with sqlite3.connect(CACHE_FILE) as conn:
            conn.execute(
                """
                INSERT INTO execution_history (prompt, command, exit_code)
                VALUES (?, ?, ?)
                """,
                (prompt, command, exit_code),
            )
    except Exception:
        pass

def get_history(limit: int = 20) -> list:
    """
    Retrieve recent command execution records from history.
    """
    try:
        init_cache()
        with sqlite3.connect(CACHE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT prompt, command, exit_code, datetime(executed_at, 'localtime') 
                FROM execution_history 
                ORDER BY executed_at DESC 
                LIMIT ?
                """,
                (limit,),
            )
            return cursor.fetchall()
    except Exception:
        return []
