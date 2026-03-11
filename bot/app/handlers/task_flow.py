from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery
)
from aiogram.fsm.context import FSMContext
from database.connection import postgresql_client
from intelligence.record_vm import transcribe_audio_v2
import json
import logging
from .testing import TestStates
from database.crud import settings_crud

logger = logging.getLogger(__name__)
router = Router(name="task_flow_router")

# /task — отправка задания

@router.message(F.text == "/task")
async def send_task(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.chat.id
    settings = settings_crud.get_settings(user_id)
    if not settings:
        settings = settings_crud.create_default_settings(user_id)
    level = settings.get('language_level', 0)
    
    db_level = 'A1' if level == 'beginner' else level
    task = postgresql_client.get_task_by_level(db_level)
    if not task:
        await message.answer("❌ Заданий пока нет", reply_markup=ReplyKeyboardRemove())
        return

    task_type = task.get("type", "text")

    await state.update_data(
        task_id=task["id"],
        correct_answer=str(task.get("answer", "")).strip().lower(),
        task_type=task_type,
        solution=task.get("solution"),
        theme=task.get("theme"),
        cost=int(task.get("cost", 0)),
        variants=task.get("variants", []),
        is_checking=False
    )

    question_text = f'<b>{task["theme"]}.</b>\n📍{task["question"]}'

    #multiple_choice
    if task_type == "multiple_choice":
        variants = task.get("variants", [])
        if isinstance(variants, str):
            try:
                variants = json.loads(variants)
            except Exception:
                logger.warning("Не удалось распарсить variants")
                variants = []
        if not variants:
            variants = [task.get("answer")]

        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=str(v))] for v in variants],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer(question_text, reply_markup=keyboard, parse_mode='HTML')

    #audio
    elif task_type == "audio_question":
        audio_text = f'<b>Speaking part.</b>\n\n📍{task["question"]}\n\n🎙️ Запишите голосовое сообщение с ответом'
        await message.answer(
            audio_text,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='HTML'
        )

    #text (default)
    else:
        await message.answer(question_text, reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')

    await state.set_state(TestStates.awaiting_start_confirmation)


def get_next_stop_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="⏭️ Next", callback_data="next_task"),
            InlineKeyboardButton(text="⏹️ Stop", callback_data="stop_task")
        ]]
    )


# Обработка текстового ответа

@router.message(TestStates.awaiting_start_confirmation, F.text)
async def check_answer(message: Message, state: FSMContext):
    data = await state.get_data()

    if data.get("is_checking"):
        await message.answer("⏳ Подождите, ответ уже проверяется.")
        return

    await state.update_data(is_checking=True)

    user_answer = message.text.strip().lower()
    correct_answer = data["correct_answer"]
    solution = data.get("solution")
    cost = data.get("cost", 0)

    processing_msg = await message.answer("⏳ Ответ на проверке...")
    is_correct = user_answer == correct_answer

    if is_correct:
        postgresql_client.add_points(user_id=message.from_user.id, points=cost)
        result_text = f"✅ Верно!\n\n📊 +<b>{cost}</b> поинтов\n"
    else:
        explanation = solution.strip() if solution else f"Правильный ответ: {correct_answer}"
        result_text = f"❌ Неверно.\n<b>Правильный ответ:</b> {correct_answer}\n<b>Объяснение:</b>\n{explanation}"

    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
    except Exception:
        pass

    await message.answer(result_text, reply_markup=get_next_stop_keyboard(), parse_mode='HTML')
    await state.set_state(TestStates.awaiting_next_action)


# Обработка голосового ответа 
@router.message(TestStates.awaiting_start_confirmation, F.voice)
async def check_audio_answer(message: Message, state: FSMContext):
    data = await state.get_data()

    if data.get("task_type") != "audio_question":  # было "audio"
        await message.answer("✍️ Для этого задания нужен текстовый ответ.")
        return

    if data.get("is_checking"):
        await message.answer("⏳ Подождите, ответ уже проверяется.")
        return

    await state.update_data(is_checking=True)
    processing_msg = await message.answer("⏳ Распознаём речь...")

    try:
        txt = await transcribe_audio_v2(message.bot, message.voice)
        logger.info(f"Транскрипция: {txt}")
    except Exception as e:
        logger.error(f"Ошибка транскрипции: {e}")
        await message.bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        await state.update_data(is_checking=False)
        await message.answer("⚠️ Не удалось распознать речь. Попробуйте ещё раз.")
        return

    variants = data.get("variants", [])
    cost = data.get("cost", 0)

    matched = sum(1 for word in variants if word in txt)
    is_correct = matched >= 7

    if is_correct:
        postgresql_client.add_points(user_id=message.from_user.id, points=cost)
        result_text = f"✅ Верно!\n\n📊 +<b>{cost}</b> поинтов\n"
    else:
        result_text = "❌ Неверно. Попробуйте ещё раз."

    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
    except Exception:
        pass

    await message.answer(result_text, reply_markup=get_next_stop_keyboard(), parse_mode='HTML')
    await state.set_state(TestStates.awaiting_next_action)


# /audio — отдельная команда (без изменений)
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup


class AudioTaskState(StatesGroup):
    waiting_for_voice = State()


@router.message(Command("audio"))
async def send_audio_task(message: Message, state: FSMContext):
    user = message.from_user
    settings = settings_crud.get_settings(user.id)
    if not settings:
        settings = settings_crud.create_default_settings(user.id)
    level = settings.get('language_level', 0)
    db_level = 'A1' if level == 'beginner' else level  # добавлено
    print(f"Запрашиваю задание для уровня: {repr(db_level)}")
    task = postgresql_client.get_audio_task(level=db_level)  # передаём уровень
    print(f"Получено задание: id={task.get('id')}, level={task.get('level')}, type={task.get('type')}")
    if not task:
        await message.answer("❌ Аудиозаданий пока нет")
        return

    await message.answer(f"📍{task['question']}\n\n🎙️ Запишите голосовое сообщение с ответом")
    await state.set_state(AudioTaskState.waiting_for_voice)
    await state.update_data(task=task)


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
    matched = sum(1 for word in task.get("variants", []) if word in txt)

    if matched >= 7:
        postgresql_client.add_points(user_id=message.from_user.id, points=cost)
        result_text = f"✅ Верно!\n\n📊 +<b>{cost}</b> поинтов\n"
    else:
        result_text = "❌ Неверно. Попробуйте ещё раз."

    await message.answer(result_text, parse_mode='HTML')
    await state.clear()

# Next / Stop
@router.callback_query(F.data == "next_task", TestStates.awaiting_next_action)
async def handle_next_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(user_id=callback.from_user.id)
    await send_task(callback.message, state)


@router.callback_query(F.data == "stop_task", TestStates.awaiting_next_action)
async def handle_stop_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer(
        "Хорошая работа! Возвращайся и зарабатывай поинты😉",
        reply_markup=ReplyKeyboardRemove()
    )


def get_task_handler():
    return router