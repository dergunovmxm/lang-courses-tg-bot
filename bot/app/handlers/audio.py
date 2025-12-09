from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command, ContentTypeFilter
from aiogram.types import Message
import asyncio
import logging
logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("audio"))
async def cmd_start(message: Message):
    await message.answer("Пришлите голосовое сообщение!")

@router.message(lambda message: message.voice is not None)
async def handle_voice(message: Message):
    voice = message.voice
    await message.reply(f"Получено голосовое сообщение!\n"
                        f"ID файла: {voice.file_id}\n"
                        f"Длительность: {voice.duration} сек\n"
                        f"Размер (байт): {voice.file_size}")


def get_audio_handler():
    return router