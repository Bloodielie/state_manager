import asyncio
import typing

from state_manager.models.state import StateData
from state_manager.storage.base import BaseStorage
from state_manager.storage_settings import StorageSettings
from logging import getLogger

try:
    import aioredis
except ImportError:
    aioredis = None


logger = getLogger(__name__)


class RedisStorage(BaseStorage):
    def __init__(
        self, storage_settings: StorageSettings, loop: typing.Optional[asyncio.AbstractEventLoop] = None, **kwargs,
    ):
        if aioredis is None:
            raise RuntimeError("You have to install aioredis - pip install aioredis")

        self._kwargs = kwargs
        self._storage_settings = storage_settings

        self._host = storage_settings.storage_dsn.host
        self._port = storage_settings.storage_dsn.port
        self._db = storage_settings.storage_db
        self._password = storage_settings.storage_dsn.password
        self._ssl = storage_settings.storage_ssl
        self._pool_size = storage_settings.pool_size
        self._timeout = storage_settings.storage_timeout
        self._loop = loop or asyncio.get_event_loop()

        self._redis: typing.Optional["aioredis.Redis"] = None
        self._connection_lock = asyncio.Lock(loop=self._loop)

    async def get(self, key: str, default: typing.Optional[StateData] = None) -> typing.Optional[StateData]:
        conn = await self.redis()
        logger.debug(f"get, {key=}, {default=}")
        key_ = await conn.get(key)
        if key_:
            return StateData.parse_raw(key_)
        return default

    async def put(self, key: str, value: StateData) -> None:
        conn = await self.redis()
        logger.debug(f"put, {key=}, {value=}")
        if pre_state := await self.get(key):
            value.pre_state = pre_state.current_state
            await conn.set(key, value.json())
        await conn.set(key, value.json())

    async def delete(self, key: str) -> typing.Optional[typing.NoReturn]:
        logger.debug(f"delete, {key=}")
        if not await self.contains(key):
            raise KeyError("Storage doesn't contain this key.")

        conn = await self.redis()
        await conn.delete(key)

    async def contains(self, key: str) -> bool:
        conn = await self.redis()
        logger.debug(f"contains, {key=}")
        return await conn.exists(key)

    async def redis(self) -> "aioredis.Redis":
        logger.debug(f"get pool")
        async with self._connection_lock:
            if self._redis is None or self._redis.closed:
                logger.debug(f"create pool")
                self._redis = await aioredis.create_redis_pool(
                    (self._host, self._port),
                    db=self._db,
                    password=self._password,
                    ssl=self._ssl,
                    loop=self._loop,
                    maxsize=self._pool_size,
                    timeout=self._timeout,
                    **self._kwargs,
                )

        return self._redis

    async def close(self) -> None:
        async with self._connection_lock:
            if self._redis and not self._redis.closed:
                logger.debug(f"close redis pool")
                self._redis.close()

    async def wait_closed(self) -> bool:
        async with self._connection_lock:
            if self._redis:
                logger.debug(f"wait close redis pool")
                return await self._redis.wait_closed()
            return True
