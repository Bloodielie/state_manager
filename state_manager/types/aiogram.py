from typing import Union

from aiogram.types import Message, CallbackQuery
from aiogram.types.base import TelegramObject

aiogram_context = Union[Message, CallbackQuery, TelegramObject]
