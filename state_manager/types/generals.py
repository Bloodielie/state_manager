from typing import Union, Optional, Tuple, Callable, List, Coroutine, Any

from state_manager.dependency.container import AppContainer, ContainerWrapper

Data = Optional[Union[dict, str, int, bool]]
AnyText = Union[tuple, list, str]
Container = Union[AppContainer, ContainerWrapper]
StateNames = Optional[Union[str, List[Optional[str]]]]
Filter = Optional[Union[Callable[..., Union[bool, Coroutine[Any, Any, bool]]], "BaseFilter"]]
Filters = Optional[Tuple[Filter, ...]]
