from logging import getLogger
from typing import Callable, Optional, Union, Any

from state_manager.filters.base import BaseFilter
from state_manager.storages.state_storage import StateStorage
from state_manager.types.generals import BaseContainer
from state_manager.utils.check import check_filter_result
from state_manager.utils.runers import check_function_and_run

logger = getLogger(__name__)

all_state_name = "*"


async def run_filter(filter_: Union[Callable[..., Any], BaseFilter], dependency_container: BaseContainer, ) -> bool:
    if isinstance(filter_, BaseFilter):
        attr = dependency_container.get_target_attributes(filter_.check)
        return await check_function_and_run(filter_.check, **attr)
    attr = dependency_container.get_target_attributes(filter_)
    return check_filter_result(await check_function_and_run(filter_, **attr))


async def get_state_handler(
    state_storage: StateStorage, dependency_container: BaseContainer, state_name: str, event_type: str,
) -> Optional[Callable[..., Any]]:
    for state_model in state_storage.get_state(event_type, [all_state_name, state_name]):
        if state_model.filters is None:
            return state_model.handler

        for filter_ in state_model.filters:
            filter_result = await run_filter(filter_, dependency_container)
            if filter_result:
                return state_model.handler


async def get_state_handler_and_run(
    state_storage: StateStorage, dependency_container: BaseContainer, state_name: str, event_type: str
) -> Any:
    callback = await get_state_handler(state_storage, dependency_container, state_name, event_type)
    if callback is not None:
        attr = dependency_container.get_target_attributes(callback)
        return await check_function_and_run(callback, **attr)
