from vkwave.bots import SimpleLongPollBot

import logging

from state_manager import MemoryStorage
from state_manager.models.state_managers.vkwave import VkWaveStateManager
from state_manager.routes.vkwave import VkWaveMainStateRouter

logging.basicConfig(level=logging.INFO)


bot = SimpleLongPollBot(tokens="your token", group_id=123123,)
main_state = VkWaveMainStateRouter(bot)


@main_state.message_handler()
async def home(event: bot.SimpleBotEvent, state_manager: VkWaveStateManager):
    await event.answer("go to home2")
    await state_manager.set_next_state("home2", data="Test data")


@main_state.message_handler()
async def home2(event: bot.SimpleBotEvent, state_manager: VkWaveStateManager):
    print(await state_manager.data)
    await event.answer("go to home")
    await state_manager.back_to_pre_state()


main_state.install(storage=MemoryStorage())
bot.run_forever(ignore_errors=True)
