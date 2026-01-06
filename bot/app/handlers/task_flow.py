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
import json
import logging
from .testing import TestStates

logger = logging.getLogger(__name__)

router = Router(name="task_flow_router")


# ============================
# /task — отправка задания
# ============================
@router.message(F.text == "/task")
async def send_random_task(message: Message, state: FSMContext):
    await state.clear()

    task = postgresql_client.get_random_task()

    if not task:
        await message.answer(
            "❌ Заданий пока нет",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    await state.update_data(
        task_id=task["id"],
        correct_answer=str(task.get("answer", "")).strip().lower(),
        task_type=task.get("type", "text"),
        solution=task.get("solution"),
        theme=task.get("theme"),
        cost=int(task.get("cost", 0)), 
        is_checking=False
    )

    if task.get("type") == "multiple_choice":
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
            keyboard=[
                [KeyboardButton(text=str(v))]
                for v in variants
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await message.answer(f'''
<b>{task['theme']}.</b>
📍{task["question"]}''',
                             reply_markup=keyboard, parse_mode='HTML')

    else:
        await message.answer(
            f'''
<b>{task['theme']}.</b>
📍{task["question"]}''',
            reply_markup=ReplyKeyboardRemove(), parse_mode='HTML'
        )

    await state.set_state(TestStates.awaiting_start_confirmation)
def get_next_stop_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⏭️ Next", callback_data="next_task"),
                InlineKeyboardButton(text="⏹️ Stop", callback_data="stop_task")
            ]
        ]
    )
@router.message(TestStates.awaiting_start_confirmation)
async def check_answer(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("✍️ Пожалуйста, отправьте текстовый ответ.")
        return

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
        new_points = postgresql_client.add_points(
            user_id=message.from_user.id,
            points=cost
        )
        result_text = (
            "✅ Верно!\n\n"
            f"📊 +<b>{cost}</b> поинтов\n"
        )
    else:
        explanation = (
            solution.strip()
            if solution
            else f"Правильный ответ: {correct_answer}"
        )
        result_text = f"""❌ Неверно.
<b>Правильный ответ:</b> {correct_answer}
<b>Объяснение:</b>
{explanation}
"""

    try:
        await message.bot.delete_message(
            chat_id=message.chat.id,
            message_id=processing_msg.message_id
        )
    except Exception:
        pass

    # Отправляем результат + inline-кнопки
    await message.answer(
        result_text,
        reply_markup=get_next_stop_keyboard(),
        parse_mode='HTML'
    )
    await state.set_state(TestStates.awaiting_next_action)

@router.callback_query(F.data == "next_task", TestStates.awaiting_next_action)
async def handle_next_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await send_random_task(callback.message, state)


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