import inspect

from state_manager.utils.dependency import get_typed_signature


def func_test(a: str, b: "int"):
    pass


print(get_typed_signature(func_test))
