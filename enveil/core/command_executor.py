import subprocess
from typing import List, Dict
from ..utils.security import SecurityValidator
from ..utils.exceptions import CommandExecutionError, SecurityError

class CommandExecutor:
    def __init__(self, allowed_commands: Dict[str, List[str]] = None):
        self.allowed_commands = allowed_commands if allowed_commands else {}

    def execute(self, command_key: str, params: List[str] = None) -> str:
        if command_key not in self.allowed_commands:
            raise SecurityError(f"Command '{command_key}' is not allowed.")

        command_template = self.allowed_commands[command_key]
        command = command_template

        if params:
            # Simple parameter substitution, assuming the template has placeholders like {0}, {1}
            # For security, we should validate params before substitution
            # This is a simplified version
            try:
                command = command.format(*[self.sanitize_input(p) for p in params])
            except IndexError:
                raise CommandExecutionError("Incorrect number of parameters for command.")

        if not self.is_command_safe(command):
            raise SecurityError(f"Command '{command}' is not safe.")

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise CommandExecutionError(f"Command '{command}' failed with exit code {e.returncode}: {e.stderr.strip()}")
        except FileNotFoundError:
            raise CommandExecutionError(f"Command not found: {command.split()[0]}")

    def is_command_safe(self, command: str) -> bool:
        return SecurityValidator.validate_command(command)

    def sanitize_input(self, input_str: str) -> str:
        # Basic sanitization, remove potentially harmful characters
        # This should be much more robust in a real-world scenario
        return ''.join(c for c in input_str if c.isalnum() or c in ['-', '_', '.'])
