import pytest
from unittest.mock import patch, MagicMock

from src.enveil import main

@pytest.fixture
def mock_api():
    """EnveilAPIのモックを作成"""
    with patch('src.enveil.main.EnveilAPI') as mock_api_class:
        mock_api_instance = MagicMock()
        mock_api_instance.get_hardware_info.return_value = {"cpu": "test-cpu"}
        mock_api_instance.get_os_info.return_value = {"os": "test-os"}
        mock_api_instance.get_software_info.return_value = {"python": "test-python"}
        mock_api_class.return_value = mock_api_instance
        yield mock_api_instance

def run_main_with_args(args):
    with patch('sys.argv', ['enveil'] + args):
        main()

def test_main_no_args(mock_api):
    """引数なしで実行した場合、すべての情報が収集されることをテスト"""
    run_main_with_args([])
    mock_api.get_hardware_info.assert_called_once()
    mock_api.get_os_info.assert_called_once()
    mock_api.get_software_info.assert_called_once_with(software_list=None)

def test_main_hardware_only(mock_api):
    """--hardwareフラグを指定した場合、ハードウェア情報のみ収集されることをテスト"""
    run_main_with_args(['--hardware'])
    mock_api.get_hardware_info.assert_called_once()
    mock_api.get_os_info.assert_not_called()
    mock_api.get_software_info.assert_not_called()

def test_main_os_only(mock_api):
    """--osフラグを指定した場合、OS情報のみ収集されることをテスト"""
    run_main_with_args(['--os'])
    mock_api.get_hardware_info.assert_not_called()
    mock_api.get_os_info.assert_called_once()
    mock_api.get_software_info.assert_not_called()

def test_main_software_all(mock_api):
    """--softwareフラグのみを指定した場合、すべてのソフトウェア情報が収集されることをテスト"""
    run_main_with_args(['--software'])
    mock_api.get_hardware_info.assert_not_called()
    mock_api.get_os_info.assert_not_called()
    mock_api.get_software_info.assert_called_once_with(software_list=None)

def test_main_software_specific(mock_api):
    """--softwareフラグに引数を指定した場合、特定のソフトウェア情報が収集されることをテスト"""
    run_main_with_args(['--software', 'Python', 'Git'])
    mock_api.get_hardware_info.assert_not_called()
    mock_api.get_os_info.assert_not_called()
    mock_api.get_software_info.assert_called_once_with(software_list=['Python', 'Git'])

def test_main_multiple_flags(mock_api):
    """複数のフラグを指定した場合、対応するすべての情報が収集されることをテスト"""
    run_main_with_args(['--hardware', '--os'])
    mock_api.get_hardware_info.assert_called_once()
    mock_api.get_os_info.assert_called_once()
    mock_api.get_software_info.assert_not_called()

def test_main_config_file():
    """--configフラグで設定ファイルが渡されることをテスト"""
    with patch('src.enveil.main.EnveilAPI') as mock_api_class:
        mock_instance = mock_api_class.return_value
        mock_instance.get_hardware_info.return_value = {}
        mock_instance.get_os_info.return_value = {}
        mock_instance.get_software_info.return_value = {}
        run_main_with_args(['--config', 'my_config.json'])
        mock_api_class.assert_called_once_with(config_path='my_config.json')
