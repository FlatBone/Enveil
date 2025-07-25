from abc import ABC, abstractmethod
from typing import Any, Dict
from ..core.command_executor import CommandExecutor

class BaseCollector(ABC):
    def __init__(self, executor: CommandExecutor):
        self.executor = executor

    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        pass

    def is_available(self) -> bool:
        return True
