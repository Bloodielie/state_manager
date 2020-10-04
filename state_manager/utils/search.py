from logging import getLogger
from typing import Callable, Optional, Union, Any

from state_manager.dependency.container import ContainerWrapper
from state_manager.dependency.dependency import get_func_attributes
from state_manager.filters.base import BaseFilter
from state_manager.storages.state_storage import StateStorage
from state_manager.utils.check import check_filter_result
from state_manager.utils.runers import check_function_and_run

logger = getLogger(__name__)

all_state_name = "*"


async def run_filter(filter_: Union[Callable[..., Any], BaseFilter], dependency_storage: ContainerWrapper,) -> bool:
    if isinstance(filter_, BaseFilter):
        filter_attr = await get_func_attributes(filter_.check, dependency_storage)
        return check_filter_result(await check_function_and_run(filter_.check, **filter_attr))

    filter_attr = await get_func_attributes(filter_, dependency_storage)
    return check_filter_result(await check_function_and_run(filter_, **filter_attr))


async def get_state_handler(
    state_storage: StateStorage, dependency_container: ContainerWrapper, state_name: str, event_type: str,
) -> Optional[Optional[..., Any]]:
    for state_model in state_storage.get_state(event_type, [all_state_name, state_name]):
        if state_model.filters is None:
            return state_model.handler

        for filter_ in state_model.filters:
            filter_result = await run_filter(filter_, dependency_container)
            if filter_result:
                return state_model.handler


async def get_state_handler_and_run(
    state_storage: StateStorage, dependency_container: ContainerWrapper, state_name: str, event_type: str
) -> Any:
    callback = await get_state_handler(state_storage, dependency_container, state_name, event_type)
    if callback is not None:
        func_attr = await get_func_attributes(callback, dependency_container)
        return await check_function_and_run(callback, **func_attr)
