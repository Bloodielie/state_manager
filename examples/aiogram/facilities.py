import logging

from aiogram import Bot, Dispatcher, executor

from state_manager import AiogramStateManager, MemoryStorage
from state_manager.routes.aiogram import AiogramMainRouter

logging.basicConfig(level=logging.INFO)

bot = Bot(token='your token')
dp = Dispatcher(bot)
main_state = AiogramMainRouter(dp)
main_state.install(storage=MemoryStorage())


@main_state.message_handler(state_name=["home", "home3"])
async def home(state_manager: AiogramStateManager):
    state = await state_manager.current_state
    if state == "home3":
        await state_manager.set_next_state("home")
        return "go to home"
    await state_manager.set_next_state("home2")
    return "go to home2"


@main_state.message_handler()
async def home2(state_manager: AiogramStateManager):
    await state_manager.set_next_state("home3")
    return "go to home3"


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
