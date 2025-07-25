import platform
from ..utils.exceptions import PlatformNotSupportedError

class PlatformDetector:
    @staticmethod
    def get_platform() -> str:
        system = platform.system()
        if system == 'Windows':
            return 'windows'
        elif system == 'Linux':
            return 'linux'
        elif system == 'Darwin':
            return 'macos'
        else:
            raise PlatformNotSupportedError(f"Unsupported platform: {system}")

    @staticmethod
    def is_windows() -> bool:
        return platform.system() == "Windows"

    @staticmethod
    def is_linux() -> bool:
        return platform.system() == "Linux"

    @staticmethod
    def is_macos() -> bool:
        return platform.system() == "Darwin"
