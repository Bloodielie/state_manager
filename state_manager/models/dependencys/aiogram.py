from aiogram import Bot, Dispatcher
from aiogram.types.base import TelegramObject

from state_manager.models.dependencys.base import BaseDependencyStorage, back_to_pre_state_, BaseStateManager
from state_manager.models.state import StateData
from state_manager.types import Context, Data


class AiogramStateManager(BaseStateManager):
    context: Context

    async def set_next_state(self, state_name: str, *, data: Data = None) -> None:
        state_data = StateData(current_state=state_name, data=data)
        await self.storage.put(self.context.from_user.id, state_data)

    async def back_to_pre_state(self, *, data: Data = None) -> None:
        await back_to_pre_state_(self.storage, self.context.from_user.id, data)

    @property
    async def get_data(self) -> Data:
        return (await self._get_storage()).data

    @property
    async def get_storage(self) -> StateData:
        return await self._get_storage()

    async def _get_storage(self) -> StateData:
        return await self.storage.get(self.context.from_user.id)

    class Config:
        arbitrary_types_allowed = True


class AiogramDependencyStorage(BaseDependencyStorage):
    bot: Bot
    dispatcher: Dispatcher
    context: TelegramObject

    class Config:
        arbitrary_types_allowed = True
