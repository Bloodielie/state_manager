import asyncio
import contextvars
import functools
from typing import Callable, Any, TypeVar

from state_manager.models.state import StateData
from state_manager.storages.base import BaseStorage

T = TypeVar("T")


async def get_state_name(user_id: str, storage: BaseStorage, default: str) -> str:
    user_state = await storage.get(user_id)
    if not user_state:
        user_state = StateData(current_state=default)
        await storage.put(user_id, user_state)
    return user_state.current_state


async def run_in_threadpool(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    loop = asyncio.get_event_loop()
    if contextvars is not None:
        child = functools.partial(func, *args, **kwargs)
        func = contextvars.copy_context().run
        args = (child,)
    elif kwargs:
        func = functools.partial(func, **kwargs)
    return await loop.run_in_executor(None, func, *args)
