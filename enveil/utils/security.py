import re

class SecurityValidator:
    BLOCKED_PATTERNS = [
        r'[;&|`$()]',  # シェルメタ文字
        r'\.\./',      # ディレクトリトラバーサル
        r'rm\s+',      # 危険なコマンド
        r'del\s+',     # 危険なコマンド
    ]
    
    @classmethod
    def validate_command(cls, command: str) -> bool:
        for pattern in cls.BLOCKED_PATTERNS:
            if re.search(pattern, command):
                return False
        return True
