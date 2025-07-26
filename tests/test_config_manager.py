import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open
from src.enveil.config.config_manager import ConfigManager
from src.enveil.utils.exceptions import ConfigurationError

# --- Mock Data --- #
VALID_CONFIG = {
    "software": {
        "Python": "python --version",
        "Git": "git --version"
    },
    "security": {
        "allowed_command_patterns": [
            "^python --version$",
            "^git --version$"
        ]
    }
}

INVALID_SCHEMA_CONFIG = {
    "software": ["python", "git"] 
}

# This represents the source for the default config
DEFAULT_SOFTWARE = {
    "Python": "python --version || python3 --version",
    "Git": "git --version",
    "Docker": "docker --version"
}

@pytest.fixture
def mock_default_software():
    with patch('src.enveil.config.config_manager.DEFAULT_SOFTWARE', DEFAULT_SOFTWARE) as mock:
        yield mock

@patch('src.enveil.config.config_manager.ConfigManager.find_config_file')
def test_load_config_success(mock_find_config, tmp_path, mock_default_software):
    """正常な設定ファイルを読み込めることをテスト"""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(VALID_CONFIG))
    mock_find_config.return_value = config_path
    
    manager = ConfigManager()
    config = manager.load_config()
    
    assert config == VALID_CONFIG

@patch('src.enveil.config.config_manager.ConfigManager.find_config_file', return_value=None)
def test_load_config_file_not_found(mock_find, mock_default_software):
    """設定ファイルが存在しない場合にデフォルト設定を返すことをテスト"""
    manager = ConfigManager()
    config = manager.load_config()
    
    # The loaded default config is structured
    expected_software_config = {name: {'command': cmd} for name, cmd in DEFAULT_SOFTWARE.items()}
    assert config['software'] == expected_software_config

@patch('src.enveil.config.config_manager.ConfigManager.find_config_file')
def test_load_config_invalid_json(mock_find_config, tmp_path, mock_default_software):
    """不正なJSONファイルの場合にConfigurationErrorを送出するテスト"""
    config_path = tmp_path / "invalid.json"
    config_path.write_text("this is not json")
    mock_find_config.return_value = config_path

    manager = ConfigManager()
    with pytest.raises(ConfigurationError, match="不正なJSON形式です"):
        manager.load_config()

@patch('src.enveil.config.config_manager.ConfigManager.find_config_file')
def test_get_software_commands_from_file(mock_find_config, tmp_path, mock_default_software):
    """設定ファイルからソフトウェアコマンドを取得するテスト"""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(VALID_CONFIG))
    mock_find_config.return_value = config_path
    
    manager = ConfigManager()
    commands = manager.get_software_commands()
    
    assert commands == VALID_CONFIG['software']

@patch('src.enveil.config.config_manager.ConfigManager.find_config_file', return_value=None)
def test_get_software_commands_from_default(mock_find, mock_default_software):
    """デフォルト設定からソフトウェアコマンドを取得するテスト"""
    manager = ConfigManager()
    commands = manager.get_software_commands()
    
    # This should return the flattened dict, which matches the original DEFAULT_SOFTWARE
    assert commands == DEFAULT_SOFTWARE

@patch('src.enveil.config.config_manager.ConfigManager.find_config_file')
def test_load_config_invalid_schema(mock_find_config, tmp_path, mock_default_software):
    """不正なスキーマのファイルの場合にConfigurationErrorを送出するテスト"""
    config_path = tmp_path / "invalid_schema.json"
    config_path.write_text(json.dumps(INVALID_SCHEMA_CONFIG))
    mock_find_config.return_value = config_path

    manager = ConfigManager()
    with pytest.raises(ConfigurationError, match="'software'セクションが不正です"):
        manager.load_config()

@patch('src.enveil.config.config_manager.ConfigManager.find_config_file')
def test_load_config_unsafe_command(mock_find_config, tmp_path, mock_default_software):
    """危険なコマンドを含む設定ファイルの場合にConfigurationErrorを送出するテスト"""
    unsafe_config = {
        "software": {
            "Malicious": "echo pwned; rm -rf /"
        }
    }
    config_path = tmp_path / "unsafe_config.json"
    config_path.write_text(json.dumps(unsafe_config))
    mock_find_config.return_value = config_path
    
    manager = ConfigManager()
    with pytest.raises(ConfigurationError, match="セキュリティ上許可されていません"):
        manager.load_config()