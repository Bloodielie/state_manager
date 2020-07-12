import asyncio
import functools
from asyncio import iscoroutinefunction
from typing import Callable, Any


async def check_function_and_run(func: Callable, *args: Any, **kwargs: Any):
    if iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        func_ = functools.partial(func, *args, **kwargs)
        return await asyncio.get_event_loop().run_in_executor(None, func_)
