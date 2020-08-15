from typing import Union, Optional
from aiogram.types import Message, CallbackQuery
from aiogram.types.base import TelegramObject

from state_manager.dependency.container import AppContainer, ContainerWrapper

aiogram_context = Union[Message, CallbackQuery, TelegramObject]
Data = Optional[Union[dict, str, int, bool]]
AnyText = Union[tuple, list, str]
Container = Union[AppContainer, ContainerWrapper]
