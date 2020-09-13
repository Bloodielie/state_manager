import inspect
from logging import getLogger
from typing import Callable, Any

logger = getLogger(__name__)


def is_coroutine_callable(call: Callable) -> bool:
    if inspect.isroutine(call):
        return inspect.iscoroutinefunction(call)
    if inspect.isclass(call):
        return False
    call = getattr(call, "__call__", None)
    return inspect.iscoroutinefunction(call)


def is_factory(object_: Any) -> bool:
    return getattr(object_, "is_factory", False)


def check_filter_result(filter_result: Any) -> bool:
    if isinstance(filter_result, bool):
        return filter_result
    logger.warning(f"Filter return no bool, filter_result={filter_result}")
    return False
