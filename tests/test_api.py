import pytest
import time
from unittest.mock import MagicMock, patch
from src.enveil.api import EnveilAPI

# --- Mock Data --- #
HARDWARE_INFO = {'CPU': 'Intel i9', 'RAM': '32GB'}
OS_INFO = {'OS': 'Windows 11'}
SOFTWARE_INFO = {'Python': '3.10', 'Git': '2.35'}

@pytest.fixture
def mock_collectors():
    """各コレクターのモックを作成"""
    with (patch('src.enveil.api.HardwareCollector') as mock_hw,
          patch('src.enveil.api.OSCollector') as mock_os,
          patch('src.enveil.api.SoftwareCollector') as mock_sw):
        
        mock_hw.return_value.collect.return_value = HARDWARE_INFO
        mock_os.return_value.collect.return_value = OS_INFO
        mock_sw.return_value.collect.return_value = SOFTWARE_INFO
        
        yield mock_hw, mock_os, mock_sw

def test_get_all_info_sequential(mock_collectors):
    """すべての情報を順次取得するテスト"""
    api = EnveilAPI()
    result = api.get_all_info(parallel=False)

    assert result['hardware'] == HARDWARE_INFO
    assert result['os'] == OS_INFO
    assert result['software'] == SOFTWARE_INFO

def test_get_all_info_parallel(mock_collectors):
    """すべての情報を並列取得するテスト"""
    api = EnveilAPI()
    result = api.get_all_info(parallel=True)

    assert result['hardware'] == HARDWARE_INFO
    assert result['os'] == OS_INFO
    assert result['software'] == SOFTWARE_INFO

def test_get_all_info_timeout(mock_collectors):
    """情報収集がタイムアウトするテスト"""
    mock_hw, _, _ = mock_collectors
    def slow_collect():
        time.sleep(0.2)
        return HARDWARE_INFO
    mock_hw.return_value.collect.side_effect = slow_collect

    api = EnveilAPI()
    result = api.get_all_info(parallel=True, timeout=0.1)

    assert "timed out" in result['hardware']
    assert result['os'] == OS_INFO
    assert result['software'] == SOFTWARE_INFO

def test_get_hardware_info(mock_collectors):
    """ハードウェア情報のみを取得するテスト"""
    api = EnveilAPI()
    result = api.get_hardware_info()
    
    assert result == HARDWARE_INFO
    assert mock_collectors[0].return_value.collect.call_count == 1
    assert mock_collectors[1].return_value.collect.call_count == 0
    assert mock_collectors[2].return_value.collect.call_count == 0

def test_get_os_info(mock_collectors):
    """OS情報のみを取得するテスト"""
    api = EnveilAPI()
    result = api.get_os_info()
    
    assert result == OS_INFO
    assert mock_collectors[0].return_value.collect.call_count == 0
    assert mock_collectors[1].return_value.collect.call_count == 1
    assert mock_collectors[2].return_value.collect.call_count == 0

def test_get_software_info(mock_collectors):
    """ソフトウェア情報のみを取得するテスト"""
    api = EnveilAPI()
    result = api.get_software_info()
    
    assert result == SOFTWARE_INFO
    assert mock_collectors[0].return_value.collect.call_count == 0
    assert mock_collectors[1].return_value.collect.call_count == 0
    assert mock_collectors[2].return_value.collect.call_count == 1

def test_get_software_info_with_list(mock_collectors):
    """特定のソフトウェア情報のみを取得するテスト"""
    mock_sw_instance = mock_collectors[2].return_value
    api = EnveilAPI()
    api.get_software_info(software_list=['Python'])
    
    mock_sw_instance.collect.assert_called_once_with(software_list=['Python'])


# --- Integration Tests (No Mocks) --- #

# 現在のプラットフォームがWindowsかどうかを判定
is_windows = 'win32' in __import__('sys').platform

@pytest.mark.integration
@pytest.mark.skipif(not is_windows, reason="Windows-specific integration test")
def test_integration_get_hardware_info_on_windows():
    """【統合テスト】Windowsでハードウェア情報を実際に取得する"""
    api = EnveilAPI()
    hardware_info = api.get_hardware_info()

    assert hardware_info is not None
    assert isinstance(hardware_info, dict)
    assert "CPU" in hardware_info
    assert "RAM" in hardware_info
    assert "GPU" in hardware_info
    assert hardware_info["CPU"] is not None and hardware_info["CPU"] != "N/A"
    assert hardware_info["RAM"] is not None and hardware_info["RAM"] != "N/A"
    # GPUは搭載されていない環境もあるため、存在のみチェック
    assert hardware_info["GPU"] is not None

@pytest.mark.integration
@pytest.mark.skipif(not is_windows, reason="Windows-specific integration test")
def test_integration_get_os_info_on_windows():
    """【統合テスト】WindowsでOS情報を実際に取得する"""
    api = EnveilAPI()
    os_info = api.get_os_info()

    assert os_info is not None
    assert isinstance(os_info, dict)
    assert "OS" in os_info
    assert "Version" in os_info
    assert "Build" in os_info
    assert "Architecture" in os_info
    assert "Windows" in os_info["OS"]

@pytest.mark.integration
@pytest.mark.skipif(not is_windows, reason="Windows-specific integration test")
def test_integration_get_software_info_on_windows():
    """【統合テスト】Windowsでソフトウェア情報を実際に取得する"""
    api = EnveilAPI()
    software_info = api.get_software_info()

    assert software_info is not None
    assert isinstance(software_info, dict)
    # デフォルトでチェックされるソフトウェアのいずれかが含まれていることを確認
    assert "Python" in software_info or "Git" in software_info
    if "Python" in software_info:
        assert software_info["Python"] is not None

