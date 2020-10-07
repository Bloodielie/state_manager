from typing import Any, Dict, List

from pydantic import BaseModel
from enum import IntEnum


class Scope(IntEnum):
    SINGLETON: int = 0
    CONTEXT: int = 1


class DependencyWrapper(BaseModel):
    type_: Any
    implementation: Any
    scope: int = Scope.CONTEXT


class DependencyStorage(BaseModel):
    dependencies: List[DependencyWrapper] = list()
    singleton_dependencies: List[DependencyWrapper] = list()
    constant_dependencies: List[DependencyWrapper] = list()
