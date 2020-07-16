import pytest

from state_manager import MemoryStorage
from state_manager.utils.utils import get_user_state_name


@pytest.mark.asyncio
async def test_get_user_state_name():
    storage = MemoryStorage()
    assert await get_user_state_name("123", storage, "123") == "123"
