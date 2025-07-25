import re

class SecurityValidator:
    # シェルメタ文字、リダイレクト、ディレクトリトラバーサル、危険なコマンド
    BLOCKED_PATTERNS = [
        r'[;&|`$()><]', 
        r'\.\./',
        r'\brm\s+',
        r'\bdel\s+'
    ]
    
    @classmethod
    def is_command_safe(cls, command: str) -> bool:
        """コマンドが安全なパターンに一致するかを検証します。"""
        for pattern in cls.BLOCKED_PATTERNS:
            if re.search(pattern, command):
                return False
        return True