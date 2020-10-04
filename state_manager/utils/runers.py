import asyncio
import contextvars
import functools
from typing import Callable, Any, TypeVar, Union, Awaitable

from state_manager.utils.check import is_coroutine_callable

T = TypeVar("T")


async def check_function_and_run(
    func: Union[Callable[..., T], Callable[..., Awaitable[T]]], *args: Any, **kwargs: Any
) -> T:
    if is_coroutine_callable(func):
        return await func(*args, **kwargs)
    return await run_in_threadpool(func, *args, **kwargs)


async def run_in_threadpool(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Runs a callable object in the threadpool and waits for it."""
    loop = asyncio.get_event_loop()
    if contextvars is not None:
        child = functools.partial(func, *args, **kwargs)
        func = contextvars.copy_context().run
        args = (child,)
    elif kwargs:
        func = functools.partial(func, **kwargs)
    return await loop.run_in_executor(None, func, *args)
