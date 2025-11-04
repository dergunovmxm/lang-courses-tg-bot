from .supabase_client import supabase_client
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserCRUD:
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        try:
            result = supabase_client.select('users', limit=1)
            for user in result:
                if user.get("telegram_id") == telegram_id:
                    return user
            return None
        except Exception as e:
            logger.error(f"Ошибка получения пользователя {telegram_id}: {e}")
            return None

    def create_user(self, telegram_id: int, username: str, first_name: str,
                    last_name: str = None, language_code: str = 'ru', chat_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        try:
            user_data = {
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
            result = supabase_client.insert('users', user_data)
            if result:
                logger.info(f"Создан новый пользователь {telegram_id}")
                return result
            return None
        except Exception as e:
            logger.error(f"Ошибка создания пользователя {telegram_id}: {e}")
            return None

    def update_user(self, telegram_id: int, username: str, first_name: str,
                    last_name: str = None, language_code: str = 'ru', chat_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        try:
            update_data = {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'language_code': language_code,
                'chat_id': chat_id,
                'updated_at': datetime.utcnow().isoformat()
            }
            result = supabase_client.update('users', {'telegram_id': telegram_id}, update_data)
            if result:
                return result
            return None
        except Exception as e:
            logger.error(f"Ошибка обновления пользователя {telegram_id}: {e}")
            return None

    def get_or_create_user(self, telegram_id: int, username: str, first_name: str,
                           last_name: str = None, language_code: str = 'ru', chat_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        user = self.get_user_by_telegram_id(telegram_id)
        if user:
            updated = self.update_user(telegram_id, username, first_name, last_name, language_code, chat_id)
            return updated or user
        else:
            return self.create_user(telegram_id, username, first_name, last_name, language_code, chat_id)

class UserSettingsCRUD:
    def get_settings(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        try:
            result = supabase_client.select('user_settings', limit=1)
            for s in result:
                if s.get("telegram_id") == telegram_id:
                    return s
            return None
        except Exception as e:
            logger.error(f"Ошибка получения настроек пользователя {telegram_id}: {e}")
            return None

    def create_default_settings(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        try:
            settings_data = {
                'telegram_id': telegram_id,
                'notification_enabled': True,
                'daily_reminder_time': "09:00",
                'language_level': "beginner",
                'target_language': "en",
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            result = supabase_client.insert('user_settings', settings_data)
            return result
        except Exception as e:
            logger.error(f"Ошибка создания настроек пользователя {telegram_id}: {e}")
            return None

    def update_notification_settings(self, telegram_id: int, enabled: bool) -> Optional[Dict[str, Any]]:
        try:
            settings = self.get_settings(telegram_id)
            if not settings:
                settings = self.create_default_settings(telegram_id)
                if not settings:
                    return None

            update_data = {
                'notification_enabled': enabled,
                'updated_at': datetime.utcnow().isoformat()
            }
            result = supabase_client.update('user_settings', {'telegram_id': telegram_id}, update_data)
            return result
        except Exception as e:
            logger.error(f"Ошибка обновления настроек уведомлений {telegram_id}: {e}")
            return None

user_crud = UserCRUD()
settings_crud = UserSettingsCRUD()