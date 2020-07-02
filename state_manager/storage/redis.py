import asyncio
import json
import typing

from state_manager.storage.base import BaseStorage
from state_manager.storage_settings import StorageSettings
from state_manager.types import Dumper, Loader

try:
    import aioredis
except ImportError:
    aioredis = None


class RedisStorage(BaseStorage):
    def __init__(
        self,
        storage_settings: StorageSettings,
        loop: typing.Optional[asyncio.AbstractEventLoop] = None,
        dumper: Dumper = json.dumps,
        loader: Loader = json.loads,
        **kwargs,
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

        self._dumper = dumper
        self._loader = loader

        self._redis: typing.Optional["aioredis.Redis"] = None
        self._connection_lock = asyncio.Lock(loop=self._loop)

    async def get(self, key: str, default: typing.Optional[typing.Any] = None) -> typing.Union[None, typing.Any]:
        conn = await self.redis()

        key_ = await conn.get(key)
        if key_:
            return self._loader(key_)
        return default

    async def put(self, key: str, value: typing.Any) -> None:
        conn = await self.redis()
        await conn.set(key, self._dumper(value))

    async def delete(self, key: str) -> typing.Optional[typing.NoReturn]:
        if not await self.contains(key):
            raise KeyError("Storage doesn't contain this key.")

        conn = await self.redis()
        await conn.delete(key)

    async def contains(self, key: str) -> bool:
        conn = await self.redis()
        return await conn.exists(key)

    async def redis(self) -> "aioredis.Redis":
        async with self._connection_lock:
            if self._redis is None or self._redis.closed:
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
                self._redis.close()

    async def wait_closed(self) -> bool:
        async with self._connection_lock:
            if self._redis:
                return await self._redis.wait_closed()
            return True
