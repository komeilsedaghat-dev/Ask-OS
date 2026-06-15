import pytest
import typer
from askos.main import execute_ask_flow

def test_execute_ask_flow_success(mocker):
    # Mock cache
    mocker.patch("askos.cache.get_cached_command", return_value="ls -la")
    mocker.patch("askos.cache.log_execution")
    
    # Mock executor
    mock_executor_class = mocker.patch("askos.main.CommandExecutor")
    mock_executor = mock_executor_class.return_value
    mock_executor.execute.return_value = (0, "file1.txt\nfile2.txt")
    
    # Run ask flow (should execute successfully using cached command)
    with pytest.raises(typer.Exit) as exc:
        execute_ask_flow("list files", None, None, None, explain=False)
        
    assert exc.value.exit_code == 0
    mock_executor.execute.assert_called_once_with("ls -la")

def test_execute_ask_flow_retry_loop(mocker):
    # Mock cache
    mocker.patch("askos.cache.get_cached_command", return_value=None)
    mocker.patch("askos.cache.log_execution")
    
    # Mock LLM Client
    mock_llm_class = mocker.patch("askos.main.LLMClient")
    mock_llm = mock_llm_class.return_value
    mock_llm.generate_command.return_value = ("wrong_cmd", False)
    mock_llm.generate_correction.return_value = ("corrected_cmd")
    
    # Mock executor: first execution fails (exit code 1), second execution succeeds (exit code 0)
    mock_executor_class = mocker.patch("askos.main.CommandExecutor")
    mock_executor = mock_executor_class.return_value
    mock_executor.execute.side_effect = [
        (1, "error output"),
        (0, "success output")
    ]
    
    # Mock user confirmation to retry
    mocker.patch("typer.confirm", return_value=True)
    
    # Run ask flow
    with pytest.raises(typer.Exit) as exc:
        execute_ask_flow("run code", None, None, None, explain=False)
        
    assert exc.value.exit_code == 0
    # generate_correction should have been called
    mock_llm.generate_correction.assert_called_once_with("run code", "wrong_cmd", "error output")
