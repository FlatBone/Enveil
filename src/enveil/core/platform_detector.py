import platform

class PlatformDetector:
    @staticmethod
    def get_platform() -> str:
        return platform.system()

    @staticmethod
    def is_windows() -> bool:
        return platform.system() == "Windows"

    @staticmethod
    def is_linux() -> bool:
        return platform.system() == "Linux"

    @staticmethod
    def is_macos() -> bool:
        return platform.system() == "Darwin"
