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
                # この部分は未実装のため、基本的な情報を返す
                return {"OS": self.executor.execute("get_os_linux")}
            elif self.platform_detector.is_macos():
                # この部分は未実装のため、基本的な情報を返す
                return {"OS": self.executor.execute("get_os_macos")}
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
