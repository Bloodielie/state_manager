import inspect

from state_manager.utils.dependency import get_typed_signature


def func_test(a: str, b: str):
    return None


def func_test_2(a: str, b: "str"):
    return None


def test_get_typed_signature():
    assert get_typed_signature(func_test) == inspect.signature(func_test)
    assert get_typed_signature(func_test_2) != inspect.signature(func_test_2)
