import inspect
from typing import Callable, Dict, Any, TypeVar

from pydantic.typing import ForwardRef, evaluate_forwardref

from state_manager.models.dependencys.aiogram import AiogramDependencyStorage, AiogramStateManager
from state_manager.models.dependencys.base import Depends, BaseDependencyStorage
from state_manager.models.dependencys.vkwave import VkWaveDependencyStorage, VkWaveStateManager
from state_manager.utils.check import check_function_and_run
from logging import getLogger

logger = getLogger(__name__)

T = TypeVar("T")


def get_typed_signature(call: Callable) -> inspect.Signature:
    signature = inspect.signature(call)
    globalns = getattr(call, "__globals__", {})
    typed_params = [
        inspect.Parameter(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=get_typed_annotation(param, globalns),
        )
        for param in signature.parameters.values()
    ]
    typed_signature = inspect.Signature(typed_params)
    return typed_signature


def get_typed_annotation(param: inspect.Parameter, globalns: Dict[str, Any]) -> Any:
    annotation = param.annotation
    if isinstance(annotation, str):
        annotation = ForwardRef(annotation)
        annotation = evaluate_forwardref(annotation, globalns, globalns)
    return annotation


async def get_func_attributes(function: Callable[..., T], dependency_storage: BaseDependencyStorage) -> T:
    logger.debug(f"Get func attr, {function=}, {dependency_storage=}")
    func_arg = {}
    for attr_name, parameter in get_typed_signature(function).parameters.items():
        if isinstance(parameter.default, Depends):
            dep = parameter.default.dependency
            dependency = dep if dep else parameter.annotation
            attr = await get_func_attributes(dependency, dependency_storage)
            func_arg[attr_name] = await check_function_and_run(dependency, **attr)
            continue

        for dependency in dependency_storage.fields.values():
            if not issubclass(parameter.annotation, dependency.type_):
                continue
            func_arg[attr_name] = getattr(dependency_storage, dependency.name, None)

        if not func_arg:
            func_arg[attr_name] = dependency_storage.context
    return func_arg


def dependency_storage_factory(*, lib: str = "aiogram", **kwargs) -> BaseDependencyStorage:
    if lib == "aiogram":
        kwargs["state_manager"] = AiogramStateManager(storage=kwargs.get("storage"), context=kwargs.get("context"))
        logger.debug(f"Create AiogramDependencyStorage, {kwargs=}")
        return AiogramDependencyStorage(**kwargs)
    elif lib == "vkwave":
        kwargs["state_manager"] = VkWaveStateManager(storage=kwargs.get("storage"), context=kwargs.get("context"))
        logger.debug(f"Create VkWaveDependencyStorage, {kwargs=}")
        return VkWaveDependencyStorage(**kwargs)
