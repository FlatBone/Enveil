import pytest
from enveil.utils.exceptions import (
    EnveilException,
    CommandExecutionError,
    SecurityError,
    ConfigurationError,
    PlatformNotSupportedError
)

def test_enveil_exception():
    """EnveilExceptionが正しく送出されるかテストする"""
    with pytest.raises(EnveilException, match="汎用的なエラー"):
        raise EnveilException("汎用的なエラー")

def test_command_execution_error():
    """CommandExecutionErrorが正しく送出されるかテストする"""
    with pytest.raises(CommandExecutionError, match="コマンド実行エラー"):
        raise CommandExecutionError("コマンド実行エラー")

def test_security_error():
    """SecurityErrorが正しく送出されるかテストする"""
    with pytest.raises(SecurityError, match="セキュリティエラー"):
        raise SecurityError("セキュリティエラー")

def test_configuration_error():
    """ConfigurationErrorが正しく送出されるかテストする"""
    with pytest.raises(ConfigurationError, match="設定エラー"):
        raise ConfigurationError("設定エラー")

def test_platform_not_supported_error():
    """PlatformNotSupportedErrorが正しく送出されるかテストする"""
    with pytest.raises(PlatformNotSupportedError, match="プラットフォーム非対応エラー"):
        raise PlatformNotSupportedError("プラットフォーム非対応エラー")
