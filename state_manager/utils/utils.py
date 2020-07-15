from state_manager.models.state import StateData
from state_manager.storage.base import BaseStorage


async def get_user_state_name(user_id: str, storage: BaseStorage, default: str) -> str:
    user_state = await storage.get(user_id)
    if not user_state:
        user_state = StateData(current_state=default)
        await storage.put(user_id, user_state)
    return user_state.current_state
