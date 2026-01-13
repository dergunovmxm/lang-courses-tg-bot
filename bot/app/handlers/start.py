from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.crud import user_crud, settings_crud
import logging
from app.handlers.testing import initiate_test
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import F
logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def handle_start(message: Message):
    user = message.from_user

    try:
        # 1. Создаём / обновляем пользователя
        db_user = user_crud.get_or_create_user(
            user.id,
            user.username or "",
            user.first_name,
            user.last_name,
            user.language_code or "ru",
            message.chat.id,
        )

        if not db_user:
            await message.answer("❌ Ошибка сохранения данных пользователя.")
            return

        # 2. Отправляем приветствие
        await message.answer(
            f"Привет, {user.first_name}! 👋\n"
            "Добро пожаловать в GradeUp 🎓\n\n"
            "Мы поможем тебе прокачать иностранные языки 💪\n\n"
            "📌 Основные команды:\n"
            "/task — задание дня\n"
            "/profile — мой профиль\n"
            "/timer — таймер занятия\n"
            "/test — тестирование уровня языка\n"
            "/audio — распознавание голоса\n"
            "/info — информация о боте"
        )

        # 3. Получаем или создаём настройки
        settings = settings_crud.get_settings(user.id)

        if not settings:
            settings = settings_crud.create_default_settings(user.id)

        test_btn = InlineKeyboardButton(text='Пройти тест', callback_data='initiate_test')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[test_btn]])
        # 4. Если уровень beginner — предлагаем тест
        if settings and settings.get("language_level") == "beginner":
            await message.answer(
                "👀 Я вижу, что твой уровень языка пока не определён.\n\n"
                "📊 Рекомендую пройти короткое тестирование, "
                "чтобы я подбирал задания именно под тебя.", reply_markup=keyboard)

        logger.info(f"Пользователь {user.id} запустил бота")

    except Exception as e:
        logger.error(f"Ошибка в handle_start: {e}")
        await message.answer("❌ Произошла ошибка при запуске бота")
@router.callback_query(F.data == "initiate_test")
async def handle_initiate_test(callback: CallbackQuery, state: FSMContext):
    # Убираем кнопку, чтобы не нажимали дважды
    await callback.message.edit_reply_markup(reply_markup=None)
    # Запускаем тест
    await initiate_test(callback.message, state)
    # Подтверждаем нажатие (убираем "часики" у пользователя)
    await callback.answer()

def get_start_handler():
    return router