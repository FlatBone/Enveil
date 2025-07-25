from typing import Dict, Any
from .base_collector import BaseCollector
from ..core.command_executor import CommandExecutor
from ..core.platform_detector import PlatformDetector

class OSCollector(BaseCollector):
    """
    OS情報を収集するコレクター。
    """
    def __init__(self, executor: CommandExecutor):
        """
        コンストラクタ

        Args:
            executor (CommandExecutor): コマンド実行を担当するインスタンス
        """
        super().__init__(executor)
        self.platform_detector = PlatformDetector()

    def collect(self) -> Dict[str, Any]:
        """
        OS情報を収集します。

        Returns:
            Dict[str, Any]: 収集したOS情報を含む辞書。
                            例: {'OS': 'Windows 11 Pro'}
        """
        try:
            os_info = self._get_os_info()
            return {"OS": os_info}
        except Exception:
            return {"OS": "N/A"}

    def _get_os_info(self) -> str:
        """
        プラットフォームに応じてOS情報を取得する内部メソッド。
        """
        if self.platform_detector.is_windows():
            return self.executor.execute("get_os_windows")
        elif self.platform_detector.is_linux():
            return self.executor.execute("get_os_linux")
        elif self.platform_detector.is_macos():
            return self.executor.execute("get_os_macos")
        else:
            return "Unsupported OS"
