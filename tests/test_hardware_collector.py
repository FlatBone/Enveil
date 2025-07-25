import pytest
from unittest.mock import MagicMock, patch
from src.enveil.collectors.hardware_collector import HardwareCollector
from src.enveil.core.command_executor import CommandExecutor

# --- Mock Data --- #
WINDOWS_RAW_CPU = "Name: Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz"
WINDOWS_RAW_RAM = "16.0"
WINDOWS_RAW_GPU = "NVIDIA GeForce RTX 3080 (8GB)"

LINUX_RAW_CPU = "  Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz"
LINUX_RAW_RAM = "16G"
LINUX_RAW_GPU = "NVIDIA GeForce RTX 3080"

# --- Test Cases --- #

@patch('src.enveil.core.platform_detector.PlatformDetector.is_windows', return_value=True)
def test_hardware_collector_windows(mock_is_windows):
    """Windows環境でのハードウェア情報収集をテスト"""
    # Mock CommandExecutor
    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.side_effect = {
        "get_cpu_windows": WINDOWS_RAW_CPU,
        "get_ram_windows": WINDOWS_RAW_RAM,
        "get_gpu_windows": WINDOWS_RAW_GPU,
    }.get

    # Collectorの実行
    collector = HardwareCollector(mock_executor)
    result = collector.collect()

    # 結果の検証
    assert result['CPU'] == "Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz"
    assert result['RAM'] == "16.0GB"
    assert result['GPU'] == "NVIDIA GeForce RTX 3080 (8GB)"
    assert mock_executor.execute.call_count == 3

@patch('src.enveil.core.platform_detector.PlatformDetector.is_windows', return_value=False)
def test_hardware_collector_linux(mock_is_windows):
    """Linux環境でのハードウェア情報収集をテスト"""
    # Mock CommandExecutor
    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.side_effect = {
        "get_cpu_linux": LINUX_RAW_CPU,
        "get_ram_linux": LINUX_RAW_RAM,
        "get_gpu_linux": LINUX_RAW_GPU,
    }.get

    # Collectorの実行
    collector = HardwareCollector(mock_executor)
    result = collector.collect()

    # 結果の検証
    assert result['CPU'] == "Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz"
    assert result['RAM'] == "16G"
    assert result['GPU'] == "NVIDIA GeForce RTX 3080"
    assert mock_executor.execute.call_count == 3

def test_hardware_collector_command_failure():
    """コマンド実行が失敗した場合のテスト"""
    # Mock CommandExecutor
    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.side_effect = Exception("Command failed")

    # Collectorの実行
    collector = HardwareCollector(mock_executor)
    result = collector.collect()

    # 結果の検証
    assert result['CPU'] == "N/A"
    assert result['RAM'] == "N/A"
    assert result['GPU'] == "N/A"
