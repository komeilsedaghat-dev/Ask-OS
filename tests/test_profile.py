import json
from pathlib import Path
from askos import config

def test_profile_lifecycle(tmp_path, mocker):
    temp_dir = tmp_path / "askos"
    mocker.patch("askos.config.GLOBAL_CONFIG_DIR", temp_dir)
    mocker.patch("askos.config.PROFILES_DIR", temp_dir / "profiles")
    mocker.patch("askos.config.ACTIVE_CONFIG_FILE", temp_dir / "config.json")
    
    # 1. Test get active profile defaults to 'default'
    assert config.get_active_profile() == "default"
    
    # 2. Test set active profile
    config.set_active_profile("local-ollama")
    assert config.get_active_profile() == "local-ollama"
    
    # 3. Test save profile configuration
    config.save_profile_config("local-ollama", "test_key", "http://localhost:11434/v1", "llama3")
    profile_file = config.get_profile_path("local-ollama")
    assert profile_file.exists()
    
    # Check contents
    content = profile_file.read_text()
    assert "OPENAI_API_KEY=test_key" in content
    assert "OPENAI_BASE_URL=http://localhost:11434/v1" in content
    assert "OPENAI_MODEL_NAME=llama3" in content

    # 4. Test list profiles
    profiles = config.list_profiles()
    assert "local-ollama" in profiles
    
    # 5. Test delete profile
    config.set_active_profile("default") # Switch active away from local-ollama to delete it
    success = config.delete_profile("local-ollama")
    assert success is True
    assert not profile_file.exists()
    assert "local-ollama" not in config.list_profiles()
