from logging import getLogger
from typing import Optional, Union, List, Callable

from state_manager.models.state import StateModel
from state_manager.storages.state_storage import StateStorage
from state_manager.types.generals import Filters

logger = getLogger(__name__)


class BaseStateHandler:
    def __init__(self, storage: Optional[StateStorage] = None) -> None:
        self.storage = storage or StateStorage()

    def registration_state_handler(
        self,
        event_type: str,
        handler: Callable,
        *,
        state_name: Optional[Union[str, List[Optional[str]]]] = None,
        filters: Filters = None,
    ) -> None:
        if isinstance(state_name, str) or state_name is None:
            state_names = [state_name]
        else:
            state_names = state_name
        logger.debug(
            f"registration_state_handler, event_type={event_type}, handler={handler}, state_names={state_names}, filters={filters}"
        )
        if isinstance(filters, tuple) and (len(filters) == 0):
            filters = None
        for state_name in state_names:
            state_name = state_name or handler.__name__
            state = StateModel(name=state_name, event_type=event_type, handler=handler, filters=filters)
            self.storage.add_state(state)


class BaseHandler:
    def __init__(self, storage: Optional[StateStorage] = None) -> None:
        self.storage = storage or StateStorage()

    def registration_handler(
        self,
        event_type: str,
        handler: Callable,
        *,
        filters: Filters = None,
    ) -> None:
        logger.debug(
            f"registration_handler, event_type={event_type}, handler={handler}, state_names=*, filters={filters}"
        )
        if isinstance(filters, tuple) and (len(filters) == 0):
            filters = None
        state = StateModel(name="*", event_type=event_type, handler=handler, filters=filters)
        self.storage.add_state(state)
