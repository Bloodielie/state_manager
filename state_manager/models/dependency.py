from typing import Callable

from aiogram import Bot, Dispatcher
from aiogram.types.base import TelegramObject
from pydantic import BaseModel

from state_manager.storage.base import BaseStorage


class DependencyManager(BaseModel):
    bot: Bot
    storage: BaseStorage
    dispatcher: Dispatcher
    context: TelegramObject

    async def set_scene(self, scene_name: str) -> None:
        await self.storage.put(self.context.from_user.id, scene_name)

    class Config:
        arbitrary_types_allowed = True


class Depends:
    def __init__(self, dependency: Callable) -> None:
        self.dependency = dependency

    def __repr__(self) -> str:
        attr = getattr(self.dependency, "__name__", type(self.dependency).__name__)
        return f"{self.__class__.__name__}({attr})"
