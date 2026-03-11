# app/handlers/testing.py

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.connection import postgresql_client
from database.crud import settings_crud
import logging
import asyncio
import json
import time
import random

logger = logging.getLogger(__name__)

router = Router()
# === Состояния теста ===
class TestStates(StatesGroup):
    awaiting_start_confirmation = State()
    in_progress = State()
    awaiting_next_action = State()  # оставляем, так как используется в task_flow.py


# === Вспомогательные функции ===

async def send_message_with_min_delay(
    message: Message, 
    text: str, 
    reply_markup=None, 
    min_delay: float = 1.5
):
    start_time = time.monotonic()
    await message.answer(text, reply_markup=reply_markup)
    elapsed = time.monotonic() - start_time
    remaining = min_delay - elapsed
    if remaining > 0:
        await asyncio.sleep(remaining)


async def load_tasks_from_db():
    tasks = postgresql_client.select(
        "tasks",
        condition="type != 'audio_question'"
    )

    logger.error("=== DEBUG TASKS ===")
    logger.error(f"TOTAL FROM PYTHON: {len(tasks)}")

    from collections import Counter
    levels = Counter(t["level"] for t in tasks)
    logger.error(f"LEVELS FROM PYTHON: {levels}")
    logger.error("===================")

    return tasks or []


def normalize_level(value: str) -> str:
    return str(value).replace("\u00a0", "").strip().upper()


def select_random_tasks(tasks, count_per_level=3):
    """Выбирает случайно count_per_level заданий для каждого уровня и перемешивает все"""
    levels = ["A1", "A2", "B1", "B2", "C1"]
    selected = []

    for level in levels:
        # фильтруем по нормализованному уровню
        level_tasks = [t for t in tasks if normalize_level(t.get("level")) == level and t.get("type") != "audio_question"]
        if len(level_tasks) < count_per_level:
            logger.warning(f"Не хватает заданий уровня {level}, есть {len(level_tasks)}")
        selected.extend(random.sample(level_tasks, min(count_per_level, len(level_tasks))))

    random.shuffle(selected)
    return selected


def determine_language_level(total_score: int) -> str:
    if total_score <= 40:
        return "A1"
    elif total_score <= 130:
        return "A2"
    elif total_score <= 260:
        return "B1"
    elif total_score <= 430:
        return "B2"
    else:
        return "C1"


# === Основная логика запуска теста ===

async def initiate_test(message: Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="start_test_yes"),
         InlineKeyboardButton(text="Нет", callback_data="start_test_no")]
    ])
    await message.answer("Начинаем тестирование?", reply_markup=kb)
    await state.set_state(TestStates.awaiting_start_confirmation)


# === Роутер ===

def get_test_handler() -> Router:
    router = Router(name="test_router")

    @router.message(F.text == "/test")
    async def start_test_handler(message: Message, state: FSMContext):
        await initiate_test(message, state)

    @router.message(TestStates.awaiting_start_confirmation, F.text.in_({"Да", "Нет"}))
    async def handle_confirmation(message: Message, state: FSMContext):
        if message.text == "Нет":
            await send_message_with_min_delay(message, "Хорошо, тест отменён.", reply_markup=ReplyKeyboardRemove())
            await state.clear()
            return

        all_tasks = await load_tasks_from_db()
        if not all_tasks:
            await send_message_with_min_delay(message, "❌ Нет доступных заданий.", reply_markup=ReplyKeyboardRemove())
            await state.clear()
            return

        # === Формирование уникального набора заданий на каждый запуск ===
        selected_tasks = select_random_tasks(all_tasks, count_per_level=3)

        if len(selected_tasks) < 15:
            logger.warning(f"Не хватает заданий для полного теста: всего {len(selected_tasks)}")

        await state.update_data(
            tasks=selected_tasks,
            current_index=0,
            total_score=0,
            total=len(selected_tasks),
            last_message_time=0,
            start_time=time.time()
        )

        await send_next_task(message, state)

    async def send_next_task(message: Message, state: FSMContext):
        data = await state.get_data()
        tasks = data["tasks"]
        index = data["current_index"]

        if index >= len(tasks):
            total_score = data["total_score"]
            level = determine_language_level(total_score)
            user_id = message.from_user.id
            settings_crud.update_language_level(user_id, level)
            await send_message_with_min_delay(
                message,
                f"✅ Тест завершён!\n\n"
                f"Набрано баллов: {total_score}\n"
                f"Ваш уровень: {level} 🎯",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.clear()
            return

        task = tasks[index]

        if task.get("type") == "multiple_choice":
            variants = task.get("variants")
            if isinstance(variants, str):
                try:
                    options = json.loads(variants)
                except Exception as e:
                    logger.error(f"Ошибка парсинга variants: {e}")
                    options = []
            elif isinstance(variants, list):
                options = variants
            else:
                options = []

            if not options:
                options = [task.get("answer", "Ответ"), "Вариант 2", "Вариант 3", "Вариант 4"]

            kb = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=str(opt))] for opt in options],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            await send_message_with_min_delay(message, task.get("question", "Вопрос отсутствует"), reply_markup=kb)
        else:
            await send_message_with_min_delay(message, task.get("question", "Вопрос отсутствует"), reply_markup=ReplyKeyboardRemove())

        await state.set_state(TestStates.in_progress)
    @router.callback_query(F.data.in_({"start_test_yes", "start_test_no"}))
    async def handle_start_test_confirmation(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_reply_markup(None)

        if callback.data == "start_test_no":
            await callback.message.answer("Тест отменён.", reply_markup=ReplyKeyboardRemove())
            await state.clear()
            return

        # Если "Да" — формируем задания
        all_tasks = await load_tasks_from_db()
        if not all_tasks:
            await callback.message.answer("❌ Нет доступных заданий.", reply_markup=ReplyKeyboardRemove())
            await state.clear()
            return

        selected_tasks = select_random_tasks(all_tasks, count_per_level=3)
        await state.update_data(
            tasks=selected_tasks,
            current_index=0,
            total_score=0,
            total=len(selected_tasks),
            last_message_time=0,
            start_time=time.time()
        )

        # После того, как данные есть — запускаем первое задание
        await send_next_task(callback.message, state)
        await callback.answer()
    @router.message(TestStates.in_progress)
    async def handle_answer(message: Message, state: FSMContext):
        user_answer = message.text.strip()

        if user_answer.lower() == "/test":
            await message.answer("⏹ Тестирование завершено досрочно.", reply_markup=ReplyKeyboardRemove())
            await state.clear()
            return

        data = await state.get_data()
        last_message_time = data.get("last_message_time", 0)
        now = time.monotonic()

        if now - last_message_time < 2:
            await message.answer("⚠️ Вы печатаете слишком быстро! Подождите немного ⏳")
            return

        await state.update_data(last_message_time=now)
        processing_msg = await message.answer("⏳ Ответ принят, проверяю...")

        try:
            tasks = data["tasks"]
            index = data["current_index"]
            task = tasks[index]
            correct_answer = str(task.get("answer", "")).strip()
            is_correct = user_answer.lower() == correct_answer.lower()

            await message.bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)

            cost = int(task.get("cost", 0)) if is_correct else 0
            new_total_score = data["total_score"] + cost
            await state.update_data(total_score=new_total_score)

            if is_correct:
                await send_message_with_min_delay(message, "✅ Верно!")
            else:
                solution = task.get("solution") or f"Правильный ответ: {correct_answer}"
                await send_message_with_min_delay(message, f"❌ Неверно.\n{solution}")

            await state.update_data(current_index=index + 1)
            await send_next_task(message, state)

        except Exception as e:
            logger.error(f"Ошибка при проверке ответа: {e}")
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
            except Exception:
                pass
            await message.answer("❌ Ошибка при проверке ответа. Попробуйте снова.")
         

    return router
