from vkwave.bots import SimpleLongPollBot

from slave import state_router

import logging

from state_manager import MemoryStorage
from state_manager.routes.vkwave import VkWaveMainStateRouter

logging.basicConfig(level=logging.INFO)


bot = SimpleLongPollBot(tokens="your token", group_id=123123,)
main_state = VkWaveMainStateRouter(bot)
main_state.include_router(state_router)


main_state.install(storage=MemoryStorage())
bot.run_forever(ignore_errors=True)
