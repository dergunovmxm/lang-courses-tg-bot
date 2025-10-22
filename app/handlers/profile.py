from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.crud import user_crud, settings_crud
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("profile"))
async def handle_profile(message: Message):

    #Обработчик команды /profile - показывает профиль пользователя
    
    user = message.from_user
    
    try:
        # Получаем или создаем пользователя
        db_user = user_crud.get_or_create_user(
            user.id, 
            user.username or "", 
            user.first_name, 
            user.last_name, 
            user.language_code or 'ru'
        )
        
        if not db_user:
            await message.answer("❌ Произошла ошибка при загрузке профиля")
            return

        
        # Получаем настройки
        settings = settings_crud.get_user_settings(user.id)
        if not settings:
            settings = settings_crud.create_default_settings(user.id)
        
        # Формируем сообщение
        profile_text = f"👤 <b>Профиль пользователя</b>\n\n"
        profile_text += f"🆔 ID: <code>{user.id}</code>\n"
        profile_text += f"👤 Имя: {user.first_name}\n"
        if user.username:
            profile_text += f"📱 Username: @{user.username}\n"
        
        if settings:
            profile_text += f"🔔 Уведомления: {'Включены' if settings.notification_enabled else 'Выключены'}\n"
            profile_text += f"⏰ Напоминание: {settings.daily_reminder_time}\n"
            profile_text += f"🎯 Уровень: {settings.language_level}\n"
            profile_text += f"🌍 Язык: {settings.target_language}\n\n"
        
        await message.answer(profile_text, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Ошибка в handle_profile: {e}")
        await message.answer("❌ Произошла ошибка при загрузке профиля")

def get_profile_handler():
    return router