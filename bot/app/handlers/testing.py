from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.connection import postgresql_client
import logging
import asyncio
import json
import time

logger = logging.getLogger(__name__)

class TestStates(StatesGroup):
    awaiting_start_confirmation = State()
    in_progress = State()
    awaiting_start_confirmation = State()
    awaiting_next_action = State() 


async def send_message_with_min_delay(message: Message, text: str, reply_markup=None, min_delay: float = 1.5):
    """Отправка сообщения с минимальной задержкой"""
    start_time = time.monotonic()
    await message.answer(text, reply_markup=reply_markup)
    elapsed = time.monotonic() - start_time
    remaining = min_delay - elapsed
    if remaining > 0:
        await asyncio.sleep(remaining)


def get_test_handler() -> Router:
    router = Router(name="test_router")

    async def load_tasks_from_db():
        """Загрузка задач из базы данных"""
        try:
            tasks = postgresql_client.select("tasks")
            logger.info(f"🔍 Загружено {len(tasks) if tasks else 0} заданий из PostgreSQL")
            
            if tasks:
                logger.info(f"Пример первого задания: {tasks[0]}")
            
            return tasks or []
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке заданий: {e}", exc_info=True)
            return []

    # Команда /test
    @router.message(F.text == "/test")
    async def start_test_handler(message: Message, state: FSMContext):
        """Запуск теста"""
        current_state = await state.get_state()

        # Если пользователь уже проходит тест — завершаем
        if current_state == TestStates.in_progress.state:
            await message.answer("⏹ Тестирование завершено досрочно.", reply_markup=ReplyKeyboardRemove())
            await state.clear()
            return
        
        try:
            tasks = await load_tasks_from_db()
            
            if not tasks:
                await send_message_with_min_delay(
                    message, 
                    "❌ Нет доступных заданий.",
                    reply_markup=ReplyKeyboardRemove()
                )
                return
                
        except Exception as e:
            logger.error(f"Ошибка при предзагрузке заданий: {e}")

        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await send_message_with_min_delay(message, "Начинаем тестирование?", reply_markup=kb)
        await state.set_state(TestStates.awaiting_start_confirmation)

    # Подтверждение начала теста 
    @router.message(TestStates.awaiting_start_confirmation, F.text.in_({"Да", "Нет"}))
    async def handle_confirmation(message: Message, state: FSMContext):
        if message.text == "Нет":
            await send_message_with_min_delay(message, "Хорошо, тест отменён.", reply_markup=ReplyKeyboardRemove())
            await state.clear()
            return

        try:
            tasks = await load_tasks_from_db()

            if not tasks:
                await send_message_with_min_delay(message, "❌ Нет доступных заданий.", reply_markup=ReplyKeyboardRemove())
                await state.clear()
                return
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке заданий: {e}")
            await send_message_with_min_delay(
                message, 
                "❌ Ошибка при загрузке заданий",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.clear()
            return
        
         # Сохраняем данные теста
        await state.update_data(
            tasks=tasks,
            current_index=0,
            correct_count=0,
            total=len(tasks),
            last_message_time=0,
            start_time=time.time()  # Запоминаем время начала теста
        )
        
        await send_next_task(message, state)

  
    async def send_next_task(message: Message, state: FSMContext):
        data = await state.get_data()
        tasks = data["tasks"]
        index = data["current_index"]

        if index >= len(tasks):
            correct = data["correct_count"]
            total = data["total"]
            await send_message_with_min_delay(
                message,
                f"✅ Тест завершён!\nПравильных ответов: {correct} из {total}.",
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

    # Обработка ответов
    @router.message(TestStates.in_progress)
    async def handle_answer(message: Message, state: FSMContext):
        user_answer = message.text.strip()

        # Досрочное завершение теста
        if user_answer.lower() == "/test":
            await message.answer("⏹ Тестирование завершено досрочно.", reply_markup=ReplyKeyboardRemove())
            await state.clear()
            return

        data = await state.get_data()
        last_message_time = data.get("last_message_time", 0)
        now = time.monotonic()

        # Защита от слишком быстрой отправки
        if now - last_message_time < 2:
            await message.answer("⚠️ Вы печатаете слишком быстро! Подождите немного ⏳")
            return

        await state.update_data(last_message_time=now)

        # Отправляем сообщение-заглушку
        processing_msg = await message.answer("⏳ Ответ принят, проверяю...")

        try:
            start_check_time = time.monotonic()  # Засекаем время начала проверки

            tasks = data["tasks"]
            index = data["current_index"]
            task = tasks[index]

            correct_answer = str(task.get("answer", "")).strip()
            is_correct = user_answer.lower() == correct_answer.lower()

            end_check_time = time.monotonic()
            check_duration = end_check_time - start_check_time  # сколько заняла проверка

            # Удаляем "Ответ принят..."
            await message.bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)

            # Если проверка была слишком быстрой (< 0.8 сек) — добавим небольшую задержку
            if check_duration < 0.8:
                await asyncio.sleep(2)

            # Отправляем результат
            if is_correct:
                await state.update_data(correct_count=data["correct_count"] + 1)
                await send_message_with_min_delay(message, "✅ Верно!")
            else:
                solution = task.get("solution") or f"Правильный ответ: {correct_answer}"
                await send_message_with_min_delay(message, f"❌ Неверно.\n{solution}")

            # Следующий вопрос
            await state.update_data(current_index=index + 1)
            await send_next_task(message, state)

        except Exception as e:
            logger.error(f"Ошибка при проверке ответа: {e}")
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
            except:
                pass
            await message.answer("❌ Ошибка при проверке ответа. Попробуйте снова.")

    return router