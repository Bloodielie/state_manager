from asyncio import iscoroutinefunction
from functools import partial
from typing import Callable, Optional, Set, Dict, Tuple

from state_manager.models.dependency import DependencyStorage
from state_manager.storage.state_storage import StateStorage
from state_manager.utils.dependency import get_func_attributes


class HandlerFinder:
    def __init__(self, main_router: "MainStateRouter", is_cache: bool = False):
        self._main_router = main_router
        self._is_cache = is_cache
        self._handler_in_cache: Dict[Tuple[str, str], Callable] = {} if is_cache else None

    async def get_state_handler(
        self, dependency_storage: DependencyStorage, state_name: str, event_type: str
    ) -> Optional[Callable]:
        if self._is_cache:
            handler = self._handler_in_cache.get((state_name, event_type))
            if handler:
                return handler
        return await self._get_state_handler(dependency_storage, state_name, event_type)

    async def _get_state_handler(
        self, dependency_storage: DependencyStorage, state_name: str, event_type: str
    ) -> Optional[Callable]:
        handler_search = partial(self._handler_search, dependency_storage, event_type, state_name)
        if handler := await handler_search(self._main_router.state_storage):
            if self._is_cache:
                self._handler_in_cache[(state_name, event_type)] = handler
            return handler
        if handler := await self._search_handler_in_routes(self._main_router.routers, handler_search):
            if self._is_cache:
                self._handler_in_cache[(state_name, event_type)] = handler
            return handler

    @staticmethod
    async def _handler_search(
        dependency_manager: DependencyStorage, event_type: str, state_name: str, state_storage: StateStorage
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

    @classmethod
    async def _search_handler_in_routes(cls, routes: Set["StateRouter"], search_func: Callable) -> Optional[Callable]:
        if not isinstance(routes, set):
            return None
        for router in routes:
            if handler := await search_func(router.state_storage):
                return handler
            if handler := await cls._search_handler_in_routes(router.routers, search_func):
                return handler
