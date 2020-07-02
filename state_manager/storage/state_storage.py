from typing import Dict, Set, Generator, Optional
from state_manager.models.state import StateModel


class StateStorage:
    def __init__(self) -> None:
        self._state_store: Dict[str, Set[StateModel]] = {}

    def add_state(self, state_model: StateModel) -> None:
        state_store = self._state_store.get(state_model.event_type)
        if state_store is None:
            self._state_store[state_model.event_type] = {state_model}
        else:
            state_store.add(state_model)

    def get_state(self, event_type: str, name: str) -> Optional[Generator[StateModel, None, None]]:
        state_store = self._state_store.get(event_type)
        if state_store is None:
            return None
        for state in state_store:
            if state.name != name:
                continue
            yield state
