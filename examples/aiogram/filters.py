import logging

from aiogram import Bot, Dispatcher, executor, types

from state_manager import AiogramStateManager
from state_manager.routes.aiogram import AiogramMainRouter

logging.basicConfig(level=logging.INFO)

bot = Bot(token='your token')
dp = Dispatcher(bot)
main_state = AiogramMainRouter(dp)
main_state.install()


async def filter_1(msg: types.Message):
    return not msg.from_user.is_bot


def filter_2(msg: types.Message):
    return msg.from_user.language_code in ["ru", "en"]


@main_state.message_handler(filter_1)
async def home(msg: types.Message, state_manager: AiogramStateManager):
    await msg.answer("go to home2")
    await state_manager.set_next_state("home2")


@main_state.message_handler(filter_2)
async def home2(msg: types.Message, state_manager: AiogramStateManager):
    await msg.answer("go to home")
    await state_manager.set_next_state("home")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
