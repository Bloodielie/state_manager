import logging

from aiogram import Bot, Dispatcher, executor

from slave import state_router

from state_manager import MemoryStorage
from state_manager.routes.aiogram.state import AiogramMainStateRouter

logging.basicConfig(level=logging.INFO)

bot = Bot(token='your token')
dp = Dispatcher(bot)

main_state = AiogramMainStateRouter(dp)
main_state.include_router(state_router)
main_state.install(storage=MemoryStorage())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
