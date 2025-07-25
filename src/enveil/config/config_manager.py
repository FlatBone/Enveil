import json
from pathlib import Path
from typing import Dict, Any

from ..utils.exceptions import ConfigurationError
from .default_software import DEFAULT_SOFTWARE

class ConfigManager:
    """
    設定ファイルの管理を担当します。
    """
    def __init__(self, config_path: str = "config.json"):
        """
        コンストラクタ

        Args:
            config_path (str): 設定ファイルのパス
        """
        self.config_path = Path(config_path)
        self._config = None

    def load_config(self) -> Dict[str, Any]:
        """
        設定ファイルを読み込みます。
        ファイルが存在しない場合はデフォルト設定を返します。

        Returns:
            Dict[str, Any]: 読み込んだ設定

        Raises:
            ConfigurationError: ファイルの読み込みやパースに失敗した場合
        """
        if self._config is not None:
            return self._config

        if not self.config_path.exists():
            self._config = self._get_default_config()
            return self._config

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            # ここでスキーマ検証を将来的に追加
            self._config = config
            return self._config
        except json.JSONDecodeError:
            raise ConfigurationError(f"設定ファイル '{self.config_path}' は不正なJSON形式です。")
        except Exception as e:
            raise ConfigurationError(f"設定ファイル '{self.config_path}' の読み込みに失敗しました: {e}")

    def get_software_commands(self) -> Dict[str, str]:
        """
        チェック対象のソフトウェアとコマンドの辞書を取得します。

        Returns:
            Dict[str, str]: ソフトウェア名と実行コマンドのマッピング
        """
        config = self.load_config()
        return config.get("software", self._get_default_config()["software"])

    def _get_default_config(self) -> Dict[str, Any]:
        """
        デフォルトの設定を生成します。
        """
        return {
            "software": DEFAULT_SOFTWARE,
            "security": {
                "allowed_command_patterns": [
                    f"^{cmd.split(' ')[0]} --version$" for cmd in DEFAULT_SOFTWARE.values()
                ]
            }
        }
