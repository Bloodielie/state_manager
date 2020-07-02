from typing import Union, Callable, Any
from aiogram.types import Message, CallbackQuery

Context = Union[Message, CallbackQuery]

Dumper = Callable[[Any], str]
Loader = Callable[[str], Any]
