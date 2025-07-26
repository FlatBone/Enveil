from typing import Dict, Any, List, Optional
import concurrent.futures

from .core.command_executor import CommandExecutor
from .config.config_manager import ConfigManager
from .collectors.hardware_collector import HardwareCollector
from .collectors.os_collector import OSCollector
from .collectors.software_collector import SoftwareCollector

class EnveilAPI:
    """
    Enveilライブラリの主要APIを提供します。
    """
    def __init__(self, config_path: Optional[str] = None):
        """
        コンストラクタ

        Args:
            config_path (Optional[str]): カスタム設定ファイルのパス
        """
        self.config_manager = ConfigManager(config_path=config_path) if config_path else ConfigManager()
        config = self.config_manager.load_config()
        
        allowed_commands = self._prepare_allowed_commands(config)
        
        self.executor = CommandExecutor(allowed_commands=allowed_commands)
        
        self.hardware_collector = HardwareCollector(self.executor)
        self.os_collector = OSCollector(self.executor)
        self.software_collector = SoftwareCollector(self.executor, self.config_manager)

    def _prepare_allowed_commands(self, config: Dict[str, Any]) -> Dict[str, str]:
        """コレクターが使用するすべての許可コマンドを準備します。"""
        commands = {
            # HardwareCollector Commands
            "get_cpu_windows": "wmic cpu get name /format:list",
            "get_ram_windows": "wmic memorychip get capacity",
            "get_gpu_windows": "wmic path win32_videocontroller get name,adapterram /format:csv",
            "get_gpu_name_nvidia": "nvidia-smi --query-gpu=name --format=csv,noheader",
            "get_gpu_mem_nvidia": "nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits",
            "get_cpu_linux": "lscpu | grep 'Model name' | sed 's/.*Model name:[^A-Za-z0-9]*//'",
            "get_ram_linux": "free -b | grep Mem | awk '{print $2}'",
            "get_gpu_linux": "lspci | grep -i vga | sed 's/.*controller:[^A-Za-z0-9]*//'",
            "get_cpu_macos": "sysctl -n machdep.cpu.brand_string",
            "get_ram_macos": "sysctl -n hw.memsize",
            "get_gpu_name_macos": "system_profiler SPDisplaysDataType | grep 'Chipset Model' | awk -F': ' '{print $2}'",
            "get_gpu_vram_macos": "system_profiler SPDisplaysDataType | grep 'VRAM' | awk -F': ' '{print $2}' | head -n 1",
            # OSCollector Commands
            "get_os_windows": "wmic os get caption,version,buildnumber,osarchitecture /format:list",
            "get_os_linux": "lsb_release -ds || grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '\"'",
            "get_os_macos": "sw_vers",
        }
        software_cmds = config.get("software", {})
        commands.update(software_cmds)
        return commands

    def get_all_info(self, parallel: bool = True, timeout: int = 30) -> Dict[str, Any]:
        """
        すべてのシステム情報を収集します。

        Args:
            parallel (bool): Trueの場合、並列で情報収集を実行します。
            timeout (int): 各収集処理のタイムアウト（秒）。

        Returns:
            Dict[str, Any]: ハードウェア、OS、ソフトウェア情報を含む辞書
        """
        if not parallel:
            return {
                "hardware": self.get_hardware_info(),
                "os": self.get_os_info(),
                "software": self.get_software_info()
            }

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                'hardware': executor.submit(self.get_hardware_info),
                'os': executor.submit(self.get_os_info),
                'software': executor.submit(self.get_software_info)
            }
            
            results = {}
            for key, future in futures.items():
                try:
                    results[key] = future.result(timeout=timeout)
                except concurrent.futures.TimeoutError:
                    results[key] = f"{key} information collection timed out."
                except Exception as e:
                    results[key] = f"Error collecting {key} info: {e}"
            
            return results

    def get_hardware_info(self) -> Dict[str, str]:
        """
        ハードウェア情報を収集します。
        """
        return self.hardware_collector.collect()

    def get_os_info(self) -> Dict[str, str]:
        """
        OS情報を収集します。
        """
        return self.os_collector.collect()

    def get_software_info(self, software_list: Optional[List[str]] = None) -> Dict[str, str]:
        """
        ソフトウェア情報を収集します。

        Args:
            software_list (Optional[List[str]]): 収集対象のソフトウェアリスト
        """
        return self.software_collector.collect(software_list=software_list)