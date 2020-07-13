from typing import Union, Optional
from aiogram.types import Message, CallbackQuery
from aiogram.types.base import TelegramObject

Context = Union[Message, CallbackQuery, TelegramObject]
Data = Optional[Union[dict, str, int, bool]]
AnyText = Union[tuple, list, str]
