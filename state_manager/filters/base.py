import re
from abc import ABC, abstractmethod

from state_manager.types import AnyText


class BaseFilter(ABC):
    @abstractmethod
    async def check(self, *args, **kwargs) -> bool:  # type: ignore
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"


class BaseTextFilter(BaseFilter):
    def __init__(self, text: AnyText, ignore_case: bool = True) -> None:
        self.text = (text,) if isinstance(text, str) else text
        self.ignore_case = ignore_case


class BaseTextContainsFilter(BaseFilter):
    def __init__(self, text: AnyText, ignore_case: bool = True) -> None:
        self.text = (text,) if isinstance(text, str) else text
        self.ignore_case = ignore_case


class BaseRegexFilter(BaseFilter):
    def __init__(self, regex: str, flags: int = 0) -> None:
        self.pattern = re.compile(regex, flags)
