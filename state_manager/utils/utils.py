import contextvars
from typing import TypeVar, Type

from state_manager.models.state import StateData
from state_manager.storages.base import BaseStorage

T = TypeVar("T")


async def get_state_name(user_id: str, storage: BaseStorage, default: str) -> str:
    """Get the name of the state in the storage."""
    user_state = await storage.get(user_id)
    if not user_state:
        user_state = StateData(current_state=default)
        await storage.put(user_id, user_state)
    return user_state.current_state


class ContextInstanceMixin:
    def __init_subclass__(cls, **kwargs):
        cls.__context_instance = contextvars.ContextVar(f"instance_{cls.__name__}")
        return cls

    @classmethod
    def get_current(cls: Type[T], no_error=True) -> T:
        if no_error:
            return cls.__context_instance.get(None)
        return cls.__context_instance.get()

    @classmethod
    def set_current(cls: Type[T], value: T):
        if not isinstance(value, cls):
            raise TypeError(f"Value should be instance of {cls.__name__!r} not {type(value).__name__!r}")
        cls.__context_instance.set(value)
