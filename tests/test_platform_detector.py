import pytest
from unittest.mock import patch
from src.enveil.core.platform_detector import PlatformDetector
from src.enveil.utils.exceptions import PlatformNotSupportedError

@patch('platform.system')
def test_get_platform_windows(mock_system):
    """Windowsプラットフォームを正しく検出できるかテスト"""
    mock_system.return_value = 'Windows'
    assert PlatformDetector.get_platform() == 'windows'
    assert PlatformDetector.is_windows() is True
    assert PlatformDetector.is_linux() is False
    assert PlatformDetector.is_macos() is False

@patch('platform.system')
def test_get_platform_linux(mock_system):
    """Linuxプラットフォームを正しく検出できるかテスト"""
    mock_system.return_value = 'Linux'
    assert PlatformDetector.get_platform() == 'linux'
    assert PlatformDetector.is_windows() is False
    assert PlatformDetector.is_linux() is True
    assert PlatformDetector.is_macos() is False

@patch('platform.system')
def test_get_platform_macos(mock_system):
    """macOSプラットフォームを正しく検出できるかテスト"""
    mock_system.return_value = 'Darwin'
    assert PlatformDetector.get_platform() == 'macos'
    assert PlatformDetector.is_windows() is False
    assert PlatformDetector.is_linux() is False
    assert PlatformDetector.is_macos() is True

@patch('platform.system')
def test_get_platform_unsupported(mock_system):
    """サポートされていないプラットフォームで例外を送出するかテスト"""
    mock_system.return_value = 'Java'
    with pytest.raises(PlatformNotSupportedError, match="Unsupported platform: Java"):
        PlatformDetector.get_platform()
