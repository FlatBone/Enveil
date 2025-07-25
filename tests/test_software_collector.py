import pytest
from unittest.mock import MagicMock, patch
from src.enveil.collectors.software_collector import SoftwareCollector
from src.enveil.core.command_executor import CommandExecutor
from src.enveil.config.config_manager import ConfigManager

# --- Mock Data --- #
SOFTWARE_COMMANDS = {
    "Python": "python --version",
    "Git": "git --version",
    "NonExistent": "nonexistent --version"
}

@pytest.fixture
def mock_config_manager():
    """ConfigManagerのモックを作成"""
    mock = MagicMock(spec=ConfigManager)
    mock.get_software_commands.return_value = SOFTWARE_COMMANDS
    return mock

@pytest.fixture
def mock_command_executor():
    """CommandExecutorのモックを作成"""
    mock = MagicMock(spec=CommandExecutor)
    def execute_side_effect(command_key):
        if command_key == "Python":
            return "Python 3.9.1"
        if command_key == "Git":
            return "git version 2.30.1"
        if command_key == "NonExistent":
            raise Exception("Command not found")
        return ""
    mock.execute.side_effect = execute_side_effect
    return mock

def test_collect_software_versions_all(mock_config_manager, mock_command_executor):
    """すべてのソフトウェアバージョンを収集するテスト"""
    collector = SoftwareCollector(mock_command_executor, mock_config_manager)
    result = collector.collect()

    assert result["Python"] == "Python 3.9.1"
    assert result["Git"] == "git version 2.30.1"
    assert result["NonExistent"] == "N/A"
    assert mock_command_executor.execute.call_count == 3

def test_collect_software_versions_specific(mock_config_manager, mock_command_executor):
    """指定されたソフトウェアのバージョンのみを収集するテスト"""
    collector = SoftwareCollector(mock_command_executor, mock_config_manager)
    result = collector.collect(software_list=["Python", "Git"])

    assert "Python" in result
    assert "Git" in result
    assert "NonExistent" not in result
    assert result["Python"] == "Python 3.9.1"
    assert result["Git"] == "git version 2.30.1"
    assert mock_command_executor.execute.call_count == 2

def test_collect_with_empty_list(mock_config_manager, mock_command_executor):
    """空のリストが指定された場合に何も収集しないことをテスト"""
    collector = SoftwareCollector(mock_command_executor, mock_config_manager)
    result = collector.collect(software_list=[])

    assert not result
    mock_command_executor.execute.assert_not_called()
