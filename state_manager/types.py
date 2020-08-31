from typing import Union, Optional, Tuple, Callable, List
from aiogram.types import Message, CallbackQuery
from aiogram.types.base import TelegramObject

from state_manager.dependency.container import AppContainer, ContainerWrapper

aiogram_context = Union[Message, CallbackQuery, TelegramObject]
Data = Optional[Union[dict, str, int, bool]]
AnyText = Union[tuple, list, str]
Container = Union[AppContainer, ContainerWrapper]
Filters = Optional[Tuple[Union[Callable[..., bool], "BaseFilter"]]]
StateNames = Optional[Union[str, List[Optional[str]]]]
