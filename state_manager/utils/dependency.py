import inspect
from typing import Callable

from aiogram import Bot, Dispatcher

from state_manager.models.dependency import DependencyStorage, Depends, StateManager
from state_manager.storage.base import BaseStorage
from state_manager.types import Context
from state_manager.utils.check import check_function_and_run


async def get_func_attributes(function: Callable, dependency_storage: DependencyStorage):
    func_arg = {}
    for _, parameter in inspect.signature(function).parameters.items():
        attr_name = parameter.name
        depends_result = await embedded_depends_check(parameter, dependency_storage)
        if depends_result is not None:
            func_arg[attr_name] = depends_result
            continue
        dependency_result = dependency_search(parameter, dependency_storage)
        if not func_arg and dependency_result is None:
            func_arg[attr_name] = dependency_storage.context
        else:
            func_arg[attr_name] = dependency_result
    return func_arg


async def embedded_depends_check(parameter: inspect.Parameter, dependency_storage: DependencyStorage):
    if isinstance(parameter.default, Depends) and (
        callable(parameter.annotation) or parameter.annotation == parameter.empty
    ):
        """
        a: Depends = Depends(check_agg2)
        a = Depends(check_agg2)
        a: check_agg2 = Depends()
        a: Any = Depends(check_agg2) 
        """
        return await run_depends_function(parameter, dependency_storage)


def dependency_search(parameter: inspect.Parameter, dependency_storage: DependencyStorage):
    dependencies = dependency_storage.fields.values()
    for dependency in dependencies:
        if not issubclass(parameter.annotation, dependency.type_):
            continue
        return getattr(dependency_storage, dependency.name, None)


async def run_depends_function(parameter: inspect.Parameter, dependency_storage: DependencyStorage):
    dependency = parameter.default.dependency
    attr = await get_func_attributes(dependency, dependency_storage)
    return await check_function_and_run(dependency, **attr)


def dependency_storage_factory(
    bot: Bot, dispatcher: Dispatcher, context: Context, storage: BaseStorage
) -> DependencyStorage:
    state_manager = StateManager(storage=storage, context=context)
    return DependencyStorage(
        bot=bot, dispatcher=dispatcher, context=context, storage=storage, state_manager=state_manager
    )
