import pytest
from unittest.mock import MagicMock, patch
from src.enveil.collectors.os_collector import OSCollector
from src.enveil.core.command_executor import CommandExecutor

# --- Mock Data --- #
WINDOWS_OS_INFO = "Microsoft Windows 11 Pro"
LINUX_OS_INFO = "Ubuntu 22.04.3 LTS"
MACOS_OS_INFO = "macOS Sonoma 14.5"

# --- Test Cases --- #

@patch('src.enveil.core.platform_detector.PlatformDetector.is_windows', return_value=True)
@patch('src.enveil.core.platform_detector.PlatformDetector.is_linux', return_value=False)
@patch('src.enveil.core.platform_detector.PlatformDetector.is_macos', return_value=False)
def test_os_collector_windows(mock_is_macos, mock_is_linux, mock_is_windows):
    """Windows環境でのOS情報収集をテスト"""
    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.return_value = WINDOWS_OS_INFO

    collector = OSCollector(mock_executor)
    result = collector.collect()

    assert result['OS'] == WINDOWS_OS_INFO
    mock_executor.execute.assert_called_once_with("get_os_windows")

@patch('src.enveil.core.platform_detector.PlatformDetector.is_windows', return_value=False)
@patch('src.enveil.core.platform_detector.PlatformDetector.is_linux', return_value=True)
@patch('src.enveil.core.platform_detector.PlatformDetector.is_macos', return_value=False)
def test_os_collector_linux(mock_is_macos, mock_is_linux, mock_is_windows):
    """Linux環境でのOS情報収集をテスト"""
    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.return_value = LINUX_OS_INFO

    collector = OSCollector(mock_executor)
    result = collector.collect()

    assert result['OS'] == LINUX_OS_INFO
    mock_executor.execute.assert_called_once_with("get_os_linux")

@patch('src.enveil.core.platform_detector.PlatformDetector.is_windows', return_value=False)
@patch('src.enveil.core.platform_detector.PlatformDetector.is_linux', return_value=False)
@patch('src.enveil.core.platform_detector.PlatformDetector.is_macos', return_value=True)
def test_os_collector_macos(mock_is_macos, mock_is_linux, mock_is_windows):
    """macOS環境でのOS情報収集をテスト"""
    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.return_value = MACOS_OS_INFO

    collector = OSCollector(mock_executor)
    result = collector.collect()

    assert result['OS'] == MACOS_OS_INFO
    mock_executor.execute.assert_called_once_with("get_os_macos")

@patch('src.enveil.core.platform_detector.PlatformDetector.is_windows', return_value=True)
def test_os_collector_command_failure(mock_is_windows):
    """コマンド実行が失敗した場合のテスト"""
    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.side_effect = Exception("Command failed")

    collector = OSCollector(mock_executor)
    result = collector.collect()

    assert result['OS'] == "N/A"
