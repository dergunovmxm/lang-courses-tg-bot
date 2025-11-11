from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from database.crud import user_crud
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(CommandStart())
async def handle_start(message: Message):
    """Обработчик команды /start"""
    user = message.from_user
    
    try:
        # Сохраняем/обновляем пользователя в Supabase
        db_user = user_crud.get_or_create_user(
            user.id, 
            user.username or "", 
            user.first_name, 
            user.last_name, 
            user.language_code or 'ru',
            message.chat.id,
        )
        
        if db_user:
            welcome_text = (
                f"Привет, {user.first_name}! 👋\n"
                'Добро пожаловать в GradeUp🎓\n\n'
                'Мы готовы помочь тебе в освоении иностранных языков!\n'
                "Начни прямо сейчас - приступай с заданиям и набирай очки💪\n\n"
                "📌Основные команды:\n"
                "/start - начать работу\n"
                "/profile - мой профиль\n" 
                "/timer - запустить таймер занятия\n"
                '/test - первое тестирование уровня языка\n'
                "/info - информация о боте\n\n"
                'Учись регулярно — и результат не заставит себя ждать!'
            )
        else:
            welcome_text = (
                f"Привет, {user.first_name}! 👋\n\n"
                "Произошла ошибка при сохранении ваших данных. "
                "Пожалуйста, попробуйте позже."
            )
        
        await message.answer(welcome_text)
        logger.info(f"Пользователь {user.id} запустил бота")
        
    except Exception as e:
        logger.error(f"Ошибка в handle_start: {e}")
        await message.answer("❌ Произошла ошибка при запуске бота")

# Функция для получения роутера (для совместимости с предыдущей структурой)
def get_start_handler():
    return router