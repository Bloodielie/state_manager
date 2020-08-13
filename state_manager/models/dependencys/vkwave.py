from logging import getLogger
from typing import Optional

from vkwave.bots.addons.easy.base_easy_bot import SimpleBotEvent

from state_manager.models.dependencys.base import BaseStateManager, back_to_pre_state_
from state_manager.models.state import StateData
from state_manager.types import Data

logger = getLogger(__name__)


class VkWaveStateManager(BaseStateManager):
    context: SimpleBotEvent

    async def set_next_state(self, state_name: str, *, data: Data = None) -> None:
        logger.debug(f"set_next_state, state_name={state_name}, data={data}")
        state_data = StateData(current_state=state_name, data=data)
        await self.storage.put(str(self.context.object.object.message.from_id), state_data)

    async def back_to_pre_state(self, *, data: Data = None) -> None:
        logger.debug(f"back_to_pre_state, data{data}")
        user_id = str(self.context.object.object.message.from_id)
        await back_to_pre_state_(self.storage, user_id, data)

    async def _get_state_data(self) -> Optional[StateData]:
        logger.debug(f"get_storage")
        return await self.storage.get(str(self.context.object.object.message.from_id))

    class Config:
        arbitrary_types_allowed = True
