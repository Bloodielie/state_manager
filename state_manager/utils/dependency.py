import inspect
from typing import Callable

from state_manager.models.dependencys.aiogram import AiogramDependencyStorage, AiogramStateManager
from state_manager.models.dependencys.base import Depends, BaseDependencyStorage
from state_manager.models.dependencys.vkwave import VkWaveDependencyStorage, VkWaveStateManager
from state_manager.utils.check import check_function_and_run
from logging import getLogger

logger = getLogger(__name__)


async def get_func_attributes(function: Callable, dependency_storage: BaseDependencyStorage):
    logger.debug(f"Get func attr, {function=}, {dependency_storage=}")
    func_arg = {}
    dependencies = dependency_storage.fields.values()
    for attr_name, parameter in inspect.signature(function).parameters.items():
        if isinstance(parameter.default, Depends):
            dependency = parameter.default.dependency
            attr = await get_func_attributes(dependency, dependency_storage)
            func_arg[attr_name] = await check_function_and_run(dependency, **attr)
            continue

        for dependency in dependencies:
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
