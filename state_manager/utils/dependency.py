import inspect
from typing import Callable

from aiogram import Bot, Dispatcher

from state_manager.models.dependency import DependencyStorage, Depends, StateManager
from state_manager.storage.base import BaseStorage
from state_manager.types import Context
from state_manager.utils.check import check_function_and_run


async def get_func_attributes(function: Callable, dependency_storage: DependencyStorage):
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


def dependency_storage_factory(
    bot: Bot, dispatcher: Dispatcher, context: Context, storage: BaseStorage
) -> DependencyStorage:
    state_manager = StateManager(storage=storage, context=context)
    return DependencyStorage(
        bot=bot, dispatcher=dispatcher, context=context, storage=storage, state_manager=state_manager
    )
