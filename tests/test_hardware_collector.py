import pytest
from unittest.mock import MagicMock, patch
from src.enveil.collectors.hardware_collector import HardwareCollector
from src.enveil.core.command_executor import CommandExecutor
from src.enveil.utils.exceptions import CommandExecutionError

# --- Mock Data --- #
WINDOWS_RAW_CPU = "Name=Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz"
WINDOWS_RAW_RAM = """
Capacity
17179869184
"""
# WMICの4GBの壁を再現するデータ
WINDOWS_RAW_GPU_WMIC = "Node,Name,AdapterRAM\nMY-PC,NVIDIA GeForce RTX 5070,4294967295"

# nvidia-smiからの正常な出力を模倣するデータ
NVIDIA_SMI_NAME = "NVIDIA GeForce RTX 5070"
NVIDIA_SMI_MEM_MIB = "12288"  # 12GB in MiB

LINUX_RAW_CPU = "  Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz"
LINUX_RAW_RAM = "16G"
LINUX_RAW_GPU = "NVIDIA GeForce RTX 3080"


# --- Test Cases --- #

@patch('src.enveil.core.platform_detector.PlatformDetector.is_windows', return_value=True)
def test_hardware_collector_windows_nvidia_smi_success(mock_is_windows):
    """【Windows】nvidia-smiが成功した場合のテスト"""
    mock_executor = MagicMock(spec=CommandExecutor)
    
    def mock_execute(command_key):
        if command_key == "get_cpu_windows": return WINDOWS_RAW_CPU
        if command_key == "get_ram_windows": return WINDOWS_RAW_RAM
        if command_key == "get_gpu_name_nvidia": return NVIDIA_SMI_NAME
        if command_key == "get_gpu_mem_nvidia": return NVIDIA_SMI_MEM_MIB
        # wmicのGPUコマンドは呼ばれないはず
        if command_key == "get_gpu_windows": raise AssertionError("wmic should not be called")
        raise CommandExecutionError(f"Command '{command_key}' failed.")

    mock_executor.execute.side_effect = mock_execute

    collector = HardwareCollector(mock_executor)
    result = collector.collect()

    assert result['CPU'] == "Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz"
    assert result['RAM'] == "16.0GB"
    assert result['GPU'] == "NVIDIA GeForce RTX 5070 (12.0GB)"
    # get_gpu_windowsが呼ばれていないことを確認
    assert mock_executor.execute.call_count == 4


@patch('src.enveil.core.platform_detector.PlatformDetector.is_windows', return_value=True)
def test_hardware_collector_windows_wmic_fallback(mock_is_windows):
    """【Windows】nvidia-smiが失敗し、wmicにフォールバックするテスト"""
    mock_executor = MagicMock(spec=CommandExecutor)
    
    def mock_execute(command_key):
        if command_key == "get_cpu_windows": return WINDOWS_RAW_CPU
        if command_key == "get_ram_windows": return WINDOWS_RAW_RAM
        # nvidia-smiは失敗させる
        if command_key in ["get_gpu_name_nvidia", "get_gpu_mem_nvidia"]:
            raise CommandExecutionError("nvidia-smi not found")
        # wmicは成功させる
        if command_key == "get_gpu_windows": return WINDOWS_RAW_GPU_WMIC
        raise CommandExecutionError(f"Command '{command_key}' failed.")

    mock_executor.execute.side_effect = mock_execute

    collector = HardwareCollector(mock_executor)
    result = collector.collect()

    assert result['CPU'] == "Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz"
    assert result['RAM'] == "16.0GB"
    # wmicの4GB制限下の出力を検証
    assert result['GPU'] == "NVIDIA GeForce RTX 5070 (4.0GB)"
    assert mock_executor.execute.call_count == 4


@patch('src.enveil.core.platform_detector.PlatformDetector.is_windows', return_value=True)
def test_hardware_collector_windows_all_gpu_fail(mock_is_windows):
    """【Windows】nvidia-smiとwmicの両方が失敗した場合のテスト"""
    mock_executor = MagicMock(spec=CommandExecutor)
    
    def mock_execute(command_key):
        if command_key == "get_cpu_windows": return WINDOWS_RAW_CPU
        if command_key == "get_ram_windows": return WINDOWS_RAW_RAM
        # すべてのGPUコマンドを失敗させる
        if command_key.startswith("get_gpu"):
            raise CommandExecutionError("All GPU commands failed")
        return ""

    mock_executor.execute.side_effect = mock_execute

    collector = HardwareCollector(mock_executor)
    result = collector.collect()

    assert result['GPU'] == "N/A"


@patch('src.enveil.core.platform_detector.PlatformDetector.is_windows', return_value=False)
def test_hardware_collector_linux(mock_is_windows):
    """Linux環境でのハードウェア情報収集をテスト"""
    mock_executor = MagicMock(spec=CommandExecutor)
    
    def mock_execute(command_key):
        if command_key == "get_cpu_linux": return LINUX_RAW_CPU
        if command_key == "get_ram_linux": return LINUX_RAW_RAM
        if command_key == "get_gpu_linux": return LINUX_RAW_GPU
        return ""

    mock_executor.execute.side_effect = mock_execute

    collector = HardwareCollector(mock_executor)
    result = collector.collect()

    assert result['CPU'] == "Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz"
    assert result['RAM'] == "16G"
    assert result['GPU'] == "NVIDIA GeForce RTX 3080"
    assert mock_executor.execute.call_count == 3