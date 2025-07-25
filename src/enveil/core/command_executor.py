import subprocess
from typing import List, Dict
from ..utils.security import SecurityValidator
from ..utils.exceptions import CommandExecutionError, SecurityError

class CommandExecutor:
    def __init__(self, allowed_commands: Dict[str, str] = None):
        self.allowed_commands = allowed_commands if allowed_commands else {}

    def execute(self, command_key: str, params: List[str] = None) -> str:
        if command_key not in self.allowed_commands:
            raise SecurityError(f"Command '{command_key}' is not allowed.")

        command = self.allowed_commands[command_key]

        # パラメータ置換は未実装のため、paramsは無視

        if not SecurityValidator.is_command_safe(command):
            raise SecurityError(f"Command '{command}' is not safe.")

        try:
            # shell=Trueはインジェクションのリスクがあるが、is_command_safeで検証済みと想定
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False, timeout=15)
            if result.returncode != 0:
                # コマンドが見つからない場合なども含め、エラーとして扱う
                # ただし、バージョンチェックなどでコマンドがないのは許容したいため、ここでは出力を返す
                return result.stderr.strip()
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            raise CommandExecutionError(f"Command '{command}' timed out.")
        except Exception as e:
            raise CommandExecutionError(f"An unexpected error occurred while executing command '{command}': {e}")
