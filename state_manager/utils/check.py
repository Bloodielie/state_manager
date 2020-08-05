import inspect
from typing import Callable, Any, TypeVar

from state_manager.utils.utils import run_in_threadpool

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


def is_factory(obj) -> bool:
    return getattr(obj, "is_factory", False)
