from state_manager.types import Context
from abc import ABC, abstractmethod


class BaseFilter(ABC):
    @abstractmethod
    def __call__(self, context: Context) -> bool:
        raise NotImplementedError
