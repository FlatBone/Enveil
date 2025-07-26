import pytest
from unittest.mock import patch, MagicMock
import logging
from pathlib import Path

from src.enveil.main import main
from src.enveil.utils.exceptions import EnveilException

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

@pytest.mark.parametrize(
    "found_path_obj",
    [
        Path('/home/user/.config/enveil/config.json'),
        None
    ],
    ids=["config_found", "config_not_found"]
)
@patch('src.enveil.main.ConfigManager')
def test_main_config_flag(mock_config_manager, found_path_obj, capsys):
    """--configフラグが設定ファイルのパスまたはメッセージを正しく表示するテスト"""
    # モックインスタンスのセットアップ
    mock_instance = mock_config_manager.return_value
    mock_instance.find_config_file.return_value = found_path_obj
    
    # モックするパスのリスト
    potential_paths = [
        Path('/fake/cwd/config.json'),
        Path('/home/user/.config/enveil/config.json')
    ]
    mock_instance.get_potential_config_paths.return_value = potential_paths

    run_main_with_args(['--config'])
    captured = capsys.readouterr()

    if found_path_obj:
        # 【ファイルが見つかった場合】
        expected_output = f"Configuration file in use: {found_path_obj}"
        assert captured.out.strip() == expected_output
    else:
        # 【ファイルが見つからない場合】
        assert "No custom configuration file found" in captured.out
        assert "To customize, create a 'config.json' file" in captured.out
        # Pathオブジェクトを文字列に変換して比較することで、OS依存の問題を解消
        assert str(potential_paths[0]) in captured.out
        assert str(potential_paths[1]) in captured.out

@patch('src.enveil.main.EnveilAPI')
def test_main_use_default_flag(mock_api_class):
    """--use-defaultフラグがEnveilAPIに正しく渡されることをテスト"""
    run_main_with_args(['--hardware', '--use-default'])
    mock_api_class.assert_called_once_with(use_default_config=True)

def test_main_enveil_exception(mock_api, caplog):
    """EnveilExceptionが発生した場合にエラーログが出力されることをテスト"""
    mock_api.get_hardware_info.side_effect = EnveilException("Test error")
    with caplog.at_level(logging.ERROR):
        run_main_with_args(['--hardware'])
        assert "An error occurred: Test error" in caplog.text