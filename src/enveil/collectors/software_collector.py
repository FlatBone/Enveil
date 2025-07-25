from typing import Dict, Any, List, Optional

from .base_collector import BaseCollector
from ..core.command_executor import CommandExecutor
from ..config.config_manager import ConfigManager

class SoftwareCollector(BaseCollector):
    """
    インストール済みのソフトウェアバージョン情報を収集します。
    """
    def __init__(self, executor: CommandExecutor, config_manager: ConfigManager):
        """
        コンストラクタ

        Args:
            executor (CommandExecutor): コマンド実行を担当するインスタンス
            config_manager (ConfigManager): 設定管理を担当するインスタンス
        """
        super().__init__(executor)
        self.config_manager = config_manager

    def collect(self, software_list: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        指定された、あるいは設定ファイルに定義されたソフトウェアのバージョン情報を収集します。

        Args:
            software_list (Optional[List[str]]): 収集対象のソフトウェア名のリスト。
                                                 Noneの場合は設定ファイル全体が対象。

        Returns:
            Dict[str, Any]: 収集したソフトウェア情報を含む辞書。
                            例: {'Python': '3.9.1', 'Git': 'N/A'}
        """
        results = {}
        software_commands = self.config_manager.get_software_commands()

        target_software = software_list if software_list is not None else software_commands.keys()

        for name in target_software:
            if name in software_commands:
                try:
                    # The key for execution is the software name itself
                    version = self.executor.execute(name)
                    results[name] = version.strip()
                except Exception:
                    results[name] = "N/A"
        return results
