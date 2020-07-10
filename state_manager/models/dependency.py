from typing import Callable, Optional

from aiogram import Bot, Dispatcher
from aiogram.types.base import TelegramObject
from pydantic import BaseModel

from state_manager.models.state import StateData
from state_manager.storage.base import BaseStorage
from state_manager.types import Context


class StateManager(BaseModel):
    storage: BaseStorage
    context: Context

    async def set_next_state(self, state_name: str, *, data: Optional[dict] = None) -> None:
        state_data = StateData(current_state=state_name, data=data)
        await self.storage.put(self.context.from_user.id, state_data)

    async def back_to_pre_state(self, *, data: Optional[dict] = None) -> None:
        user_id = self.context.from_user.id
        state = await self.storage.get(user_id)
        if state.pre_state is None:
            state_data = StateData(current_state=state.current_state, data=data)
        else:
            state_data = StateData(current_state=state.pre_state, data=data)
        await self.storage.put(user_id, state_data)

    class Config:
        arbitrary_types_allowed = True


class DependencyStorage(BaseModel):
    bot: Bot
    storage: BaseStorage
    dispatcher: Dispatcher
    context: TelegramObject
    state_manager: Optional[StateManager] = None

    class Config:
        arbitrary_types_allowed = True


class Depends:
    def __init__(self, dependency: Callable) -> None:
        self.dependency = dependency

    def __repr__(self) -> str:
        attr = getattr(self.dependency, "__name__", type(self.dependency).__name__)
        return f"{self.__class__.__name__}({attr})"
