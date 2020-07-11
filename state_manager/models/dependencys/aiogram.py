from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.types.base import TelegramObject

from state_manager.models.dependencys.base import BaseDependencyStorage, back_to_pre_state_, BaseStateManager
from state_manager.models.state import StateData
from state_manager.types import Context


class AiogramStateManager(BaseStateManager):
    context: Context

    async def set_next_state(self, state_name: str, *, data: Optional[dict] = None) -> None:
        state_data = StateData(current_state=state_name, data=data)
        await self.storage.put(self.context.from_user.id, state_data)

    async def back_to_pre_state(self, *, data: Optional[dict] = None) -> None:
        user_id = self.context.from_user.id
        await back_to_pre_state_(self.storage, user_id, data)

    class Config:
        arbitrary_types_allowed = True


class AiogramDependencyStorage(BaseDependencyStorage):
    bot: Bot
    dispatcher: Dispatcher
    context: TelegramObject
    state_manager: Optional[AiogramStateManager] = None

    class Config:
        arbitrary_types_allowed = True
