from state_manager.models.state import StateData
from state_manager.storages.base import BaseStorage


async def get_state_name(user_id: str, storage: BaseStorage, default: str) -> str:
    """Get the name of the state in the storage."""
    user_state = await storage.get(user_id)
    if not user_state:
        user_state = StateData(current_state=default)
        await storage.put(user_id, user_state)
    return user_state.current_state
