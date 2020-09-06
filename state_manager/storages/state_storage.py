from typing import Dict, Set, Generator, Optional, Union, List

from state_manager.models.state import StateModel
from logging import getLogger

logger = getLogger(__name__)


class StateStorage:
    def __init__(self) -> None:
        self._state_store: Dict[str, Set[StateModel]] = {}

    def add_state(self, state_model: StateModel) -> None:
        logger.debug(f"add_state, state_model={state_model}")
        state_store = self._state_store.get(state_model.event_type)
        if state_store is None:
            self._state_store[state_model.event_type] = {state_model}
        else:
            state_store.add(state_model)

    def get_state(self, event_type: str, name: str) -> Optional[Union[Generator[StateModel, None, None], List]]:
        logger.debug(f"get_state, event_type={event_type}, name={name}")
        state_store = self._state_store.get(event_type)
        if state_store is None:
            return []
        for state in state_store:
            if state.name != name:
                continue
            yield state

    @property
    def state_store(self) -> Dict[str, Set[StateModel]]:
        return self._state_store
