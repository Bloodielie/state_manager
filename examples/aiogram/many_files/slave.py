from aiogram import types

from state_manager.routes.aiogram import AiogramStateRouter, AiogramStateManager

state_router = AiogramStateRouter()


@state_router.message_handler()
async def home(msg: types.Message, state_manager: AiogramStateManager):
    await msg.answer("go to home2")
    await state_manager.set_next_state("home2")


@state_router.message_handler()
async def home2(msg: types.Message, state_manager: AiogramStateManager):
    await msg.answer("go to home")
    await state_manager.set_next_state("home")
