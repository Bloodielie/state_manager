import importlib
from logging import getLogger
from typing import Optional, Union

import httpx

from state_manager import BaseStorage
from state_manager.dependency.container import AppContainer
from state_manager.enums import Frameworks
from state_manager.handlers.aiogram import AiogramStateHandler, AiogramHandler
from state_manager.handlers.vkwave import VkWaveStateHandler, VkWaveHandler
from state_manager.storages.app import RouterStorage
from state_manager.storage_settings import StorageSettings
from state_manager.storages import redis
from state_manager.storages.state_storage import StateStorage

logger = getLogger(__name__)


class Router:
    def __init__(self, mode: Union[Frameworks, str] = Frameworks.AIOGRAM):
        state_storage = StateStorage()
        if mode == Frameworks.AIOGRAM:
            self.on_state = AiogramStateHandler(state_storage)
            self.on = AiogramHandler(state_storage)
        elif mode == Frameworks.VKWAVE:
            self.on_state = VkWaveStateHandler(state_storage)
            self.on = VkWaveHandler(state_storage)

        self.storage = RouterStorage[Router](state_storage=self.on_state.storage)

    def include_router(self, router: "Router") -> None:
        logger.debug(f"include_router, router={router}")
        self.storage.routers.add(router)


class MainRouter(Router):
    def __init__(self, token: str, mode: Union[Frameworks, str] = Frameworks.AIOGRAM) -> None:
        super().__init__(mode)
        self.container = AppContainer()

        self.mode = mode
        if mode == Frameworks.AIOGRAM:
            self._aiogram = importlib.import_module("aiogram")
            bot = self._aiogram.Bot(token=token)
            self.dp = self._aiogram.Dispatcher(bot)
            self.inject_values = {self._aiogram.Bot: bot, self._aiogram.Dispatcher: self.dp}
        elif mode == Frameworks.VKWAVE:
            self._vkwave = importlib.import_module("vkwave")
            group_id = httpx.get(
                'https://api.vk.com/method/groups.getById', params={"access_token": token, "v": "5.92"}
            ).json()["response"][0]['id']
            self.bot = self._vkwave.bots.SimpleLongPollBot(tokens=token, group_id=group_id)
            self.inject_values = {self._vkwave.bots.SimpleLongPollBot: self.bot}

    def install(
        self, *, storage: Optional[BaseStorage] = None, default_state_name: Optional[str] = None, is_cached: bool = True
    ) -> None:
        storage = storage or redis.RedisStorage(StorageSettings())
        self.container.bind_constant(BaseStorage, storage)
        for class_, instance in self.inject_values.items():
            self.container.bind_constant(class_, instance)

        if self.mode == Frameworks.AIOGRAM:
            logger.info(f"Install AiogramMainRouter")
            from state_manager.event_processors.aiogram import AiogramEventProcessor
            AiogramEventProcessor.install(self.dp, self.storage, storage, default_state_name, is_cached)
        elif self.mode == Frameworks.VKWAVE:
            from state_manager.event_processors.vkwave import VkWaveEventProcessor
            VkWaveEventProcessor.install(self.bot, self.storage, storage, default_state_name, is_cached)

        logger.debug(f"install, storage={storage}, default_state_name={default_state_name}, is_cached={is_cached}")

    def start(self):
        if self.mode == Frameworks.AIOGRAM:
            self._aiogram.utils.executor.start_polling(self.dp, skip_updates=True)
        elif self.mode == Frameworks.VKWAVE:
            self.bot.run_forever()
