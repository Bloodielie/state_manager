from typing import Union, Optional, Tuple, Callable, List, Coroutine, Any
from pyject import BaseContainer

Data = Optional[Union[dict, str, int, bool]]
BaseContainer = BaseContainer
AnyText = Union[tuple, list, str]
StateNames = Optional[Union[str, List[Optional[str]]]]
Filter = Optional[Union[Callable[..., Union[bool, Coroutine[Any, Any, bool]]], "BaseFilter"]]
Filters = Optional[Tuple[Filter, ...]]
