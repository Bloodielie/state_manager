from typing import Callable, Optional, Tuple, Any

from pydantic import BaseModel

try:
    import ujson as json
except ImportError:
    import json


class StateModel(BaseModel):
    name: str
    event_type: str
    handler: Callable
    filters: Optional[Tuple[Callable[[Any], bool]]] = None

    class Config:
        arbitrary_types_allowed = True

    def __hash__(self) -> int:
        return hash((self.name, self.handler, self.event_type, self.filters))


class StateData(BaseModel):
    pre_state: Optional[str]
    current_state: str
    data: Optional[Any]

    class Config:
        json_loads = json.loads
        json_dumps = json.dumps
