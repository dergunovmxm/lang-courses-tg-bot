from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
import asyncio

from config import TOKEN

router = Router()
bot = Bot(token=TOKEN)

@router.message(Command('timer'))
async def message_sender(message: Message):
    counter = 1
    chat_id = message.chat.id

    try:
        await message.answer("Таймер запущен! Каждую минуту буду присылать сообщение.")
        
        while True:
            await bot.send_message(chat_id, f"🔔 Минута №{counter} прошла!")
            await asyncio.sleep(60)
            counter += 1
    except asyncio.CancelledError:
        await bot.send_message(chat_id, 'Таймер остановлен!')
        raise
    except Exception as e:
        await bot.send_message(chat_id, f'Произошла ошибка: {e}')