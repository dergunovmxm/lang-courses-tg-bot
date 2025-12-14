import sys
import os
from intelligence.record_vm import transcribe_audio_v2
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
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
    txt = await transcribe_audio_v2(message.bot, voice)
    await message.reply(f"Получено голосовое сообщение!\n"
                        f"ID файла: {voice.file_id}\n"
                        f"Длительность: {voice.duration} сек\n"
                        f"Размер (байт): {voice.file_size}\n"
                        f"Распознанный текст: {txt}")

def get_audio_handler():
    return router