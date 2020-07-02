from typing import Callable, Optional, Set

from aiogram.types.base import TelegramObject

from state_manager.storage.state_storage import StateStorage


def search_handler_in_routes(routes: Set["StateRouter"], search_func: Callable) -> Optional[Callable]:
    if not isinstance(routes, set):
        return None
    for router in routes:
        if handler := search_func(router.state_storage):
            return handler
        if handler := search_handler_in_routes(router.routers, search_func):
            return handler


def handler_search(ctx: TelegramObject, event_type: str, state_name: str, state_storage: StateStorage) -> Optional[Callable]:
    for state in state_storage.get_state(event_type, state_name):
        if state.filter is None:
            return state.handler
        if not state.filter(ctx):
            continue
        return state.handler
