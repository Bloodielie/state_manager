from pydantic import BaseModel
from typing import Callable, Optional


class StateModel(BaseModel):
    name: str
    event_type: str
    handler: Callable
    filter: Optional[Callable] = None

    class Config:
        arbitrary_types_allowed = True

    def __hash__(self) -> int:
        return hash((self.name, self.handler, self.event_type, self.filter))
