from typing import Dict, Any
from .base_collector import BaseCollector
from ..core.command_executor import CommandExecutor
from ..core.platform_detector import PlatformDetector

class OSCollector(BaseCollector):
    """
    OS情報を収集するコレクター。
    """
    def __init__(self, executor: CommandExecutor):
        super().__init__(executor)
        self.platform_detector = PlatformDetector()

    def collect(self) -> Dict[str, Any]:
        """
        OS情報を収集します。
        """
        try:
            if self.platform_detector.is_windows():
                return self._get_windows_info()
            elif self.platform_detector.is_linux():
                os_str = self.executor.execute("get_os_linux").strip()
                return {"OS": os_str if os_str else "N/A"}
            elif self.platform_detector.is_macos():
                return self._get_macos_info()
            else:
                return {"OS": "Unsupported OS"}
        except Exception:
            return {
                "OS": "N/A",
                "Version": "N/A",
                "Build": "N/A",
                "Architecture": "N/A",
            }

    def _get_windows_info(self) -> Dict[str, str]:
        """Windowsの詳細なOS情報を取得します。"""
        raw_info = self.executor.execute("get_os_windows")
        info = {}
        for line in raw_info.strip().splitlines():
            if not line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key == "Caption":
                info["OS"] = value
            elif key == "Version":
                info["Version"] = value
            elif key == "BuildNumber":
                info["Build"] = value
            elif key == "OSArchitecture":
                info["Architecture"] = value
        return info

    def _get_macos_info(self) -> Dict[str, str]:
        """macOSの詳細なOS情報を取得します。"""
        raw_info = self.executor.execute("get_os_macos")
        info = {}
        for line in raw_info.strip().splitlines():
            if not line:
                continue
            parts = line.split(":", 1)
            if len(parts) == 2:
                key, value = parts
                key = key.strip()
                value = value.strip()
                if key == "ProductName":
                    info["OS"] = value
                elif key == "ProductVersion":
                    info["Version"] = value
                elif key == "BuildVersion":
                    info["Build"] = value
        
        info.setdefault("OS", "N/A")
        info.setdefault("Version", "N/A")
        info.setdefault("Build", "N/A")
        return info