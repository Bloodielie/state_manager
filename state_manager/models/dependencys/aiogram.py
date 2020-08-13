from logging import getLogger
from typing import Optional

from state_manager.models.dependencys.base import back_to_pre_state_, BaseStateManager
from state_manager.models.state import StateData
from state_manager.types import Context, Data

logger = getLogger(__name__)


class AiogramStateManager(BaseStateManager):
    context: Context

    async def set_next_state(self, state_name: str, *, data: Data = None) -> None:
        logger.debug(f"set_next_state, state_name={state_name}, data={data}")
        state_data = StateData(current_state=state_name, data=data)
        await self.storage.put(self.context.from_user.id, state_data)

    async def back_to_pre_state(self, *, data: Data = None) -> None:
        logger.debug(f"back_to_pre_state, data={data}")
        await back_to_pre_state_(self.storage, self.context.from_user.id, data)

    async def _get_state_data(self) -> Optional[StateData]:
        logger.debug(f"get_storage")
        return await self.storage.get(self.context.from_user.id)

    class Config:
        arbitrary_types_allowed = True
