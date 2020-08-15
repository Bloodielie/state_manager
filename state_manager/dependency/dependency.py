import inspect
from logging import getLogger
from typing import Dict, Any, Callable

from state_manager import Depends
from state_manager.dependency.models import Scope, DependencyWrapper
from state_manager.dependency.signature import get_signature_to_implementation, get_typed_signature
from state_manager.types import Container
from state_manager.utils.check import check_function_and_run

logger = getLogger(__name__)


async def get_implementation(dependency: DependencyWrapper, dependency_container: Container) -> Any:
    signature = get_signature_to_implementation(dependency.implementation)
    if signature:
        attr = await search_attributes(dependency_container, signature)
        implementation = await check_function_and_run(dependency.implementation, **attr)
    else:
        implementation = dependency.implementation
    return implementation


async def search_attributes(dependency_container: Container, signatures: inspect.Signature) -> Dict[str, Any]:
    global i, q
    i += 1
    callable_object_arguments = {}
    app_container = dependency_container.container
    for attr_name, parameter in signatures.parameters.items():
        annotation = parameter.annotation
        if isinstance(parameter.default, Depends):
            dep = parameter.default.dependency
            dependency_ = dep if dep else annotation
            attr = await get_func_attributes(dependency_, dependency_container)
            callable_object_arguments[attr_name] = await check_function_and_run(dependency_, **attr)
            continue
        dependency = dependency_container.get(annotation)
        if dependency is not None:
            if dependency.scope == Scope.SINGLETON:
                if app_container.contains_singleton_dependency(annotation):
                    callable_object_arguments[attr_name] = dependency.implementation
                else:
                    implementation = await get_implementation(dependency, dependency_container)
                    app_container.add_singleton_implementation(annotation, implementation)
                    callable_object_arguments[attr_name] = implementation
            else:
                callable_object_arguments[attr_name] = await get_implementation(dependency, dependency_container)

    return callable_object_arguments


async def get_func_attributes(callable_: Callable[..., Any], dependency_container: Container) -> Dict[str, Any]:
    logger.debug(f"Get callable attr, callable={callable_}, dependency_container={dependency_container}")
    return await search_attributes(dependency_container, get_typed_signature(callable_))
