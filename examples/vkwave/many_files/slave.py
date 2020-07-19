from vkwave.bots.addons.easy.base_easy_bot import SimpleBotEvent

from state_manager.models.dependencys.vkwave import VkWaveStateManager
from state_manager.routes.vkwave import VkWaveRouter

state_router = VkWaveRouter()


@state_router.message_handler()
async def home(event: SimpleBotEvent, state_manager: VkWaveStateManager):
    await event.answer("go to home2")
    await state_manager.set_next_state("home2")


@state_router.message_handler()
async def home2(event: SimpleBotEvent, state_manager: VkWaveStateManager):
    await event.answer("go to home")
    await state_manager.back_to_pre_state()
