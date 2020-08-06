import inspect
from logging import getLogger
from typing import Callable, Any, TypeVar

from state_manager.utils.utils import run_in_threadpool

T = TypeVar("T")

logger = getLogger(__name__)


def is_coroutine_callable(call: Callable) -> bool:
    if inspect.isroutine(call):
        return inspect.iscoroutinefunction(call)
    if inspect.isclass(call):
        return False
    call = getattr(call, "__call__", None)
    return inspect.iscoroutinefunction(call)


async def check_function_and_run(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    if is_coroutine_callable(func):
        return await func(*args, **kwargs)  # type: ignore
    return await run_in_threadpool(func, *args, **kwargs)


def is_factory(object_: Any) -> bool:
    return getattr(object_, "is_factory", False)


def check_filter_result(filter_result: Any) -> bool:
    if isinstance(filter_result, bool):
        return filter_result
    logger.warning(f"Filter return no bool, {filter_result=}")
    return False
