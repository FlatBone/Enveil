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

DEFAULT_SOFTWARE = {
    "Python": "python --version || python3 --version",
    "Git": "git --version",
    "Docker": "docker --version"
}

@pytest.fixture
def mock_default_software():
    with patch('src.enveil.config.config_manager.DEFAULT_SOFTWARE', DEFAULT_SOFTWARE) as mock:
        yield mock

def test_load_config_success(tmp_path, mock_default_software):
    """正常な設定ファイルを読み込めることをテスト"""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(VALID_CONFIG))
    
    manager = ConfigManager(config_path=str(config_path))
    config = manager.load_config()
    
    assert config == VALID_CONFIG

def test_load_config_file_not_found(mock_default_software):
    """設定ファイルが存在しない場合にデフォルト設定を返すことをテスト"""
    manager = ConfigManager(config_path="non_existent_config.json")
    config = manager.load_config()
    
    assert config['software'] == DEFAULT_SOFTWARE

def test_load_config_invalid_json(tmp_path, mock_default_software):
    """不正なJSONファイルの場合にConfigurationErrorを送出するテスト"""
    config_path = tmp_path / "invalid.json"
    config_path.write_text("this is not json")
    
    manager = ConfigManager(config_path=str(config_path))
    with pytest.raises(ConfigurationError, match="不正なJSON形式です"):
        manager.load_config()

def test_get_software_commands_from_file(tmp_path, mock_default_software):
    """設定ファイルからソフトウェアコマンドを取得するテスト"""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(VALID_CONFIG))
    
    manager = ConfigManager(config_path=str(config_path))
    commands = manager.get_software_commands()
    
    assert commands == VALID_CONFIG['software']

def test_get_software_commands_from_default(mock_default_software):
    """デフォルト設定からソフトウェアコマンドを取得するテスト"""
    manager = ConfigManager(config_path="non_existent_config.json")
    commands = manager.get_software_commands()
    
    assert commands == DEFAULT_SOFTWARE
