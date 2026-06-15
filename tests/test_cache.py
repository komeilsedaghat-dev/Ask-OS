import sqlite3
from pathlib import Path
from askos import cache

def test_cache_operations(tmp_path, mocker):
    temp_db = tmp_path / "query_cache.db"
    mocker.patch("askos.cache.CACHE_FILE", temp_db)
    mocker.patch("askos.cache.CACHE_DIR", tmp_path)
    
    # 1. Test init_cache creates tables
    cache.init_cache()
    assert temp_db.exists()
    
    # Verify tables
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert "command_cache" in tables
        assert "execution_history" in tables

    # 2. Test cache miss
    val = cache.get_cached_command("list files", "gpt-4o")
    assert val is None
    
    # 3. Test cache set and hit
    cache.set_cached_command("list files", "gpt-4o", "ls -la")
    val = cache.get_cached_command("list files", "gpt-4o")
    assert val == "ls -la"
    
    # Test case insensitivity and trailing spaces
    val_variant = cache.get_cached_command("  List Files  ", "gpt-4o")
    assert val_variant == "ls -la"

    # 4. Test logging execution
    cache.log_execution("list files", "ls -la", 0)
    history = cache.get_history(limit=5)
    assert len(history) == 1
    assert history[0][0] == "list files"
    assert history[0][1] == "ls -la"
    assert history[0][2] == 0
