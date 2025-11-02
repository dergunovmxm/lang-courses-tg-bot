from .supabase_client import supabase_client
from .models import User, UserSettings
from typing import Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class UserCRUD:
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        try:
            result = supabase_client.select('users', {'telegram_id': telegram_id})  # только 2 позиции
            if result and len(result) > 0:
                return User.from_dict(result[0])
            return None
        except Exception as e:
            logger.error(f"Ошибка получения пользователя {telegram_id}: {e}")
            return None

    def create_user(self, telegram_id: int, username: str, first_name: str, last_name: str = None, language_code: str = 'ru', chat_id: Optional[int] = None) -> Optional[User]:
        try:
            data = {
                'telegram_id': telegram_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'language_code': language_code,
                'chat_id': chat_id,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'is_active': True
            }
            result = supabase_client.insert('users', data)
            if result:
                return User.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"Ошибка создания пользователя {telegram_id}: {e}")
            return None

    def update_user(self, telegram_id: int, username: str, first_name: str, last_name: str = None, language_code: str = 'ru', chat_id: Optional[int] = None) -> Optional[User]:
        try:
            data = {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'language_code': language_code,
                'chat_id': chat_id,
                'updated_at': datetime.utcnow().isoformat()
            }
            result = supabase_client.update('users', {'telegram_id': telegram_id}, data)
            if result:
                return User.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"Ошибка обновления пользователя {telegram_id}: {e}")
            return None

    def get_or_create_user(self, telegram_id: int, username: str, first_name: str, last_name: str = None, language_code: str = 'ru', chat_id: Optional[int] = None) -> Optional[User]:
        user = self.get_user_by_telegram_id(telegram_id)
        if user:
            return self.update_user(telegram_id, username, first_name, last_name, language_code, chat_id)
        else:
            return self.create_user(telegram_id, username, first_name, last_name, language_code, chat_id)


class UserSettingsCRUD:
    def get_settings(self, telegram_id: int) -> Optional[UserSettings]:
        try:
            result = supabase_client.select('user_settings', {'telegram_id': telegram_id})  # только 2 позиции
            if result and len(result) > 0:
                return UserSettings.from_dict(result[0])
            return None
        except Exception as e:
            logger.error(f"Ошибка получения настроек пользователя {telegram_id}: {e}")
            return None

    def create_default_settings(self, telegram_id: int) -> Optional[UserSettings]:
        try:
            data = {
                'telegram_id': telegram_id,
                'notification_enabled': True,
                'daily_reminder_time': "09:00",
                'language_level': "beginner",
                'target_language': "en",
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            result = supabase_client.insert('user_settings', data)
            if result:
                return UserSettings.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"Ошибка создания настроек пользователя {telegram_id}: {e}")
            return None

    def update_notification(self, telegram_id: int, enabled: bool) -> Optional[UserSettings]:
        settings = self.get_settings(telegram_id)
        if not settings:
            settings = self.create_default_settings(telegram_id)
            if not settings:
                return None
        try:
            data = {
                'notification_enabled': enabled,
                'updated_at': datetime.utcnow().isoformat()
            }
            result = supabase_client.update('user_settings', {'telegram_id': telegram_id}, data)
            if result:
                return UserSettings.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"Ошибка обновления уведомлений {telegram_id}: {e}")
            return None


user_crud = UserCRUD()
settings_crud = UserSettingsCRUD()