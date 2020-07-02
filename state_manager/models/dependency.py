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
