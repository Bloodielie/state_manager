import inspect
from typing import Iterator, Dict, Any, Optional, List, TypeVar, Type, Union, Callable

from state_manager.dependency.models import DependencyWrapper, Scope, DependencyStorage
from state_manager.dependency.signature import get_typed_signature, get_signature_to_implementation
from state_manager.dependency.utils import _check_annotation, _is_context_in_implementation_attr
from state_manager.utils.utils import ContextInstanceMixin

T = TypeVar("T")


def get_iterator_from_objects(*args: Any) -> Iterator[Any]:
    for iterator in args:
        if getattr(iterator, "__iter__", None) is None:
            continue
        for value in iterator:
            yield value


class AppContainer(ContextInstanceMixin):
    def __init__(self, context: Optional[List[Any]] = None) -> None:
        self._context = context or []
        self._storage = DependencyStorage()

        self.bind_constant(AppContainer, self)
        self.set_current(self)

    def bind_singleton(self, annotation: Type[T], implementation: T) -> None:
        """Bind an object that will be initialized once"""
        scope = Scope.SINGLETON
        for context in self._context:
            if _is_context_in_implementation_attr(implementation, context):
                scope = Scope.CONTEXT
                break

        if scope == Scope.CONTEXT:
            self.bind(annotation, implementation, scope=Scope.CONTEXT)
        elif scope == Scope.SINGLETON:
            obj = self._resolve_dependency(implementation)
            wrapper = DependencyWrapper(type_=annotation, implementation=obj, scope=Scope.SINGLETON)
            self._storage.singleton_dependencies.append(wrapper)

    def bind_constant(self, annotation: Type[T], implementation: T) -> None:
        """Bind an object that does not need to be initialized"""
        wrapper = DependencyWrapper(type_=annotation, implementation=implementation, scope=Scope.SINGLETON)
        self._storage.constant_dependencies.append(wrapper)

    def bind(self, annotation: Type[T], implementation: T, scope: int = Scope.CONTEXT) -> None:
        """Bind an object to be initialized"""
        wrapper = DependencyWrapper(type_=annotation, implementation=implementation, scope=scope)
        self._storage.dependencies.append(wrapper)

    def get(self, annotation: Type[T]) -> Optional[T]:
        """Get object from container"""
        singleton_dependency = self._get_checked_dependency(
            annotation, [self._storage.constant_dependencies, self._storage.singleton_dependencies]
        )
        if singleton_dependency is not None:
            return singleton_dependency.implementation

        for dependency_wrapper in self._storage.dependencies:
            if not _check_annotation(annotation, dependency_wrapper.type_):
                continue
            return self._get_implementation(dependency_wrapper.implementation)

    def _get_obj_attr(self, signatures: inspect.Signature, call_to_get: Callable) -> Dict[str, Any]:
        """Get resolved object attributes"""
        callable_object_arguments = {}
        for attr_name, parameter in signatures.parameters.items():
            annotation = parameter.annotation
            dependency = call_to_get(annotation)
            if dependency is not None:
                callable_object_arguments[attr_name] = self._get_implementation(dependency.implementation)

        return callable_object_arguments

    def _resolve_dependency(self, obj, call_to_get: Optional[Callable] = None):
        """Resolved class dependencies and initialize it"""
        call_to_get = call_to_get or self._get
        obj_attr = self._get_obj_attr(get_typed_signature(obj), call_to_get)
        return obj(**obj_attr)

    def _get_implementation(self, implementation: Union[Type[T], T]) -> T:
        signature = get_signature_to_implementation(implementation)
        if signature:
            attr = self._get_obj_attr(signature, self._get)
            implementation = implementation(**attr)
        else:
            implementation = implementation
        return implementation

    def _get(self, annotation: Any) -> Optional[DependencyWrapper]:
        """Get unresolved object/class"""
        return self._get_checked_dependency(
            annotation, [self._storage.constant_dependencies, self._storage.singleton_dependencies, self._storage.dependencies]
        )

    @staticmethod
    def _get_checked_dependency(annotation: Any, dependencies: List[List[DependencyWrapper]]) -> Optional[DependencyWrapper]:
        for dependency in dependencies:
            for dependency_wrapper in dependency:
                if _check_annotation(annotation, dependency_wrapper.type_):
                    return dependency_wrapper


class ContainerWrapper:
    def __init__(self, container: AppContainer) -> None:
        self._container = container
        self._app_dependency: Dict[Any, DependencyWrapper] = {}

    def add_dependency(self, annotation: Type[T], implementation: T) -> None:
        self._app_dependency[annotation] = DependencyWrapper(type_=annotation, implementation=implementation)

    def get(self, annotation: Any) -> Optional[DependencyWrapper]:
        for dependency in self._app_dependency:
            if _check_annotation(annotation, dependency):
                return self._app_dependency.get(dependency)
        return self._container._get(annotation)

    def get_obj_attr(self, obj) -> Dict[str, Any]:
        return self._container._get_obj_attr(get_typed_signature(obj), self.get)
