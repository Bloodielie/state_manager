from vkwave.bots.addons.easy.base_easy_bot import SimpleBotEvent, BaseSimpleLongPollBot

from state_manager.models.dependencys.base import BaseDependencyStorage, BaseStateManager, back_to_pre_state_
from state_manager.models.state import StateData
from state_manager.types import Data
from logging import getLogger

logger = getLogger(__name__)


class VkWaveStateManager(BaseStateManager):
    context: SimpleBotEvent

    async def set_next_state(self, state_name: str, *, data: Data = None) -> None:
        logger.debug(f"set_next_state, {state_name=}, {data=}")
        state_data = StateData(current_state=state_name, data=data)
        await self.storage.put(str(self.context.object.object.message.from_id), state_data)

    async def back_to_pre_state(self, *, data: Data = None) -> None:
        logger.debug(f"back_to_pre_state, {data=}")
        user_id = str(self.context.object.object.message.from_id)
        await back_to_pre_state_(self.storage, user_id, data)

    @property
    async def data(self) -> Data:
        return (await self._get_state_data()).data

    @property
    async def current_state(self) -> str:
        return (await self._get_state_data()).current_state

    @property
    async def pre_state(self) -> str:
        return (await self._get_state_data()).pre_state

    @property
    async def state_data(self) -> StateData:
        return await self._get_state_data()

    async def _get_state_data(self) -> StateData:
        logger.debug(f"get_storage")
        return await self.storage.get(str(self.context.object.object.message.from_id))

    class Config:
        arbitrary_types_allowed = True


class VkWaveDependencyStorage(BaseDependencyStorage):
    bot: BaseSimpleLongPollBot
    context: SimpleBotEvent

    class Config:
        arbitrary_types_allowed = True
