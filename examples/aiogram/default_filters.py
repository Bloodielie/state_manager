import logging

from aiogram import Bot, Dispatcher, executor, types

from state_manager import MemoryStorage
from state_manager.routes.aiogram import AiogramMainStateRouter, AiogramStateManager
from state_manager.filters.aiogram import text_filter, text_contains_filter, regex_filter

logging.basicConfig(level=logging.INFO)

bot = Bot(token='your token')
dp = Dispatcher(bot)
main_state = AiogramMainStateRouter(dp)
main_state.install(storage=MemoryStorage())


@main_state.message_handler(text_filter("111"))
async def home(msg: types.Message, state_manager: AiogramStateManager):
    await msg.answer("go to home2")
    await state_manager.set_next_state("home2")


@main_state.message_handler(text_contains_filter("yes"))
async def home2(msg: types.Message, state_manager: AiogramStateManager):
    await msg.answer("go to home")
    await state_manager.set_next_state("home")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
