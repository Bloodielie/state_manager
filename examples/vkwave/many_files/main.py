from vkwave.bots import SimpleLongPollBot

from slave import state_router

import logging

from state_manager import VkWaveMainRouter

logging.basicConfig(level=logging.INFO)


bot = SimpleLongPollBot(tokens="your token", group_id=123123,)
main_state = VkWaveMainRouter(bot)
main_state.include_router(state_router)


main_state.install()
bot.run_forever(ignore_errors=True)
