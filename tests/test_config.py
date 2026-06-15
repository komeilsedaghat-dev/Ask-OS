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
    # Setup temporary config file path
    temp_config = tmp_path / ".env"
    mocker.patch("askos.config.GLOBAL_CONFIG_FILE", temp_config)
    mocker.patch("askos.config.GLOBAL_CONFIG_DIR", tmp_path)
    
    config.save_global_config("new_key", "https://new.url", "new_model")
    
    assert temp_config.exists()
    content = temp_config.read_text()
    assert "OPENAI_API_KEY=new_key" in content
    assert "OPENAI_BASE_URL=https://new.url" in content
    assert "OPENAI_MODEL_NAME=new_model" in content
