import pytest

from state_manager.utils.check import is_coroutine_callable
from state_manager.utils.runers import check_function_and_run


async def coroutine_test():
    return None


def func_test():
    return None


class ClassTest:
    pass


def test_is_coroutine_callable():
    assert is_coroutine_callable(coroutine_test)
    assert not is_coroutine_callable(ClassTest)


@pytest.mark.asyncio
async def test_check_function_and_run():
    assert await check_function_and_run(coroutine_test) is None
    assert await check_function_and_run(func_test) is None
