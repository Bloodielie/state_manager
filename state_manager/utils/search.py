from asyncio import iscoroutinefunction
from typing import Callable, Optional, Set

from state_manager.models.dependency import DependencyManager
from state_manager.storage.state_storage import StateStorage
from state_manager.utils.dependency import get_func_attributes


async def search_handler_in_routes(routes: Set["StateRouter"], search_func: Callable) -> Optional[Callable]:
    if not isinstance(routes, set):
        return None
    for router in routes:
        if handler := await search_func(router.state_storage):
            return handler
        if handler := await search_handler_in_routes(router.routers, search_func):
            return handler


async def handler_search(
    dependency_manager: DependencyManager, event_type: str, state_name: str, state_storage: StateStorage
) -> Optional[Callable]:
    states = state_storage.get_state(event_type, state_name)
    if states is None:
        return None
    for state in states:
        if state.filters is None:
            return state.handler
        for filter in state.filters:
            filter_attr = await get_func_attributes(filter, dependency_manager)
            if iscoroutinefunction(filter):
                result = False
            else:
                result = filter(**filter_attr)
            if not result:
                continue
            return state.handler
