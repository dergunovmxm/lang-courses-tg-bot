import sys
import os
from intelligence.record_vm import transcribe_audio_v2
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import asyncio
import logging
from database.connection import postgresql_client
logger = logging.getLogger(__name__)
from database.crud import settings_crud
router = Router()
class AudioTaskState(StatesGroup):
    waiting_for_voice = State()
@router.message(Command("audio"))
async def send_audio_task(message: Message, state: FSMContext):
    user = message.from_user
    settings = settings_crud.get_settings(user.id)
    if not settings:
        settings = settings_crud.create_default_settings(user.id)
    level = settings.get('language_level', 0)
    db_level = 'A1' if str(level).lower() == 'beginner' else str(level).upper()

    task = postgresql_client.get_audio_task(level=db_level)

    if not task:
        await message.answer("❌ Аудиозаданий пока нет")
        return

    await state.set_state(AudioTaskState.waiting_for_voice)
    await state.update_data(task=task)
    await message.answer(f"📍{task['question']}\n\n🎙️ Запишите голосовое сообщение с ответом")

@router.message(AudioTaskState.waiting_for_voice, F.voice)
async def handle_voice(message: Message, state: FSMContext):
    data = await state.get_data()
    task = data.get("task")

    if not task:
        await message.answer("⚠️ Задание не найдено. Начните заново: /audio")
        await state.clear()
        return

    try:
        txt = await transcribe_audio_v2(message.bot, message.voice)
        logger.info(f"Транскрипция /audio: {txt}")
    except Exception as e:
        logger.error(f"Ошибка транскрипции: {e}")
        await message.answer("⚠️ Не удалось распознать речь. Попробуйте ещё раз.")
        return

    cost = task.get("cost", 0)
    variants = task.get("variants", [])
    if isinstance(variants, str):
        try:
            variants = json.loads(variants)
        except Exception:
            variants = []

    matched = sum(1 for word in variants if word in txt)

    if matched >= 7:
        postgresql_client.add_points(user_id=message.from_user.id, points=cost)
        result_text = f"✅ Верно!\n\n📊 +<b>{cost}</b> поинтов\n"
    else:
        result_text = "❌ Неверно. Попробуйте ещё раз."

    await message.answer(result_text, parse_mode='HTML')
    await state.clear()



def get_audio_handler():
    return router