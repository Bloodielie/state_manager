from typing import Any

from pydantic import BaseModel
from enum import IntEnum


class Scope(IntEnum):
    SINGLETON: int = 0
    CONTEXT: int = 1


class DependencyWrapper(BaseModel):
    type_: Any
    implementation: Any
    scope: int = Scope.CONTEXT
