import pytest
from enveil.core.command_executor import CommandExecutor
from enveil.utils.exceptions import SecurityError, CommandExecutionError

# テスト用の許可されたコマンドリスト
ALLOWED_COMMANDS = {
    "echo_hello": "echo hello",
    "list_files": "ls",
}

# 1. 許可されたコマンドが正常に実行できること
def test_execute_allowed_command():
    executor = CommandExecutor(allowed_commands=ALLOWED_COMMANDS)
    result = executor.execute("echo_hello")
    assert result == "hello"

# 2. 許可されていないコマンドがSecurityErrorを発生させること
def test_execute_disallowed_command():
    executor = CommandExecutor(allowed_commands=ALLOWED_COMMANDS)
    with pytest.raises(SecurityError, match="Command 'delete_all' is not allowed."):
        executor.execute("delete_all")

# 3. 不正なパラメータがCommandExecutionErrorを発生させること
# (このテストは、パラメータ置換を実装した後に有効になります)
@pytest.mark.skip(reason="Parameter substitution not yet implemented")
def test_execute_with_invalid_params():
    pass

# 4. 安全でないコマンドがSecurityErrorを発生させること
def test_execute_unsafe_command():
    unsafe_commands = {
        "unsafe_echo": "echo hello; rm -rf /"
    }
    executor = CommandExecutor(allowed_commands=unsafe_commands)
    with pytest.raises(SecurityError, match="Command 'echo hello; rm -rf /' is not safe."):
        executor.execute("unsafe_echo")
