from vkwave.bots import SimpleLongPollBot

import logging

from state_manager import VkWaveMainRouter, VkWaveStateManager, MemoryStorage
from state_manager.filters.vkwave import text_filter, text_contains_filter, regex_filter

logging.basicConfig(level=logging.INFO)


bot = SimpleLongPollBot(tokens="your token", group_id=123123,)
main_state = VkWaveMainRouter(bot)


@main_state.message_handler(text_filter("111"))
async def home(event: bot.SimpleBotEvent, state_manager: VkWaveStateManager):
    await event.answer("go to home2")
    await state_manager.set_next_state("home2")


@main_state.message_handler(text_contains_filter("yes"))
async def home2(event: bot.SimpleBotEvent, state_manager: VkWaveStateManager):
    await event.answer("go to home")
    await state_manager.back_to_pre_state()


main_state.install(storage=MemoryStorage())
bot.run_forever(ignore_errors=True)
