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

router = Router()
class AudioTaskState(StatesGroup):
    waiting_for_voice = State()
@router.message(Command("audio"))
async def send_audio_task(message: Message, state: FSMContext):
    task = postgresql_client.get_audio_task()
    await message.answer(f"📍{task['question']}")
    await state.set_state(AudioTaskState.waiting_for_voice)
    await state.update_data(task=task)

@router.message(lambda message: message.voice is not None)
async def handle_voice(message: Message, state:FSMContext):
    voice = message.voice
    data = await state.get_data()
    

    txt = await transcribe_audio_v2(message.bot, voice)
    print(txt)
    task = data.get("task")
    cost = task.get("cost", 0)
    s=0
    for i in task['variants']:
        if i in txt:
            s+=1
    if s >=7:
        new_points = postgresql_client.add_points(
            user_id=message.from_user.id,
            points=cost
        )
        result_text = (
            "✅ Верно!\n\n"
            f"📊 +<b>{cost}</b> поинтов\n"
        )
    else:
        result_text = ('❌ Неверно. Попробуйте еще раз.')
    await message.answer(result_text, parse_mode='HTML')
    await state.clear()



def get_audio_handler():
    return router