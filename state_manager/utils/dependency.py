import inspect
from typing import Callable

from state_manager.models.dependency import DependencyManager, Depends
from state_manager.utils.check import check_function_and_run


async def get_func_attributes(function: Callable, dependency_manager: DependencyManager):
    func_arg = {}
    for _, parameter in inspect.signature(function).parameters.items():
        attr_name = parameter.name
        depends_result = await embedded_depends_check(parameter, dependency_manager)
        if depends_result is not None:
            func_arg[attr_name] = depends_result
            continue
        dependency_result = dependency_search(parameter, dependency_manager)
        if not func_arg and dependency_result is None:
            func_arg[attr_name] = dependency_manager.context
        else:
            func_arg[attr_name] = dependency_result
    return func_arg


async def embedded_depends_check(parameter: inspect.Parameter, dependency_manager: DependencyManager):
    if isinstance(parameter.default, Depends) and (
        callable(parameter.annotation) or parameter.annotation == parameter.empty
    ):
        """
        a: Depends = Depends(check_agg2)
        a = Depends(check_agg2)
        a: check_agg2 = Depends()
        a: Any = Depends(check_agg2) 
        """
        return await run_depends_function(parameter, dependency_manager)
    else:
        return None


def dependency_search(parameter: inspect.Parameter, dependency_manager: DependencyManager):
    dependencies = dependency_manager.fields.values()
    for dependency in dependencies:
        if issubclass(parameter.annotation, dependency.type_):
            return getattr(dependency_manager, dependency.name, None)
        elif issubclass(parameter.annotation, DependencyManager):
            return dependency_manager


async def run_depends_function(parameter: inspect.Parameter, dependency_manager: DependencyManager):
    dependency = parameter.default.dependency
    attr = await get_func_attributes(dependency, dependency_manager)
    return await check_function_and_run(dependency, **attr)
