from abc import ABC, abstractmethod


class BaseEventProcessor(ABC):
    @classmethod
    @abstractmethod
    def install(cls, *args, **kwargs):
        pass
