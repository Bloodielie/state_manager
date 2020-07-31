from typing import Any

from pydantic import BaseModel


class DependencyWrapper(BaseModel):
    type_: Any
    implementation: Any
