import contextvars
from typing import Iterator, Dict, Any, Optional, Type, TypeVar, Callable

from state_manager.dependency.models import DependencyWrapper

T = TypeVar("T")


class ContextInstanceMixin:
    def __init_subclass__(cls, **kwargs):
        cls.__context_instance = contextvars.ContextVar(f"instance_{cls.__name__}")
        return cls

    @classmethod
    def get_current(cls: Type[T], no_error=True) -> T:
        if no_error:
            return cls.__context_instance.get(None)
        return cls.__context_instance.get()

    @classmethod
    def set_current(cls: Type[T], value: T):
        if not isinstance(value, cls):
            raise TypeError(f"Value should be instance of {cls.__name__!r} not {type(value).__name__!r}")
        cls.__context_instance.set(value)


class AppContainer(ContextInstanceMixin):
    dependencies: Dict[Any, DependencyWrapper] = {}

    def __init__(self) -> None:
        self.bind_constant(self, self)
        self.set_current(self)

    def bind_constant(self, annotation: Any, implementation: Any) -> None:
        """Bind an object that does not need to be initialized"""
        self.bind(annotation, implementation, is_constant=True)

    def bind_factory(self, annotation: Any, factory: Callable[..., Callable]) -> None:
        """Bind a factory called before giving the object"""
        setattr(factory, "is_factory", True)
        self.bind(annotation, factory)

    def bind(self, annotation: Any, implementation: Any, is_constant: bool = False) -> None:
        """Bind an object to be initialized"""
        self.dependencies[annotation] = DependencyWrapper(
            type_=annotation, implementation=implementation, is_constant=is_constant
        )

    def get(self, annotation: Any) -> Optional[DependencyWrapper]:
        return self.dependencies.get(annotation)

    def __iter__(self) -> Iterator[DependencyWrapper]:
        for value in self.dependencies.values():
            yield value


class ContainerWrapper:
    def __init__(self, container: AppContainer) -> None:
        self.container = container
        self.app_dependency: Dict[Any, DependencyWrapper] = {}

    def add_dependency(self, annotation: Any, implementation: Any) -> None:
        self.app_dependency[annotation] = DependencyWrapper(type_=annotation, implementation=implementation)

    def __iter__(self) -> Iterator[DependencyWrapper]:
        for value in self.container:
            yield value
        for value in self.app_dependency.values():
            yield value
