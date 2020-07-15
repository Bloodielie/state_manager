import asyncio
import functools
import inspect
from typing import Callable, Any, TypeVar

import contextvars

T = TypeVar("T")


def is_coroutine_callable(call: Callable) -> bool:
    if inspect.isroutine(call):
        return inspect.iscoroutinefunction(call)
    if inspect.isclass(call):
        return False
    call = getattr(call, "__call__", None)
    return inspect.iscoroutinefunction(call)


async def check_function_and_run(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    if is_coroutine_callable(func):
        return await func(*args, **kwargs)
    else:
        return await run_in_threadpool(func, *args, **kwargs)


async def run_in_threadpool(
    func: Callable[..., T], *args: Any, **kwargs: Any
) -> T:
    loop = asyncio.get_event_loop()
    if contextvars is not None:
        child = functools.partial(func, *args, **kwargs)
        context = contextvars.copy_context()
        func = context.run
        args = (child,)
    elif kwargs:
        func = functools.partial(func, **kwargs)
    return await loop.run_in_executor(None, func, *args)
