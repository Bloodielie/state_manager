from abc import ABC
from typing import Callable, Optional, Set, Tuple, Any

from state_manager.models.state import StateModel
from state_manager.storage.state_storage import StateStorage
from logging import getLogger

logger = getLogger(__name__)


class BaseRouter(ABC):
    def __init__(self) -> None:
        self.state_storage = StateStorage()
        self.routers: Set["BaseRouter"] = set()

    def registration_state_handler(
        self,
        event_type: str,
        handler: Callable,
        *,
        state_name: Optional[str] = None,
        filters: Optional[Tuple[Callable[[Any], bool]]] = None,
    ) -> None:
        logger.debug(f"registration_state_handler, {event_type=}, {handler=}, {state_name=}, {filters=}")
        if isinstance(filters, tuple) and (len(filters) == 0):
            filters = None
        state_name = state_name or handler.__name__
        state = StateModel(name=state_name, event_type=event_type, handler=handler, filters=filters)
        self.state_storage.add_state(state)

    def include_router(self, router: "BaseRouter") -> None:
        logger.debug(f"include_router, {router=}")
        self.routers.add(router)
