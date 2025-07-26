import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from .default_software import DEFAULT_SOFTWARE
from ..core.platform_detector import PlatformDetector
from ..utils.exceptions import ConfigurationError
from ..utils.security import SecurityValidator

class ConfigManager:
    """
    設定ファイルの管理を担当します。
    """
    def __init__(self, force_default: bool = False):
        """
        コンストラクタ

        Args:
            force_default (bool): Trueの場合、ファイルの存在を無視してデフォルト設定を強制します。
        """
        self.force_default = force_default
        self._config: Optional[Dict[str, Any]] = None
        self.config_path: Optional[Path] = self.find_config_file()

    def _get_config_paths(self) -> List[Path]:
        """設定ファイルの探索パス候補をリストで返します。"""
        paths = [Path.cwd() / "config.json"]
        
        if PlatformDetector.is_windows():
            appdata = Path.home() / "AppData" / "Local"
            paths.append(appdata / "enveil" / "config.json")
        else: # Linux/macOS
            paths.append(Path.home() / ".config" / "enveil" / "config.json")
            
        return paths

    def find_config_file(self) -> Optional[Path]:
        """有効な設定ファイルを探索し、そのパスを返します。"""
        for path in self._get_config_paths():
            if path.exists() and path.is_file():
                return path
        return None

    def load_config(self) -> Dict[str, Any]:
        """
        設定ファイルを読み込み、検証します。
        ファイルが存在しない場合はデフォルト設定を返します。
        """
        if self._config is not None:
            return self._config

        if self.force_default or not self.config_path:
            self._config = self._get_default_config()
            return self._config
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self._validate_config(config)
            self._config = config
            return self._config
        except json.JSONDecodeError:
            raise ConfigurationError(f"設定ファイル '{self.config_path}' は不正なJSON形式です。")
        except Exception as e:
            raise ConfigurationError(f"設定ファイル '{self.config_path}' の読み込みまたは検証に失敗しました: {e}")

    def _validate_config(self, config: Dict[str, Any]):
        """
        設定ファイルのスキーマと内容を検証します。
        古い形式（文字列）と新しい形式（オブジェクト）の両方に対応します。
        """
        if "software" not in config or not isinstance(config["software"], dict):
            raise ConfigurationError("設定ファイルの'software'セクションが不正です。辞書形式である必要があります。")

        for name, value in config["software"].items():
            command_str = ""
            if isinstance(value, str):
                # 古い形式: "Git": "git --version"
                command_str = value
            elif isinstance(value, dict) and "command" in value:
                # 新しい形式: "Git": { "command": "git --version" }
                command_str = value["command"]
            else:
                raise ConfigurationError(f"ソフトウェア '{name}' の定義が不正です。文字列、または'command'キーを持つオブジェクトである必要があります。")

            if not isinstance(command_str, str) or not command_str:
                raise ConfigurationError(f"ソフトウェア '{name}' のコマンドが空または文字列ではありません。")
            if not SecurityValidator.is_command_safe(command_str):
                raise ConfigurationError(f"ソフトウェア '{name}' のコマンド '{command_str}' はセキュリティ上許可されていません。")

    def get_software_commands(self) -> Dict[str, str]:
        """
        チェック対象のソフトウェアとコマンドの辞書を取得します。
        古い形式と新しい形式の両方に対応します。
        """
        config = self.load_config()
        software_config = config.get("software", {})
        commands = {}
        for name, value in software_config.items():
            if isinstance(value, str):
                commands[name] = value
            elif isinstance(value, dict) and "command" in value:
                commands[name] = value["command"]
        return commands


    def _get_default_config(self) -> Dict[str, Any]:
        """
        デフォルトの設定を生成します。
        """
        # The default config uses the newer, more explicit object format.
        default_software_structured = {
            name: {"command": command} for name, command in DEFAULT_SOFTWARE.items()
        }
        
        return {
            "software": default_software_structured,
            "security": {
                "allowed_command_patterns": [
                    f"^{cmd.split(' ')[0]} --version$" for cmd in DEFAULT_SOFTWARE.values()
                ]
            }
        }