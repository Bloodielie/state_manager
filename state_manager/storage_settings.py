import json
import ssl
from typing import Optional, Union

from pydantic import BaseSettings, AnyUrl, Field

from state_manager.types import Dumper, Loader


class StorageSettings(BaseSettings):
    storage_dsn: Union[AnyUrl, str] = Field("redis://localhost:6379", env="storage_dsn")
    storage_ssl: Optional[ssl.SSLContext] = Field(None, env="storage_ssl")
    storage_db: Optional[int] = Field(None, env="storage_db")
    pool_size: int = Field(10, env="pool_size")
    storage_timeout: int = Field(5, env="storage_timeout")
    dumper: Dumper = json.dumps
    loader: Loader = json.loads

    class Config:
        env_file = ".env"
        arbitrary_types_allowed = True
