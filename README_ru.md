# StateManager - fsm for people
> Удобная реализация FSM для telegram/vk
___
## Установка
`Поддерживает python3.7+`

Только библиотеку
```sh
pip install state-manager
```
Библиотека и vkwave
```sh
pip install state-manager[vk]
```
Библиотека и aiogram
```sh
pip install state-manager[telegram]
```
Полная установка
```sh
pip install state-manager[full]
```

## Примеры

[VkWave](https://github.com/fscdev/vkwave)
```python
from vkwave.bots import SimpleLongPollBot
import logging
from state_manager.routes.vkwave import VkWaveMainStateRouter, VkWaveStateManager

logging.basicConfig(level=logging.INFO)

bot = SimpleLongPollBot(tokens="your token", group_id=123123,)
main_state = VkWaveMainStateRouter(bot)

@main_state.message_handler()
async def home(event: bot.SimpleBotEvent, state_manager: VkWaveStateManager):
    await event.answer("go to home2")
    await state_manager.set_next_state("home2")

@main_state.message_handler()
async def home2(event: bot.SimpleBotEvent, state_manager: VkWaveStateManager):
    await event.answer("go to home")
    await state_manager.back_to_pre_state()

main_state.install()
bot.run_forever(ignore_errors=True)
```
[Aiogram](https://github.com/aiogram/aiogram/)
```python
import logging
from aiogram import Bot, Dispatcher, executor, types
from state_manager.routes.aiogram import AiogramMainStateRouter, AiogramStateManager

logging.basicConfig(level=logging.INFO)

bot = Bot(token='your token')
dp = Dispatcher(bot)
main_state = AiogramMainStateRouter(dp)
main_state.install()

@main_state.message_handler()
async def home(msg: types.Message, state_manager: AiogramStateManager):
    await msg.answer("go to home2")
    await state_manager.set_next_state("home2")

@main_state.message_handler()
async def home2(msg: types.Message, state_manager: AiogramStateManager):
    await msg.answer("go to home")
    await state_manager.set_next_state("home")

executor.start_polling(dp, skip_updates=True)
```
[more examples](https://github.com/Bloodielie/state_manager/tree/master/examples)

## Хранилища состояний
На данный момент библиотека поддерживает:
- RedisStorage
- MemoryStorage

Если не передать аргументы в install используется Redis Storage, который берет настройки из env.
Настройки:
- storage_dsn, default: "redis://localhost:6379"
- storage_ssl, default: None
- storage_db: default: None
- pool_size: default: 10
- storage_timeout: default: 5

## Фильтры
Библиотека поддерживает из коробки:
- text_filter
- text_contains_filter
- regex_filter

Также вы можете написать свои фильтры.  
[aiogram](https://github.com/Bloodielie/state_manager/tree/master/examples/aiogram/their_filters.py), [vkwave](https://github.com/Bloodielie/state_manager/tree/master/examples/vkwave/their_filters.py)

## TODO  

- [ ] Middleware
- [ ] SyncEvent
- [ ] поддержка VkBottle
