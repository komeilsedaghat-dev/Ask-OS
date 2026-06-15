import os
import platform
import shutil
from askos.utils import collect_environment_context

def test_collect_environment_context(mocker):
    # Mock system info
    mocker.patch("platform.system", return_value="Linux")
    mocker.patch.dict(os.environ, {"SHELL": "/bin/zsh"})
    
    # Mock package manager checks
    def mock_which(cmd):
        if cmd in ["apt-get", "pip"]:
            return f"/usr/bin/{cmd}"
        return None
    mocker.patch("shutil.which", side_effect=mock_which)
    
    # Mock root privileges
    mocker.patch("os.getuid", return_value=0)
    
    context = collect_environment_context()
    
    assert "Target OS: Linux" in context
    assert "Active Shell: zsh" in context
    assert "Privilege Level: root/administrator (sudo not needed)" in context
    assert "Available Installers/CLI Tools: apt-get, pip" in context

def test_collect_environment_context_non_root(mocker):
    mocker.patch("platform.system", return_value="Darwin")
    mocker.patch.dict(os.environ, {"SHELL": "/bin/bash"})
    mocker.patch("shutil.which", return_value=None)
    mocker.patch("os.getuid", return_value=1000)
    
    context = collect_environment_context()
    
    assert "Target OS: Darwin" in context
    assert "Active Shell: bash" in context
    assert "Privilege Level: standard user (prepend sudo for system-level actions)" in context
    assert "Available Installers/CLI Tools: none detected" in context
