import inspect
from logging import getLogger
from typing import Callable, Dict, Any, TypeVar, Optional

from aiogram.types.base import TelegramObject
from pydantic.typing import ForwardRef, evaluate_forwardref

from state_manager.dependency.container import ContainerWrapper
from state_manager.models.dependencys.base import Depends
from state_manager.utils.check import check_function_and_run, is_factory

logger = getLogger(__name__)

T = TypeVar("T")


def get_typed_signature(call: Callable) -> inspect.Signature:
    signature = inspect.signature(call)
    globalns = getattr(call, "__globals__", {})
    typed_params = [
        inspect.Parameter(
            name=param.name, kind=param.kind, default=param.default, annotation=get_typed_annotation(param, globalns),
        )
        for param in signature.parameters.values() if param.name != "self"
    ]
    typed_signature = inspect.Signature(typed_params)
    return typed_signature


def get_typed_annotation(param: inspect.Parameter, globalns: Dict[str, Any]) -> Any:
    annotation = param.annotation
    if isinstance(annotation, str):
        try:
            annotation = ForwardRef(annotation)  # type: ignore
            annotation = evaluate_forwardref(annotation, globalns, globalns)
        except (TypeError, NameError):
            annotation = param.annotation
    return annotation


def get_signature_to_implementation(implementation: Any) -> Optional[inspect.Signature]:
    if inspect.isclass(implementation):
        return get_typed_signature(implementation.__init__)
    elif inspect.isfunction(implementation) or inspect.ismethod(implementation):
        return get_typed_signature(implementation)
    elif hasattr(implementation, '__call__'):
        return get_typed_signature(implementation.__call__)


async def search_attributes(dependency_storage: ContainerWrapper, signatures: inspect.Signature) -> Dict[str, Any]:
    func_arg = {}
    for attr_name, parameter in signatures.parameters.items():
        if isinstance(parameter.default, Depends):
            dep = parameter.default.dependency
            dependency = dep if dep else parameter.annotation
            attr = await get_func_attributes(dependency, dependency_storage)
            func_arg[attr_name] = await check_function_and_run(dependency, **attr)
            continue

        for dependency in dependency_storage:
            try:
                if not issubclass(parameter.annotation, dependency.type_):
                    continue
            except TypeError:
                if parameter.annotation != dependency.type_:
                    continue

            if is_factory(dependency.implementation):
                attr = await get_func_attributes(dependency.implementation, dependency_storage)
                func_arg[attr_name] = await check_function_and_run(dependency.implementation, **attr)
            elif dependency.is_constant:
                func_arg[attr_name] = dependency.implementation
            else:
                signature = get_signature_to_implementation(dependency.implementation)
                if signature is None:
                    func_arg[attr_name] = dependency.implementation
                else:
                    attr = await search_attributes(dependency_storage, signature)
                    func_arg[attr_name] = await check_function_and_run(dependency.implementation, **attr)

        if not func_arg:
            func_arg[attr_name] = dependency_storage.container.get(TelegramObject)
    return func_arg


async def get_func_attributes(callable_: Callable[..., Any], dependency_storage: ContainerWrapper) -> Dict[str, Any]:
    logger.debug(f"Get callable attr, {callable_=}, {dependency_storage=}")
    return await search_attributes(dependency_storage, get_typed_signature(callable_))
