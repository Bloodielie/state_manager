from typing import Optional, Callable, Any

from pydantic.main import BaseModel


class EventsModel(BaseModel):
    on_startup: Optional[Callable[..., Any]] = None
    on_shutdown: Optional[Callable[..., Any]] = None
