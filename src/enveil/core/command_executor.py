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

        command_string = self.allowed_commands[command_key]

        # Validate the entire command string first
        if not SecurityValidator.is_command_safe(command_string):
            raise SecurityError(f"Command '{command_string}' contains unsafe patterns.")

        commands_to_try = [cmd.strip() for cmd in command_string.split('||')]

        for command in commands_to_try:
            # Individual command parts should also be safe, although the main check is above
            if not SecurityValidator.is_command_safe(command):
                 raise SecurityError(f"Command part '{command}' contains unsafe patterns.")

            try:
                # shell=True is a risk, but we rely on is_command_safe
                result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False, timeout=15)
                
                # If command was successful (exit code 0) and produced output
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
                # Also handle commands that print to stderr (like `python --version`)
                elif result.returncode == 0 and result.stderr.strip():
                    return result.stderr.strip()
                # Continue to the next command if this one fails
                
            except subprocess.TimeoutExpired:
                # If one command times out, try the next
                continue
            except Exception:
                # If one command has an unexpected error, try the next
                continue
        
        # If all commands failed, raise an error
        raise CommandExecutionError(f"All commands for '{command_key}' failed or produced no output.")
