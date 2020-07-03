from typing import Union, Callable, Any
from aiogram.types import Message, CallbackQuery
from aiogram.types.base import TelegramObject

Context = Union[Message, CallbackQuery, TelegramObject]

Dumper = Callable[[Any], str]
Loader = Callable[[str], Any]
