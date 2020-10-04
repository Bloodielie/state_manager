from typing import Iterator, Dict, Any, Optional, List

from state_manager.dependency.models import DependencyWrapper, Scope
from state_manager.dependency.utils import _check_annotation, _is_context_in_implementation_attr
from state_manager.utils.utils import ContextInstanceMixin


def get_iterator_from_objects(*args: Any) -> Iterator[Any]:
    for iterator in args:
        if getattr(iterator, "__iter__", None) is None:
            continue
        for value in iterator:
            yield value


class AppContainer(ContextInstanceMixin):
    _dependencies: Dict[Any, DependencyWrapper] = {}
    _singleton_dependencies: Dict[Any, Any] = {}

    def __init__(self, context: Optional[List[Any]] = None) -> None:
        self._context = context or []
        self.bind_constant(AppContainer, self)
        self.set_current(self)

    def bind_constant(self, annotation: Any, implementation: Any) -> None:
        """Bind an object that does not need to be initialized"""
        self.bind(annotation, implementation, scope=Scope.SINGLETON)

    def bind(self, annotation: Any, implementation: Any, scope: int = Scope.CONTEXT) -> None:
        """Bind an object to be initialized"""
        if scope == Scope.SINGLETON:
            for context in self._context:
                if _is_context_in_implementation_attr(implementation, context):
                    scope = Scope.CONTEXT
                    break
        self._dependencies[annotation] = DependencyWrapper(type_=annotation, implementation=implementation, scope=scope)

    def bind_singleton(self, annotation: Any, implementation: Any) -> None:
        """Bind an object that will be initialized once"""
        self.bind(annotation, implementation, scope=Scope.SINGLETON)

    def get(self, annotation: Any) -> Optional[DependencyWrapper]:
        for dependency in self._singleton_dependencies:
            if _check_annotation(annotation, dependency):
                return self._singleton_dependencies.get(dependency)
        for dependency in self._dependencies:
            if _check_annotation(annotation, dependency):
                return self._dependencies.get(dependency)

    def contains_singleton_dependency(self, annotation: Any) -> bool:
        for dependency in self._singleton_dependencies:
            if _check_annotation(annotation, dependency):
                return True
        return False

    def add_singleton_implementation(self, annotation: Any, implementation: Any) -> None:
        self._singleton_dependencies[annotation] = DependencyWrapper(
            type_=annotation, implementation=implementation, scope=Scope.SINGLETON
        )

    def __iter__(self) -> Iterator[DependencyWrapper]:
        for value in get_iterator_from_objects(self._dependencies.values(), self._singleton_dependencies.values()):
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
        for value in get_iterator_from_objects(self.container, self.app_dependency.values()):
            yield value
