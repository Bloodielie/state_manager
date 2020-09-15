from logging import getLogger
from typing import Optional, Union, Callable, Any, Dict

import httpx

from state_manager import BaseStorage
from state_manager.dependency.container import AppContainer
from state_manager.enums import Frameworks
from state_manager.handlers.aiogram import AiogramStateHandler, AiogramHandler
from state_manager.handlers.vkwave import VkWaveStateHandler, VkWaveHandler
from state_manager.storage_settings import StorageSettings
from state_manager.storages import redis
from state_manager.storages.state_storage import StateStorage

logger = getLogger(__name__)


class Router:
    def __init__(self, mode: Union[Frameworks, str] = Frameworks.AIOGRAM):
        self._state_storage = StateStorage()

        if mode == Frameworks.AIOGRAM:
            self.on_state = AiogramStateHandler(self._state_storage)
            self.on = AiogramHandler(self._state_storage)
        elif mode == Frameworks.VKWAVE:
            self.on_state = VkWaveStateHandler(self._state_storage)
            self.on = VkWaveHandler(self._state_storage)

    def include_router(self, router: "Router") -> None:
        logger.debug(f"include_router, router={router}")
        self._state_storage.expand(router._state_storage)


class MainRouter(Router):
    def __init__(self, token: str, mode: Union[Frameworks, str] = Frameworks.AIOGRAM) -> None:
        super().__init__(mode)
        self.container = AppContainer()
        self.mode = mode
        self._events: Dict[str, Optional[Callable[..., Any]]] = {"on_startup": None, "on_shutdown": None}

        if mode == Frameworks.AIOGRAM:
            from aiogram import Bot, Dispatcher
            bot = Bot(token=token)
            self.dp = Dispatcher(bot)
            self.inject_values = {Bot: bot, Dispatcher: self.dp}
        elif mode == Frameworks.VKWAVE:
            from vkwave.bots import TaskManager, SimpleLongPollBot
            self._task_manager = TaskManager()
            group_id = httpx.get(
                'https://api.vk.com/method/groups.getById', params={"access_token": token, "v": "5.92"}
            ).json()["response"][0]['id']
            self.bot = SimpleLongPollBot(tokens=token, group_id=group_id)
            self.inject_values = {SimpleLongPollBot: self.bot}

    def install(
        self, *, storage: Optional[BaseStorage] = None, default_state_name: Optional[str] = None
    ) -> None:
        storage = storage or redis.RedisStorage(StorageSettings())
        self.container.bind_constant(BaseStorage, storage)
        for class_, instance in self.inject_values.items():
            self.container.bind_constant(class_, instance)

        if self.mode == Frameworks.AIOGRAM:
            logger.info(f"Install AiogramMainRouter")
            from state_manager.event_processors.aiogram import AiogramEventProcessor
            AiogramEventProcessor.install(self.dp, self._state_storage, storage, default_state_name)
        elif self.mode == Frameworks.VKWAVE:
            from state_manager.event_processors.vkwave import VkWaveEventProcessor
            VkWaveEventProcessor.install(self.bot, self._state_storage, storage, default_state_name)

    def start(self) -> None:
        if self.mode == Frameworks.AIOGRAM:
            from aiogram.utils import executor
            executor.start_polling(
                self.dp,
                skip_updates=True,
                on_startup=self._events["on_startup"],
                on_shutdown=self._events["on_shutdown"]
            )
        elif self.mode == Frameworks.VKWAVE:
            self._task_manager.add_task(self.bot.run)
            self._task_manager.run(on_startup=self._events["on_startup"], on_shutdown=self._events["on_shutdown"])

    def run(
        self,
        *,
        storage: Optional[BaseStorage] = None,
        default_state_name: Optional[str] = None,
        on_startup: Optional[Callable[..., Any]] = None,
        on_shutdown: Optional[Callable[..., Any]] = None,
    ) -> None:
        if on_startup is not None:
            self.on_startup(on_startup)
        if on_shutdown is not None:
            self.on_shutdown(on_shutdown)

        self.install(storage=storage, default_state_name=default_state_name)
        self.run()

    def on_startup(self, func: Callable[..., Any]) -> None:
        self._events["on_startup"] = func

    def on_shutdown(self, func: Callable[..., Any]) -> None:
        self._events["on_shutdown"] = func
