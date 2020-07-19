from vkwave.bots import SimpleLongPollBot

import logging

from state_manager import MemoryStorage
from state_manager.filters.base import BaseFilter
from state_manager.models.dependencys.vkwave import VkWaveStateManager
from state_manager.routes.vkwave import VkWaveMainRouter

logging.basicConfig(level=logging.INFO)


bot = SimpleLongPollBot(tokens="your token", group_id=123123,)
main_state = VkWaveMainRouter(bot)


async def filter_1(event: bot.SimpleBotEvent):
    # can use asynchronous and synchronous functions
    return event.object.object.message.geo is None


class ExampleFilter(BaseFilter):
    async def check(self, event: bot.SimpleBotEvent) -> bool:
        # can use asynchronous and synchronous method
        return event.object.object.message.update_time is None


@main_state.message_handler(filter_1)
async def home(event: bot.SimpleBotEvent, state_manager: VkWaveStateManager):
    await event.answer("go to home2")
    await state_manager.set_next_state("home2")


@main_state.message_handler(ExampleFilter())
async def home2(event: bot.SimpleBotEvent, state_manager: VkWaveStateManager):
    await event.answer("go to home")
    await state_manager.back_to_pre_state()


main_state.install(storage=MemoryStorage())
bot.run_forever(ignore_errors=True)
