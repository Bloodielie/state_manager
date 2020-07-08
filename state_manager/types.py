from typing import Union
from aiogram.types import Message, CallbackQuery
from aiogram.types.base import TelegramObject

Context = Union[Message, CallbackQuery, TelegramObject]
