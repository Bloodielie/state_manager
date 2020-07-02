import inspect
from typing import Callable

from state_manager.models.dependency import DependencyManager


def get_func_attributes(function: Callable, dependency_manager: DependencyManager):
    dependencies = dependency_manager.fields.values()
    func_parameters = inspect.signature(function).parameters
    func_arg = {}
    for index, parameters in enumerate(func_parameters.items()):
        key, value = parameters
        for dependency in dependencies:
            if issubclass(value.annotation, dependency.type_):
                func_arg[value.name] = getattr(dependency_manager, dependency.name, None)
            elif issubclass(value.annotation, DependencyManager):
                func_arg[value.name] = dependency_manager
        if not func_arg and index == 0:
            func_arg[value.name] = dependency_manager.context
    return func_arg
