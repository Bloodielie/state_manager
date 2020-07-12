from vkwave.bots import SimpleLongPollBot

import logging

from state_manager import VkWaveStateManager, VkWaveMainRouter

logging.basicConfig(level=logging.INFO)


bot = SimpleLongPollBot(tokens="your token", group_id=123123,)
main_state = VkWaveMainRouter(bot)


@main_state.message_handler(state_name=["home", "home3"])
async def home(state_manager: VkWaveStateManager):
    state = await state_manager.get_current_state
    if state == "home3":
        await state_manager.set_next_state("home")
        return "go to home"
    await state_manager.set_next_state("home2")
    return "go to home2"


@main_state.message_handler()
async def home2(state_manager: VkWaveStateManager):
    await state_manager.set_next_state("home3")
    return "go to home3"


main_state.install()
bot.run_forever(ignore_errors=True)
