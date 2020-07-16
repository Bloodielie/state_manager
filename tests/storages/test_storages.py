import pytest

from state_manager.models.state import StateData
from state_manager.storage_settings import StorageSettings
from state_manager.storages.memory import MemoryStorage
from state_manager.storages.redis import RedisStorage


@pytest.fixture()
def state_data():
    return StateData(pre_state="home", current_state="home")


@pytest.mark.asyncio
async def test_memory_storage(state_data):
    storage = MemoryStorage()
    assert await storage.get("test") is None
    assert await storage.get("test", state_data) == state_data
    assert await storage.put("test", state_data) is None
    assert await storage.get("test") == state_data
    assert await storage.put("test", state_data) is None
    assert await storage.contains("test")
    assert await storage.delete("test") is None
    with pytest.raises(KeyError) as err:
        assert await storage.delete("test") is None
    assert await storage.get("test") is None
    assert storage.data == {}
    await storage.put("test", state_data)
    assert storage.data == {"test": state_data.json()}
    assert await storage.close() is None
    assert storage.data == {}


@pytest.mark.asyncio
async def test_memory_storage(state_data):
    storage = RedisStorage(StorageSettings())
    assert await storage.get("test") is None
    assert await storage.get("test", state_data) == state_data
    assert await storage.put("test", state_data) is None
    assert await storage.get("test") == state_data
    assert await storage.put("test", state_data) is None
    assert await storage.contains("test")
    assert await storage.delete("test") is None
    with pytest.raises(KeyError) as err:
        assert await storage.delete("test") is None
    assert await storage.get("test") is None
    assert await storage.close() is None
    assert await storage.wait_closed() is None
