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
        db_user = user_crud.get_user_by_telegram_id(user.id)
        if not db_user:
            #await message.answer("❌ Произошла ошибка при загрузке профиля")
            #return
            db_user = user_crud.create_user(user.id, user.username, user.first_name, user.last_name)

        # Получаем настройки
        settings = settings_crud.get_settings(user.id)
        if not settings:
            settings = settings_crud.create_default_settings(user.id)
        
        # Формируем сообщение
        profile_text = f"👤 <b>Профиль пользователя</b>\n\n"
        profile_text += f"🆔 ID: <code>{user.id}</code>\n"
        profile_text += f"👤 Имя: {user.first_name}\n"
        if user.username:
            profile_text += f"📱 Username: @{user.username}\n"
        
        if settings and isinstance(settings, dict):
            notific = settings.get('notifications_enabled')
            if notific is None:
                notific_text = 'Не задано'
            else:
                notific_text = 'Включены' if bool(notific) else 'Выключены'
            profile_text += f"🔔 Уведомления: {notific_text}\n"
            profile_text += f"⏰ Напоминание: {settings.get('daily_reminder_time', '-')}\n"
            profile_text += f"🎯 Уровень: {settings.get('language_level', '-')}\n"
            profile_text += f"🌍 Язык: {settings.get('target_language', '-')}\n\n"
            profile_text += f"📊 <b>Поинты: {db_user.get('points', 0)}</b>"
        
        await message.answer(profile_text, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Ошибка в handle_profile: {e}")
        await message.answer("❌ Произошла ошибка при загрузке профиля")

def get_profile_handler():
    return router