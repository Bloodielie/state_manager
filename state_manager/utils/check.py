from asyncio import iscoroutinefunction
from typing import Callable, Any


async def check_function_and_run(func: Callable, *args: Any, **kwargs: Any):
    if iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)
