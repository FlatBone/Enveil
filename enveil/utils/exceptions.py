
class EnveilException(Exception):
    """基底例外クラス"""
    pass

class CommandExecutionError(EnveilException):
    """コマンド実行エラー"""
    pass

class SecurityError(EnveilException):
    """セキュリティ関連エラー"""
    pass

class ConfigurationError(EnveilException):
    """設定エラー"""
    pass

class PlatformNotSupportedError(EnveilException):
    """サポートされていないプラットフォーム"""
    pass
