import contextvars
from typing import Iterator, Dict, Any, Optional, Type, TypeVar

from state_manager.dependency.models import DependencyWrapper, Scope
from state_manager.dependency.utils import _check_annotation, _is_context_in_implementation_attr

try:
    from aiogram.types.base import TelegramObject as context
except ImportError:
    from vkwave.bots import BaseEvent as context

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
    singleton_dependencies: Dict[Any, Any] = {}

    def __init__(self) -> None:
        self.bind_constant(AppContainer, self)
        self.set_current(self)

    def bind_constant(self, annotation: Any, implementation: Any) -> None:
        """Bind an object that does not need to be initialized"""
        self.bind(annotation, implementation, scope=Scope.SINGLETON)

    def bind(self, annotation: Any, implementation: Any, scope: int = Scope.CONTEXT) -> None:
        """Bind an object to be initialized"""
        if scope == Scope.SINGLETON and _is_context_in_implementation_attr(implementation, context):
            scope = Scope.CONTEXT
        self.dependencies[annotation] = DependencyWrapper(type_=annotation, implementation=implementation, scope=scope)

    def get(self, annotation: Any) -> Optional[DependencyWrapper]:
        for dependency in self.singleton_dependencies:
            if _check_annotation(annotation, dependency):
                return self.singleton_dependencies.get(dependency)
        for dependency in self.dependencies:
            if _check_annotation(annotation, dependency):
                return self.dependencies.get(dependency)

    def contains_singleton_dependency(self, annotation: Any) -> bool:
        for dependency in self.singleton_dependencies:
            if _check_annotation(annotation, dependency):
                return True
        return False

    def add_singleton_implementation(self, annotation: Any, implementation: Any) -> None:
        self.singleton_dependencies[annotation] = DependencyWrapper(
            type_=annotation, implementation=implementation, scope=Scope.SINGLETON
        )

    def __iter__(self) -> Iterator[DependencyWrapper]:
        for value in self.dependencies.values():
            yield value


class ContainerWrapper:
    def __init__(self, container: AppContainer) -> None:
        self.container = container
        self.app_dependency: Dict[Any, DependencyWrapper] = {}

    def add_dependency(self, annotation: Any, implementation: Any) -> None:
        self.app_dependency[annotation] = DependencyWrapper(type_=annotation, implementation=implementation)

    def get(self, annotation: Any) -> Optional[DependencyWrapper]:
        for dependency in self.app_dependency:
            if _check_annotation(annotation, dependency):
                return self.app_dependency.get(dependency)
        return self.container.get(annotation)

    def __iter__(self) -> Iterator[DependencyWrapper]:
        for value in self.container:
            yield value
        for value in self.app_dependency.values():
            yield value
