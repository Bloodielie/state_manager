from typing import Callable, Optional, Tuple, Type, Union

from pydantic import BaseModel

from state_manager.filter import BaseFilter


class StateModel(BaseModel):
    name: str
    event_type: str
    handler: Callable
    filters: Optional[Tuple[Callable]] = None

    class Config:
        arbitrary_types_allowed = True

    def __hash__(self) -> int:
        return hash((self.name, self.handler, self.event_type, self.filters))
