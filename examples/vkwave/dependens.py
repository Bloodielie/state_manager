from vkwave.bots import SimpleLongPollBot

import logging

from state_manager import VkWaveMainRouter, VkWaveStateManager, Depends, MemoryStorage
from state_manager.storage.base import BaseStorage

logging.basicConfig(level=logging.INFO)


bot = SimpleLongPollBot(tokens="your token", group_id=123123,)
main_state = VkWaveMainRouter(bot)


async def test(state_manager: VkWaveStateManager):
    return await state_manager.data


@main_state.message_handler()
async def home(event: bot.SimpleBotEvent, state_manager: VkWaveStateManager, depends_result=Depends(test)):
    assert depends_result == (await state_manager.data) # True
    await event.answer("go to home2")
    await state_manager.set_next_state("home2")


@main_state.message_handler()
async def home2(event: bot.SimpleBotEvent, state_manager: VkWaveStateManager, storage: BaseStorage):
    print(storage)
    await event.answer("go to home")
    await state_manager.back_to_pre_state()


main_state.install(storage=MemoryStorage())
bot.run_forever(ignore_errors=True)
