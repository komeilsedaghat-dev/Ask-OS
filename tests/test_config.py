import os
from pathlib import Path
from askos import config

def test_getters(mocker):
    mocker.patch.dict(os.environ, {
        "OPENAI_API_KEY": "test_key",
        "OPENAI_BASE_URL": "https://test.api.com",
        "OPENAI_MODEL_NAME": "test_model"
    })
    
    assert config.get_api_key() == "test_key"
    assert config.get_base_url() == "https://test.api.com"
    assert config.get_model_name() == "test_model"

def test_save_global_config(tmp_path, mocker):
    temp_dir = tmp_path / "askos"
    mocker.patch("askos.config.GLOBAL_CONFIG_DIR", temp_dir)
    mocker.patch("askos.config.PROFILES_DIR", temp_dir / "profiles")
    mocker.patch("askos.config.ACTIVE_CONFIG_FILE", temp_dir / "config.json")
    
    config.save_global_config("new_key", "https://new.url", "new_model")
    
    default_profile_file = temp_dir / "profiles" / "default.env"
    assert default_profile_file.exists()
    content = default_profile_file.read_text()
    assert "OPENAI_API_KEY=new_key" in content
    assert "OPENAI_BASE_URL=https://new.url" in content
    assert "OPENAI_MODEL_NAME=new_model" in content
