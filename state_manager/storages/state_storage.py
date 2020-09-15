from typing import Dict, Set, Generator, Optional, Union, List

from state_manager.models.state import StateModel
from logging import getLogger

logger = getLogger(__name__)


class StateStorage:
    def __init__(self) -> None:
        self._state_store: Dict[str, Set[StateModel]] = {}

    def add_state(self, state_model: StateModel) -> None:
        logger.debug(f"add_state, state_model={state_model}")
        state_store = self._state_store.get(state_model.name)
        if state_store is None:
            self._state_store[state_model.name] = {state_model}
        else:
            state_store.add(state_model)

    def get_state(
            self, event_type: str, state_name: Union[str, List[str]]
    ) -> Optional[Union[Generator[StateModel, None, None], List]]:
        logger.debug(f"get_state, event_type={event_type}, state_name={state_name}")
        if isinstance(state_name, str):
            state_name = [state_name]
        for name in state_name:
            state_store = self._state_store.get(name)
            if state_store is None:
                continue

            for state in state_store:
                if state.event_type == event_type and state.name == name:
                    yield state
        return []

    def expand(self, storage: "StateStorage") -> None:
        for state_name, state_models in storage.state_store.items():
            sub_state_models = self._state_store.get(state_name)
            if sub_state_models is not None:
                sub_state_models.update(state_models)
            else:
                self._state_store[state_name] = state_models

    @property
    def state_store(self) -> Dict[str, Set[StateModel]]:
        return self._state_store
