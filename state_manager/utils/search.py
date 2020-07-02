from typing import Callable, Optional, Set

from state_manager.storage.state_storage import StateStorage
from state_manager.types import Context


def search_handler_in_routes(routes: Set["StateRouter"], search_func: Callable) -> Optional[Callable]:
    if not isinstance(routes, set):
        return None
    for router in routes:
        if handler := search_func(router.state_storage):
            return handler
        if handler := search_handler_in_routes(router.routers, search_func):
            return handler


def handler_search(ctx: Context, event_type: str, state_name: str, state_storage: StateStorage) -> Optional[Callable]:
    if states := state_storage.get_state(event_type, state_name):
        for state in states:
            if state.filter is None:
                return state.handler
            if not state.filter(ctx):
                continue
            return state.handler
    return None
